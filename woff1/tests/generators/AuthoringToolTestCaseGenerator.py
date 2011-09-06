"""
This script generates the authoring tool test cases. It will create a directory
one level up from the directory containing this script called "AuthoringTool".
That directory will have the structure:

    /Format
        README.txt - information about how the tests were generated and how they should be modified
        /Tests
            testcaseindex.xht - index of all test cases
            test-case-name-number.otf/ttf - individual SFNT test case
            /resources
                index.css - index CSS file

Within this script, each test case is generated with a call to the
writeTest function. In this, SFNT data must be passed along with
details about the data. This function will generate the SFNT
and register the case in the suite index.
"""

import os
import shutil
import glob
import struct
import sstruct
from fontTools.ttLib.sfnt import sfntDirectorySize, sfntDirectoryEntrySize
from testCaseGeneratorLib.defaultData import defaultSFNTTestData
from testCaseGeneratorLib.sfnt import packSFNT
from testCaseGeneratorLib.paths import resourcesDirectory, authoringToolDirectory, authoringToolTestDirectory, authoringToolResourcesDirectory
from testCaseGeneratorLib.html import generateAuthoringToolIndexHTML
from testCaseGeneratorLib.utilities import padData, calcPaddingLength, calcTableChecksum

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

indexNote = """
The tests in this suite represent SFNT data to be used for WOFF
conversion without any alteration or correction. An authoring tool
may allow the explicit or silent modification and/or correction of
SFNT data. In such a case, the tests in this suite that are labeled
as "should not convert" may be converted, so long as the problems
in the files have been corrected. In that case, there is no longer
any access to the "input font" as defined in the WOFF specification,
so the bitwise identical tests should be skipped.
""".strip()

validNote = """
These files are valid SFNTs that should be converted to WOFF.
""".strip()

invalidSFNTNote = """
These files are invalid SFNTs that should not be converted to WOFF.
""".strip()

tableDataNote = """
These files are valid SFNTs that excercise conversion of the table data.
""".strip()

tableDirectoryNote = """
These files are valid SFNTs that excercise conversion of the table directory.
""".strip()

bitwiseNote = """
These files are provided as test cases for checking that the
result of converting to WOFF and back to SFNT results in a file
that is bitwise identical to the original SFNT.
""".strip()

groupDefinitions = [
    # identifier, title, spec section, category note
    ("validsfnt", "Valid SFNTs", None, validNote),
    ("invalidsfnt", "Invalid SFNT Tests", specificationURL+"#conform-incorrect-reject", invalidSFNTNote),
    ("tabledata", "SFNT Table Data Tests", specificationURL+"#DataTables", tableDataNote),
    ("tabledirectory", "SFNT Table Directory Tests", specificationURL+"#DataTables", tableDirectoryNote),
    ("bitwiseidentical", "SFNT Bitwise Identical Tests", specificationURL+"#conform-identical", bitwiseNote),
]

testRegistry = {}
for group in groupDefinitions:
    tag = group[0]
    testRegistry[tag] = []

# -----------------
# Test Case Writing
# -----------------

registeredIdentifiers = set()
registeredTitles = set()
registeredDescriptions = set()

def writeTest(identifier, title, description, data, specLink=None, credits=[], shouldConvert=False, flavor="CFF"):
    """
    This function generates all of the files needed by a test case and
    registers the case with the suite. The arguments:

    identifier: The identifier for the test case. The identifier must be
    a - separated sequence of group name (from the groupDefinitions
    listed above), test case description (arbitrary length) and a number
    to make the name unique. The number should be zero padded to a length
    of three characters (ie "001" instead of "1").

    title: A thorough, but not too long, title for the test case.

    description: A detailed statement about what the test case is proving.

    data: The complete binary data for the SFNT.

    specLink: The anchor in the WOFF spec that the test case is testing.

    credits: A list of dictionaries defining the credits for the test case. The
    dictionaries must have this form:

        title="Name of the autor or reviewer",
        role="author or reviewer",
        link="mailto:email or http://contactpage"

    shouldConvert: A boolean indicating if the SFNT is valid enough for
    conversion to WOFF.

    flavor: The flavor of the WOFF data. The options are CFF or TTF.
    """
    print "Compiling %s..." % identifier
    assert identifier not in registeredIdentifiers, "Duplicate identifier! %s" % identifier
    assert title not in registeredTitles, "Duplicate title! %s" % title
    assert description not in registeredDescriptions, "Duplicate description! %s" % description
    registeredIdentifiers.add(identifier)
    registeredTitles.add(title)
    registeredDescriptions.add(description)

    if specLink is None:
        specLink = specificationURL
    else:
        specLink = specificationURL + specLink

    # generate the SFNT
    sfntPath = os.path.join(authoringToolTestDirectory, identifier)
    if flavor == "CFF":
        sfntPath += ".otf"
    else:
        sfntPath += ".ttf"
    f = open(sfntPath, "wb")
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

