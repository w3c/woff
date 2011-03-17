import os
import shutil
import glob
import struct
import sstruct
from fontTools.ttLib.sfnt import sfntDirectoryEntrySize
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

groupDefinitions = [
    # identifier, title, spec section
    ("validsfnt", "Valid SFNTs", None),
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

def writeTest(identifier, title, description, data, specLink=None, credits=[], shouldConvert=False, flavor="cff"):
    print "Compiling %s..." % identifier
    assert identifier not in registeredIdentifiers, "Duplicate identifier! %s" % identifier
    registeredIdentifiers.add(identifier)

    if specLink is None:
        specLink = specificationURL
    else:
        specLink = specificationURL + specLink

    # generate the SFNT
    sfntPath = os.path.join(authoringToolTestDirectory, identifier)
    if flavor == "cff":
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
    header, directory, tableData = defaultSFNTTestData(flavor="ttf")
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
    flavor="ttf"
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
    description="Two table blocks overlap. This will cause checksums to be incorrect.",
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

# ------------------
# Generate the Index
# ------------------

print "Compiling index..."

testGroups = []

for tag, title, url in groupDefinitions:
    group = dict(title=title, url=url, testCases=testRegistry[tag])
    testGroups.append(group)

generateAuthoringToolIndexHTML(directory=authoringToolTestDirectory, testCases=testGroups)

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
