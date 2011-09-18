import sys
import os
from xml.etree import ElementTree as ET
from validator import validateFont

# ---------------------
# Locate the test Suite
# ---------------------

testSuiteDirectory = os.path.dirname(__file__)           # /validator
testSuiteDirectory = os.path.dirname(testSuiteDirectory) # /tools
testSuiteDirectory = os.path.dirname(testSuiteDirectory) # /WOFF
testSuiteDirectory = os.path.join(testSuiteDirectory, "tests", "Format", "Tests", "xhtml1")
if not os.path.exists(testSuiteDirectory):
    print "Test suite could not be located!"
    print "Aborting."
    sys.exit()

testSuiteIndexPath = os.path.join(testSuiteDirectory, "testcaseindex.xht")
testSuiteExpectationPath = os.path.join(os.path.dirname(__file__), "test_validatorExpectations.txt")

harnessReportPath = os.path.join(os.path.dirname(__file__), "testsuiteresults.txt")

# -------------
# Main Function
# -------------

def testValidator():
    # load the expected results
    expectedResults = {}
    for testCase in loadTestCasesFromText():
        assert testCase.identifier not in expectedResults
        expectedResults[testCase.identifier] = testCase
    # makes sure that the test suite and
    # the expected results are in sync
    checkExpectedResultSync(expectedResults)
    # test each case
    harnessResults = []
    errors = 0
    for identifier, testCase in sorted(expectedResults.items()):
        failed = not performTest(testCase)
        errors += failed
        if failed:
            s = "%s\tfail\t" % identifier
        else:
            s = "%s\tpass\t" % identifier
        harnessResults.append(s)
    # write the test suite harness fail
    harnessResults = "\n".join(harnessResults)
    if os.path.exists(harnessReportPath):
        os.remove(harnessReportPath)
    f = open(harnessReportPath, "wb")
    f.write(harnessResults)
    f.close()
    print "=" * 70
    print "%d errors found in %d tests." % (errors, len(expectedResults))
    print

def checkExpectedResultSync(expectedResults):
    suiteCases = {}
    for testCase in loadTestCasesFromIndexXHTML():
        assert testCase.identifier not in suiteCases
        suiteCases[testCase.identifier] = testCase
    inSync = True
    while inSync:
        # identifier sync
        inSuiteOnly = set(suiteCases.keys()) - set(expectedResults.keys())
        inExpectedOnly = set(expectedResults.keys()) - set(suiteCases.keys())
        if inSuiteOnly or inExpectedOnly:
            if inSuiteOnly:
                print "Test cases not in the expected results:"
                for i in sorted(inSuiteOnly):
                    print "\t" + i
            if inExpectedOnly:
                print "Test cases not in the test suite:"
                for i in sorted(inExpectedOnly):
                    print "\t" + i
            inSync = False
        # content sync
        for identifier in sorted(expectedResults.keys()):
            expected = expectedResults[identifier]
            suite = suiteCases[identifier]
            attributes = [
                "title",
                "description",
                "valid"
            ]
            for attribute in attributes:
                e = getattr(expected, attribute)
                s = getattr(suite, attribute)
                if e != s:
                    print "%s: %s is not the same in the suite and the expected result." % (identifier, attribute)
                    inSync = False
        break
    if not inSync:
        print "Test suite and the expected results text file are not in sync."
        print "Aborting."
        sys.exit()

class _ValidatorOptions(object):
    outputFormat = "text"

def performTest(testCase):
    # establish the options
    validatorOptions = _ValidatorOptions()
    validatorOptions.testGroups = []
    # validate
    woffPath = os.path.join(testSuiteDirectory, testCase.identifier + ".woff")
    report = validateFont(woffPath, validatorOptions, writeFile=False)[1]
    # skim the report
    assert "TRACEBACK" not in report
    filteredReport = [line for line in report.splitlines() if line.startswith("ERROR")]
    filteredReport = list(sorted(filteredReport))
    # compare the validator result with the expected result
    passedValidation = True
    for line in filteredReport:
        if line.startswith("ERROR"):
            passedValidation = False
            break
    if passedValidation != testCase.valid:
        print "%s Failed - Expected validity to be %s, but the result was %s." % (testCase.identifier, testCase.valid, passedValidation)
        if not passedValidation:
            for line in report.splitlines():
                print "\t" + line
            print
        return False
    # compare reports as needed
    if not testCase.valid:
        # if there isn't a match, print and return that the test didn't pass
        compare = list(sorted(testCase.report))
        if filteredReport != compare:
            print "%s - Non-matching report:" % testCase.identifier
            for line in report.splitlines():
                if not line.startswith("ERROR"):
                    continue
                print "\t" + line
            print
            return False
    return True