# ---------------
# Valid SFNT Data
# ---------------

# CFF

def makeValidSFNT1():
    header, directory, tableData = defaultSFNTTestData()
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="validsfnt-001",
    title="Valid CFF SFNT",
    description="The CFF flavored SFNT data is valid.",
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-checksumvalidate",
    data=makeValidSFNT1()
)

# TTF

def makeValidSFNT2():
    header, directory, tableData = defaultSFNTTestData(flavor="TTF")
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="validsfnt-002",
    title="Valid TTF SFNT",
    description="The TTF flavored SFNT data is valid.",
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-checksumvalidate",
    data=makeValidSFNT2(),
    flavor="TTF"
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

def makeInvalidPadding1():
    header, directory, tableData = defaultSFNTTestData()
    # grab the head table, calculate the padding length
    # and shift the following tables
    headEntry = [entry for entry in directory if entry["tag"] == "head"][0]
    shift = calcPaddingLength(headEntry["length"])
    assert shift
    entries = [(entry["offset"], entry) for entry in directory]
    assert sorted(entries)[0][1]["tag"] == "head"
    for o, entry in sorted(entries)[1:]:
        if entry["tag"] == "head":
            continue
        entry["offset"] -= shift
    # pad the tables
    for tag, data in tableData.items():
        if tag == "head":
            continue
        tableData[tag] = padData(data)
    # compile
    data = packSFNT(header, directory, tableData, applyPadding=False)
    return data

writeTest(
    identifier="invalidsfnt-padding-001",
    title="Table Data Missing Padding",
    description="There is no padding between two tables. The head check sum adjustment is also incorrect as a result.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidPadding1()
)

# final table is not padded

def makeInvalidPadding2():
    header, directory, tableData = defaultSFNTTestData()
    # pad the tables and update their offsets
    entries = [(entry["offset"], entry) for entry in directory]
    for o, entry in sorted(entries):
        tag = entry["tag"]
        data = tableData[tag]
        tableData[tag] = padData(data)
        entry["offset"] += sfntDirectoryEntrySize
    # make a bogus table and insert it
    header["numTables"] += 1
    data = "\01" * 15
    tableData["zzzz"] = data
    offset = entry["offset"] + entry["length"] + calcPaddingLength(entry["length"])
    directory.append(
        dict(
            tag="zzzz",
            offset=offset,
            length=15,
            checksum=calcTableChecksum("zzzz", data)
        )
    )
    # compile
    data = packSFNT(header, directory, tableData, applyPadding=False)
    return data

writeTest(
    identifier="invalidsfnt-padding-002",
    title="Final Table in Table Data Is Not Padded",
    description="There is no padding after the final table.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidPadding2()
)

# padding that exceeds three bytes

def makeInvalidPadding3():
    header, directory, tableData = defaultSFNTTestData()
    # shift the offsets for every table after head
    entries = [(entry["offset"], entry) for entry in directory]
    assert sorted(entries)[0][1]["tag"] == "head"
    for o, entry in sorted(entries)[1:]:
        if entry["tag"] == "head":
            continue
        entry["offset"] += 4
    # pad the tables
    for tag, data in tableData.items():
        if tag == "head":
            tableData[tag] = padData(data) + ("\0" * 4)
        else:
            tableData[tag] = padData(data)
    # compile
    data = packSFNT(header, directory, tableData, applyPadding=False)
    return data

writeTest(
    identifier="invalidsfnt-padding-003",
    title="Unnecessary Padding Between Tables",
    description="There are four extra bytes after the head table. The head check sum adjustment is also incorrect as a result.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidPadding3()
)

# unnecessary padding after final table

def makeInvalidPadding4():
    header, directory, tableData = defaultSFNTTestData()
    entries = [(entry["offset"], entry) for entry in directory]
    # pad the tables
    for o, entry in sorted(entries):
        tag = entry["tag"]
        data = tableData[tag]
        tableData[tag] = padData(data)
    # add four bogus bytes to the last table
    entry = sorted(entries)[-1][1]
    tag = entry["tag"]
    tableData[tag] += "\0" * 4
    # compile
    data = packSFNT(header, directory, tableData, applyPadding=False)
    return data

