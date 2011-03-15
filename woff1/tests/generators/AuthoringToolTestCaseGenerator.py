import os
import shutil
import glob
import struct
import sstruct
from testCaseGeneratorLib.defaultData import defaultSFNTTestData
from testCaseGeneratorLib.sfnt import packSFNT
from testCaseGeneratorLib.paths import resourcesDirectory, authoringToolDirectory, authoringToolTestDirectory, authoringToolResourcesDirectory
from testCaseGeneratorLib.html import generateFormatIndexHTML

# ------------------------
# Specification URL
# This is used frequently.
# ------------------------

specificationURL = "http://dev.w3.org/webfonts/WOFF/spec/"

# ------------------
# Directory Creation
# (if needed)
# ------------------

if not os.path.exists(authoringToolDirectory):
    os.mkdir(authoringToolDirectory)
if not os.path.exists(authoringToolTestDirectory):
    os.mkdir(authoringToolTestDirectory)
if not os.path.exists(authoringToolResourcesDirectory):
    os.mkdir(authoringToolResourcesDirectory)

# -------------------
# Move HTML Resources
# -------------------

# index css
destPath = os.path.join(authoringToolResourcesDirectory, "index.css")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "index.css"), destPath)

# ---------------
# Test Case Index
# ---------------

# As the tests are generated a log will be kept.
# This log will be translated into an index after
# all of the tests have been written.

groupDefinitions = [
    # identifier, title, spec section
    ("valid", "Valid SFNTs", None),
    ("invalidsfnt", "Invalid SFNTs", specificationURL+"#conform-incorrect-reject"),
]

testRegistry = {}
for group in groupDefinitions:
    tag = group[0]
    testRegistry[tag] = []

# -----------------
# Test Case Writing
# -----------------

registeredIdentifiers = set()

def writeTest(identifier, title, description, data, specLink=None, credits=[], shouldConvert=False):
    print "Compiling %s..." % identifier
    assert identifier not in registeredIdentifiers, "Duplicate identifier! %s" % identifier
    registeredIdentifiers.add(identifier)

    if specLink is None:
        specLink = specificationURL
    else:
        specLink = specificationURL + specLink

    # generate the SFNT
    woffPath = os.path.join(authoringToolTestDirectory, identifier) + ".otf"
    f = open(woffPath, "wb")
    f.write(data)
    f.close()

    # register the test
    tag = identifier.split("-")[0]
    testRegistry[tag].append(
        dict(
            identifier=identifier,
            title=title,
            description=description,
            shouldConvert=shouldConvert,
            specLink=specLink
        )
    )

# -----------------
# Invalid SFNT Data
# -----------------

# invalid checksum for one table

def makeInvalidChecksum1():
    header, directory, tableData = defaultSFNTTestData()
    # change the OS/2 checksum
    for entry in directory:
        if entry["tag"] == "OS/2":
            entry["checksum"] = 0
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="invalidsfnt-checksum-001",
    title="Table Directory Contains Invalid CheckSum",
    description="The checksum for the OS/2 table is set to 0.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-checksumvalidate",
    data=makeInvalidChecksum1()
)

# invalid checksum adjustment in head table

def makeInvalidChecksum2():
    header, directory, tableData = defaultSFNTTestData()
    # grab the data
    data = tableData["head"]
    # gab the original value
    origValue = data[8:12]
    # pack a new value
    newValue = struct.pack(">L", 0)
    # make sure that this really is a new value
    assert origValue != newValue
    # store the new data
    newData = data[:8] + newValue + data[12:]
    tableData["head"] = newData
    # compile
    data = packSFNT(header, directory, tableData, calcCheckSum=False)
    return data

writeTest(
    identifier="invalidsfnt-checksum-002",
    title="Font head Table Incorrect CheckSum Adjustment",
    description="The head table checksum adjustment is set to 0.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-checksumvalidate",
    data=makeInvalidChecksum2()
)

# padding that does not result in a four byte boundary
# padding that exceeds three bytes
# padding that is not null
# final table is not padded
# data between properly padded tables
# two table data blocks overlap

## ------------------
## Generate the Index
## ------------------
#
#print "Compiling index..."
#
#testGroups = []
#
#for tag, title, url in groupDefinitions:
#    group = dict(title=title, url=url, testCases=testRegistry[tag])
#    testGroups.append(group)
#
#generateFormatIndexHTML(directory=authoringToolTestDirectory, testCases=testGroups)
#
## -----------------------
## Check for Unknown Files
## -----------------------
#
#woffPattern = os.path.join(authoringToolTestDirectory, "*.woff")
#filesOnDisk = glob.glob(woffPattern)
#
#for path in filesOnDisk:
#    identifier = os.path.basename(path)
#    identifier = identifier.split(".")[0]
#    if identifier not in registeredIdentifiers:
#        print "Unknown file:", path