# ----------------
# Test Case Object
# ----------------

class TestCase(object):

    def __init__(self):
        self.identifier = None
        self.title = None
        self.description = None
        self.valid = None
        self.report = []

    def _get_text(self):
        text = [
            "identifier: %s" % self.identifier,
            "title: %s" % self.title,
            "description: %s" % self.description,
            "valid: %s" % self.validity
        ]
        if self.report:
            text.append("report:")
            text += self.report
        return "\n".join(text)

    text = property(_get_text)

# ------------
# XHTML Parser
# ------------

def loadTestCasesFromIndexXHTML():
    # get the text
    f = open(testSuiteIndexPath, "rb")
    text = f.read()
    f.close()
    # namespace required by ElementTree
    namespace = "{http://www.w3.org/1999/xhtml}"
    # get the body
    html = ET.fromstring(text)
    body = html.find(namespace + "body")
    # parse and load
    testCases = []
    for div in body.findall(namespace + "div"):
        cls = div.attrib.get("class")
        if cls != "testCase":
            continue
        # get the identifier
        identifier = div.attrib["id"]
        assert identifier
        # get the subsections
        overview, details = div.findall(namespace + "div")
        # get the title and the description
        title = overview.find(namespace + "h3").find(namespace + "a").tail
        assert title.startswith(": ")
        title = title[2:]
        description = overview.find(namespace + "p").text
        # get the validity
        validitySpan = details.find(namespace + "p").find(namespace + "span")
        validityID = validitySpan.attrib["id"]
        assert validityID == identifier + "-" + "validity"
        validity = validitySpan.text
        assert validity in ("Yes", "No")
        # make an object
        testCase = TestCase()
        testCase.identifier = identifier
        testCase.title = title
        testCase.description = description
        testCase.valid = validity == "Yes"
        # store
        testCases.append(testCase)
    # done
    return testCases

# -----------
# Text Parser
# -----------

def loadTestCasesFromText():
    # get the text
    f = open(testSuiteExpectationPath, "rb")
    text = f.read()
    f.close()
    text = text.strip()
    # parse and load
    testCases = []
    for line in text.splitlines():
        # comment
        if line.startswith("#"):
            continue
        # blank line. start a new case.
        if not line:
            testCases.append(TestCase())
            continue
        testCase = testCases[-1]
        # standard attribute
        attributes = [
            "identifier",
            "title",
            "description",
            "valid"
        ]
        matchedLine = False
        for attribute in attributes:
            t = attribute + ": "
            if line.startswith(t):
                value = line[len(t):]
                assert not getattr(testCase, attribute)
                if attribute == "valid":
                    value = value == "True"
                setattr(testCase, attribute, value)
                matchedLine = True
                break
        if matchedLine:
            continue
        # report start
        if line.startswith("report:"):
            continue
        # report line
        testCase.report.append(line)
    # done
    return testCases

# --------------
# Test Case Sync
# --------------

def makeTestCaseExpectationsFile():
    """
    This is only needed when creating the
    test case result text file.
    """
    testCases = loadTestCasesFromIndexXHTML()
    text = []
    for testCase in testCases:
        t = testCase.text
        if not testCase.validity:
            t += "\nreport:"
        text.append(t)
    text = "\n\n".join(text)
    # write
    assert not os.path.exists(testSuiteExpectationPath)
    f = open(testSuiteExpectationPath, "wb")
    f.write(text)
    f.close()

# makeTestCaseExpectationsFile()

if __name__ == "__main__":
    testValidator()