writeTest(
    identifier="invalidsfnt-padding-004",
    title="Unnecessary Padding After Final Table",
    description="There are four extra bytes after the final table. The head check sum adjustment is also incorrect as a result.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidPadding4()
)

# padding that is not null

def makeInvalidPadding5():
    header, directory, tableData = defaultSFNTTestData()
    # pad the tables
    for tag, data in tableData.items():
        if tag == "head":
            assert calcPaddingLength(len(data))
            tableData[tag] = data + ("\x01" * calcPaddingLength(len(data)))
        else:
            tableData[tag] = padData(data)
    # compile
    data = packSFNT(header, directory, tableData, applyPadding=False)
    return data

writeTest(
    identifier="invalidsfnt-padding-005",
    title="Invalid Padding Bytes in Table Data",
    description="There is padding after the head table that is not null.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidPadding5()
)

# two table data blocks overlap

def makeInvalidBlocks1():
    header, directory, tableData = defaultSFNTTestData()
    # slice four bytes off of the head table
    tableData["head"] = tableData["head"][:-4]
    # move the other tables up by four bytes
    entries = [(entry["offset"], entry) for entry in directory]
    assert sorted(entries)[0][1]["tag"] == "head"
    for o, entry in sorted(entries[1:]):
        entry["offset"] -= 4
    # compile
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="invalidsfnt-blocks-001",
    title="Table Data Blocks Overlap",
    description="Two table blocks overlap.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidBlocks1()
)

# offset to table is before start of the data block

def makeInvalidBlocks2():
    header, directory, tableData = defaultSFNTTestData()
    # shift each table up four bytes
    for entry in directory:
        entry["offset"] -= 4
    # compile
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="invalidsfnt-blocks-002",
    title="Table Data Block Begins Before End Of Directory",
    description="The first table has an offset that is before the end of the table directory.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidBlocks2()
)

# offset + length of table goes beyond the end of the file

def makeInvalidBlocks3():
    header, directory, tableData = defaultSFNTTestData()
    # extend the length of the final table by four bytes
    entries = [(entry["offset"], entry) for entry in directory]
    entry = sorted(entries)[-1][1]
    entry["length"] += 4
    # compile
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="invalidsfnt-blocks-003",
    title="Table Data Block Offset + Length Extends Past End of File",
    description="The final table has an offset + length that is four bytes past the end of the file.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidBlocks3()
)

# table directory not in ascending order

def makeInvalidDirectoryOrder1():
    header, directory, tableData = defaultSFNTTestData()
    # reverse the entries
    entries = [(entry["tag"], entry) for entry in directory]
    directory = [entry for tag, entry in reversed(sorted(entries))]
    # compile
    data = packSFNT(header, directory, tableData, sortDirectory=False)
    return data

writeTest(
    identifier="invalidsfnt-directory-order-001",
    title="Table Directory Not In Ascending Order",
    description="The table directory is in descending order.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidDirectoryOrder1()
)

# incorrect searchRange

def makeInvalidSearchRange1():
    header, directory, tableData = defaultSFNTTestData()
    # compile
    data = packSFNT(header, directory, tableData, searchRange=0)
    return data

writeTest(
    identifier="invalidsfnt-searchrange-001",
    title="Invalid searchRange",
    description="The searchRange is set to 0.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidSearchRange1()
)

# incorrect entrySelector

def makeInvalidEntrySelector1():
    header, directory, tableData = defaultSFNTTestData()
    # compile
    data = packSFNT(header, directory, tableData, entrySelector=0)
    return data

writeTest(
    identifier="invalidsfnt-entryselector-001",
    title="Invalid entrySelector",
    description="The entrySelector is set to 0.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidEntrySelector1()
)

# incorrect rangeShift

def makeInvalidRangeShift1():
    header, directory, tableData = defaultSFNTTestData()
    # compile
    data = packSFNT(header, directory, tableData, rangeShift=0)
    return data

writeTest(
    identifier="invalidsfnt-rangeshift-001",
    title="Invalid rangeShift",
    description="The rangeShift is set to 0.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-incorrect-reject",
    data=makeInvalidRangeShift1()
)

# -----------
# Compression
# -----------

def makeMustNotCompress1():
    header, directory, tableData = defaultSFNTTestData()
    # adjust the header
    header["numTables"] += 1
    # store the data
    data = "\0"
    tableData["TEST"] = data
    # offset the directory entries
    for entry in directory:
        entry["offset"] += sfntDirectoryEntrySize
    # find the offset
    entries = [(entry["offset"], entry) for entry in directory]
    entry = sorted(entries)[-1][1]
    offset = entry["offset"] + entry["length"]
    offset += calcPaddingLength(offset)
    # make the entry
    directory.append(
        dict(
            tag="TEST",
            offset=offset,
            length=1,
            checksum=calcTableChecksum("TEST", data)
        )
    )
    # compile
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="tabledata-compression-size-001",
    title="The \"TEST\" Table Must Not Be Compressed",
    description="The \"TEST\" table will be larger when compressed so it must not be compressed.",
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-compressedlarger",
    data=makeMustNotCompress1()
)

# ----------------------------
# Directory In Ascending Order
# ----------------------------

dummyTables = """1AAA
2AAA
A1AA
A2AA
AA1A
AA2A
AAA1
AAA2
AAAA
AAAB
AABA
ABAA
BAAA
8ZZZ
9ZZZ
Z8ZZ
Z9ZZ
ZZ8Z
ZZ9Z
ZZZ8
ZZZ9
YZZZ
ZYZZ
ZZYZ
ZZZY
ZZZZ
1aaa
2aaa
a1aa
a2aa
aa1a
aa2a
aaa1
aaa2
aaaa
aaab
aaba
abaa
baaa
8zzz
9zzz
z8zz
z9zz
zz8z
zz9z
zzz8
zzz9
yzzz
zyzz
zzyz
zzzy
zzzz""".splitlines()

def makeTableDirectoryAscending1():
    header, directory, tableData = defaultSFNTTestData()
    # adjust the header
    header["numTables"] += len(dummyTables)
    # adjust the offsets
    shift = len(dummyTables) * sfntDirectoryEntrySize
    for entry in directory:
        entry["offset"] += shift
    # store the data
    sorter = [(entry["offset"], entry["length"]) for entry in directory]
    offset, length = max(sorter)
    offset = offset + length
    data = "\0" * 4
    checksum = calcTableChecksum(None, data)
    for tag in dummyTables:
        tableData[tag] = data
        entry = dict(
            tag=tag,
            offset=offset,
            length=4,
            checksum=checksum
        )
        directory.append(entry)
        offset += 4
    # compile
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="tabledirectory-ascending-001",
    title="The Table Directory Must Be In Ascending Order",
    description="The SFNT contains %s tables in addition to the standard tables. The result of conversion to WOFF should be checked to ensure that the directory is in ascending order." % ", ".join(dummyTables),
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-ascending",
    data=makeTableDirectoryAscending1()
)


# ---------------------------
# Byte For Byte Compatibility
# ---------------------------

# valid CFF

writeTest(
    identifier="bitwiseidentical-001",
    title="SFNT With Common CFF Structure",
    description="The SFNT has a common CFF structure. The process of converting to WOFF and back to SFNT should result in a file that is bitwise identical.",
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-identical",
    data=makeValidSFNT1()
)

# valid TTF

writeTest(
    identifier="bitwiseidentical-002",
    title="SFNT With Common TTF Structure",
    description="The SFNT has a common TTF structure. The process of converting to WOFF and back to SFNT should result in a file that is bitwise identical.",
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-identical",
    data=makeValidSFNT2(),
    flavor="TTF"
)

# add bogus DSIG

def makeBitwiseIdenticalDSIG1():
    header, directory, tableData = defaultSFNTTestData()
    # adjust the header
    header["numTables"] += 1
    # store the data
    data = "\0" * 4
    tableData["DSIG"] = data
    # offset the directory entries
    for entry in directory:
        entry["offset"] += sfntDirectoryEntrySize
    # find the offset
    entries = [(entry["offset"], entry) for entry in directory]
    entry = max(entries)[1]
    offset = entry["offset"] + entry["length"]
    offset += calcPaddingLength(offset)
    # make the entry
    directory.append(
        dict(
            tag="DSIG",
            offset=offset,
            length=4,
            checksum=calcTableChecksum("DSIG", data)
        )
    )
    # compile
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="bitwiseidentical-003",
    title="SFNT With Uncommon Table",
    description="The SFNT has a DSIG table. (Note: this is not a valid DSIG. It should not be used for testing anything other than the presence of the table after the conversion process.) The process of converting to WOFF and back to SFNT should result in a file that is bitwise identical.",
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-identical",
    data=makeBitwiseIdenticalDSIG1()
)

# add non-standard table

def makeBitwiseIdenticalNonStandardTable1():
    header, directory, tableData = defaultSFNTTestData()
    # adjust the header
    header["numTables"] += 1
    # store the data
    data = "\0" * 4
    tableData["TEST"] = data
    # offset the directory entries
    for entry in directory:
        entry["offset"] += sfntDirectoryEntrySize
    # find the offset
    entries = [(entry["offset"], entry) for entry in directory]
    entry = max(entries)[1]
    offset = entry["offset"] + entry["length"]
    offset += calcPaddingLength(offset)
    # make the entry
    directory.append(
        dict(
            tag="TEST",
            offset=offset,
            length=4,
            checksum=calcTableChecksum("TEST", data)
        )
    )
    # compile
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="bitwiseidentical-004",
    title="SFNT With Non-Standard Table",
    description="The SFNT has a TEST table. The process of converting to WOFF and back to SFNT should result in a file that is bitwise identical.",
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-identical",
    data=makeBitwiseIdenticalNonStandardTable1()
)

# unusual order in CFF

def makeBitwiseIdenticalNotRecommendedTableOrder1():
    header, directory, tableData = defaultSFNTTestData(flavor="TTF")
    # make the new order
    newOrder = "CFF ,maxp,hhea,name,post,cmap,OS/2,head".split(",")
    newOrder = [tag for tag in newOrder if tag in tableData]
    for tag in sorted(tableData.keys()):
        if tag not in newOrder:
            newOrder.append(tag)
    # reset the offsets
    directoryDict = {}
    for entry in directory:
        directoryDict[entry["tag"]] = entry
    assert set(newOrder) == set(directoryDict.keys())
    offset = sfntDirectorySize + (sfntDirectoryEntrySize * len(directory))
    for tag in newOrder:
        entry = directoryDict[tag]
        entry["offset"] = offset
        offset += entry["length"] + calcPaddingLength(entry["length"])
    directory = [entry for tag, entry in sorted(directoryDict.items())]
    # compile
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="bitwiseidentical-005",
    title="SFNT Without Recommended CFF Table Order",
    description="The SFNT has a table order that does not follow the recommended CFF table ordering as defined in the OpenType specification. The process of converting to WOFF and back to SFNT should result in a file that is bitwise identical.",
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-identical",
    data=makeBitwiseIdenticalNotRecommendedTableOrder1()
)

# unusual order in TTF

def makeBitwiseIdenticalNotRecommendedTableOrder2():
    header, directory, tableData = defaultSFNTTestData()
    # make the new order
    newOrder = "fpgm,LTSH,glyf,cmap,hhea,hmtx,PCLT,post,DSIG,maxp,loca,gasp,VDMX,kern,name,hdmx,prep,OS/2,cvt ,head".split(",")
    newOrder = [tag for tag in newOrder if tag in tableData]
    for tag in sorted(tableData.keys()):
        if tag not in newOrder:
            newOrder.append(tag)
    # reset the offsets
    directoryDict = {}
    for entry in directory:
        directoryDict[entry["tag"]] = entry
    assert set(newOrder) == set(directoryDict.keys())
    offset = sfntDirectorySize + (sfntDirectoryEntrySize * len(directory))
    for tag in newOrder:
        entry = directoryDict[tag]
        entry["offset"] = offset
        offset += entry["length"] + calcPaddingLength(entry["length"])
    directory = [entry for tag, entry in sorted(directoryDict.items())]
    # compile
    data = packSFNT(header, directory, tableData)
    return data

writeTest(
    identifier="bitwiseidentical-006",
    title="SFNT Without Recommended TTF Table Order",
    description="The SFNT has a table order that does not follow the recommended TTF table ordering as defined in the OpenType specification. The process of converting to WOFF and back to SFNT should result in a file that is bitwise identical.",
    shouldConvert=True,
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    specLink="#conform-identical",
    data=makeBitwiseIdenticalNotRecommendedTableOrder2(),
    flavor="TTF"
)

# ------------------
# Generate the Index
# ------------------

print "Compiling index..."

testGroups = []

for tag, title, url, note in groupDefinitions:
    group = dict(title=title, url=url, testCases=testRegistry[tag], note=note)
    testGroups.append(group)

generateAuthoringToolIndexHTML(directory=authoringToolTestDirectory, testCases=testGroups, note=indexNote)

# -----------------------
# Check for Unknown Files
# -----------------------

otfPattern = os.path.join(authoringToolTestDirectory, "*.otf")
ttfPattern = os.path.join(authoringToolTestDirectory, "*.ttf")
filesOnDisk = glob.glob(otfPattern) + glob.glob(ttfPattern)

for path in filesOnDisk:
    identifier = os.path.basename(path)
    identifier = identifier.split(".")[0]
    if identifier not in registeredIdentifiers:
        print "Unknown file:", path
