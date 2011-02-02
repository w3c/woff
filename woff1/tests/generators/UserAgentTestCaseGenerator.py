"""
This script generates the User Agent test cases.
Each test is set up in the following way:

# Create the WOFF data to test.
def woffDataGeneratingFunction():
    return data

# Register and write the test case.
writeFileStructureTest(
    identifier="group-description-###",
    title="Descriptive Title",
    assertion="Details about what makes the WOFF valid/invalid.",
    credits=[
        dict(
            title="name of individual or organization",
            role="author, reviewer, etc.",
            link="email or contact page"
            ),
            # More credits as needed
    ],
    shouldDisplaySFNT=True,
    data=woffDataGeneratingFunction()
)

These will generate a WOFF and the appropriate test case files for User Agents
following the CSS Test Format (http://wiki.csswg.org/test/css2.1/format).
"""

import os
import shutil
import glob
import zlib
import glob
from copy import deepcopy
import sstruct
from fontTools.ttLib.sfnt import sfntDirectoryEntrySize
from testCaseGeneratorLib.woff import packTestHeader, packTestDirectory, packTestTableData, packTestMetadata, packTestPrivateData,\
    woffHeaderSize, woffDirectoryEntrySize, woffDirectoryEntryFormat
from testCaseGeneratorLib.defaultData import defaultTestData, testDataWOFFMetadata, testDataWOFFPrivateData,\
    sfntCFFTableData, testCFFDataWOFFDirectory
from testCaseGeneratorLib.utilities import calcPaddingLength, padData, calcTableChecksum, stripMetadata
from testCaseGeneratorLib.html import generateSFNTDisplayTestHTML, generateSFNTDisplayRefHTML, generateSFNTDisplayIndexHTML
from testCaseGeneratorLib.paths import resourcesDirectory, userAgentDirectory, userAgentTestDirectory, userAgentTestResourcesDirectory, userAgentFontsToInstallDirectory

# ------------------------
# Specification URL
# This is used frequently.
# ------------------------

specificationURL = "http://dev.w3.org/webfonts/WOFF/spec/"

# ------------------
# Directory Creation
# (if needed)
# ------------------

if not os.path.exists(userAgentDirectory):
    os.mkdir(userAgentDirectory)

if not os.path.exists(userAgentTestDirectory):
    os.mkdir(userAgentTestDirectory)

if not os.path.exists(userAgentTestResourcesDirectory):
    os.mkdir(userAgentTestResourcesDirectory)

# ---------------------
# Move Fonts To Install
# ---------------------

if not os.path.exists(userAgentFontsToInstallDirectory):
    os.mkdir(userAgentFontsToInstallDirectory)

# CFF Reference
destPath = os.path.join(userAgentFontsToInstallDirectory, "SFNT-CFF-Reference.otf")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "SFNT-CFF-Reference.otf"), os.path.join(destPath))
# CFF Fallback
destPath = os.path.join(userAgentFontsToInstallDirectory, "SFNT-CFF-Fallback.otf")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "SFNT-CFF-Fallback.otf"), os.path.join(destPath))
# TTF Reference
destPath = os.path.join(userAgentFontsToInstallDirectory, "SFNT-TTF-Reference.ttf")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "SFNT-TTF-Reference.ttf"), os.path.join(destPath))
# TTF Fallback
destPath = os.path.join(userAgentFontsToInstallDirectory, "SFNT-TTF-Fallback.ttf")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "SFNT-TTF-Fallback.ttf"), os.path.join(destPath))

# -------------------
# Move HTML Resources
# -------------------

# index css
destPath = os.path.join(userAgentTestResourcesDirectory, "sfntindex.css")
print destPath
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "sfntindex.css"), os.path.join(destPath))


# ---------------
# Test Case Index
# ---------------

# As the tests are generated a log will be kept.
# This log will be translated into an index after
# all of the tests have been written.

groupDefinitions = [
    # identifier, title, spec section
    ("valid", "Valid WOFFs", None),
    ("header", "WOFF Header Tests", specificationURL+"#WOFFHeader"),
    ("blocks", "WOFF Data Block Tests", specificationURL+"#OverallStructure"),
    ("directory", "WOFF Table Directory Tests", specificationURL+"#TableDirectory"),
    ("tabledata", "WOFF Table Data Tests", specificationURL+"#DataTables"),
    ("metadata", "WOFF Metadata Tests", specificationURL+"#Metadata"),
    ("privatedata", "WOFF Private Data Tests", specificationURL+"#Private"),
    ("metadatadisplay", "WOFF Metadata Display Tests", specificationURL+"#Metadata")
]

testRegistry = {}
for group in groupDefinitions:
    tag = group[0]
    testRegistry[tag] = []

# ---------------
# File Generators
# ---------------

registeredIdentifiers = set()

def writeFileStructureTest(identifier, flavor="CFF",
        title=None, assertion=None,
        sfntDisplaySpecLink=None, metadataDisplaySpecLink=None,
        credits=[], flags=[],
        shouldDisplaySFNT=None, metadataIsValid=None,
        data=None, metadataToDisplay=None,
        extraSFNTNotes=[], extraMetadataNotes=[]
        ):
    print "Compiling %s..." % identifier
    assert identifier not in registeredIdentifiers, "Duplicate identifier! %s" % identifier
    registeredIdentifiers.add(identifier)

    if sfntDisplaySpecLink is None:
        sfntDisplaySpecLink = ""
    sfntDisplaySpecLink = specificationURL + sfntDisplaySpecLink
    flags = list(flags)
    flags += ["font"] # fonts must be installed for all of these tests

    # generate the WOFF
    woffPath = os.path.join(userAgentTestResourcesDirectory, identifier) + ".woff"
    f = open(woffPath, "wb")
    f.write(data)
    f.close()

    # generate the test and ref html
    kwargs = dict(
        fileName=identifier,
        directory=userAgentTestDirectory,
        flavor=flavor,
        title=title,
        sfntDisplaySpecLink=sfntDisplaySpecLink,
        metadataDisplaySpecLink=metadataDisplaySpecLink,
        assertion=assertion,
        credits=credits,
        flags=flags,
        shouldDisplay=shouldDisplaySFNT,
        metadataIsValid=metadataIsValid,
        metadataToDisplay=metadataToDisplay,
        extraSFNTNotes=extraSFNTNotes,
        extraMetadataNotes=extraMetadataNotes
    )
    generateSFNTDisplayTestHTML(**kwargs)
    generateSFNTDisplayRefHTML(**kwargs)

    # register the test
    tag = identifier.split("-")[0]
    testRegistry[tag].append(
        dict(
            identifier=identifier,
            flags=flags,
            title=title,
            assertion=assertion,
            sfntExpectation=shouldDisplaySFNT,
            sfntURL=sfntDisplaySpecLink,
            metadataURL=metadataDisplaySpecLink,
            metadataExpectation=metadataIsValid,
        )
    )

def writeMetadataSchemaValidityTest(identifier, title=None, assertion=None, credits=[], sfntDisplaySpecLink=None, metadataDisplaySpecLink=None, metadataIsValid=None, metadata=None):
    """
    This is a convenience functon that eliminates the need to make a complete
    WOFF when only the metadata is being tested.
    """
    assert metadata is not None
    assert metadataIsValid is not None
    metadata = metadata.strip()
    # convert to tabs
    metadata = metadata.replace("    ", "\t")
    # store
    originalMetadata = metadata
    # pack
    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    # pass to the more verbose function
    if metadataDisplaySpecLink is None:
        if not metadataIsValid:
            metadataDisplaySpecLink = "#conform-invalid-mustignore"
        else:
            metadataDisplaySpecLink = "#Metadata"
    if sfntDisplaySpecLink is None:
        sfntDisplaySpecLink = "#conform-metadata-noeffect"
    kwargs = dict(
        title=title,
        assertion=assertion,
        credits=credits,
        sfntDisplaySpecLink=sfntDisplaySpecLink,
        metadataDisplaySpecLink=metadataDisplaySpecLink,
        shouldDisplaySFNT=True,
        metadataIsValid=metadataIsValid,
        data=data
    )
    if metadataIsValid:
        kwargs["metadataToDisplay"] = originalMetadata
    writeFileStructureTest(
        identifier,
        **kwargs
    )

# -----------
# Valid Files
# -----------

# CFF

def makeValidWOFF1():
    header, directory, tableData = defaultTestData()
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="valid-001",
    title="Valid WOFF 1",
    assertion="Valid CFF flavored WOFF with no metadata and no private data",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    data=makeValidWOFF1()
)

def makeValidWOFF2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="valid-002",
    title="Valid WOFF 2",
    assertion="Valid CFF flavored WOFF with metadata",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    data=makeValidWOFF2(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

def makeValidWOFF3():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="valid-003",
    title="Valid WOFF 3",
    assertion="Valid CFF flavored WOFF with private data",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    data=makeValidWOFF3()
)

def makeValidWOFF4():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata, havePrivateData=True) + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="valid-004",
    title="Valid WOFF 4",
    assertion="Valid CFF flavored WOFF with metadata and private data",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    data=makeValidWOFF4(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

# TTF

def makeValidWOFF5():
    header, directory, tableData = defaultTestData(flavor="ttf")
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="valid-005",
    flavor="TTF",
    title="Valid WOFF 5",
    assertion="Valid TTF flavored WOFF with no metadata and no private data",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    data=makeValidWOFF5()
)

def makeValidWOFF6():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata, flavor="ttf")
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="valid-006",
    flavor="TTF",
    title="Valid WOFF 6",
    assertion="Valid TTF flavored WOFF with metadata",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    data=makeValidWOFF6(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

def makeValidWOFF7():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData, flavor="ttf")
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="valid-007",
    flavor="TTF",
    title="Valid WOFF 7",
    assertion="Valid TTF flavored WOFF with private data",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    data=makeValidWOFF7()
)

def makeValidWOFF8():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData, flavor="ttf")
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata, havePrivateData=True) + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="valid-008",
    flavor="TTF",
    title="Valid WOFF 8",
    assertion="Valid TTF flavored WOFF with metadata and private data",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    data=makeValidWOFF8(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

# ---------------------------------
# File Structure: Header: signature
# ---------------------------------

def makeHeaderInvalidSignature1():
    header, directory, tableData = defaultTestData()
    header["signature"] = "XXXX"
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="header-signature-001",
    title="Header Signature Invalid Value",
    assertion="The signature field contains XXXX instead of wOFF.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-nonmagicnumber-reject",
    data=makeHeaderInvalidSignature1()
)

# ------------------------------
# File Structure: Header: length
# ------------------------------

def makeHeaderInvalidLength1():
    header, directory, tableData = defaultTestData()
    header["length"] -= 4
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="header-length-001",
    title="Header Length Too Short",
    assertion="The length field contains a value that is four bytes shorter than the actual data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#WOFFHeader",
    data=makeHeaderInvalidLength1()
)

def makeHeaderInvalidLength2():
    header, directory, tableData = defaultTestData()
    header["length"] += 4
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="header-length-002",
    title="Header Length Too Long",
    assertion="The length field contains a value that is four bytes longer than the actual data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#WOFFHeader",
    data=makeHeaderInvalidLength2()
)

# ---------------------------------
# File Structure: Header: numTables
# ---------------------------------

def makeHeaderInvalidNumTables1():
    header, directory, tableData = defaultTestData()
    header["numTables"] = 0
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="header-numTables-001",
    title="Header Number of Tables Set to Zero",
    assertion="The header contains 0 in the numTables field. A table directory and table data are present.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#WOFFHeader",
    data=makeHeaderInvalidNumTables1()
)

# -------------------------------------
# File Structure: Header: totalSfntSize
# -------------------------------------

def makeHeaderInvalidTotalSfntSize1():
    header, directory, tableData = defaultTestData()
    # find a padding value that can be subtracted from the totalSfntSize.
    decreaseBy = None
    for entry in directory:
        paddingSize = calcPaddingLength(entry["origLength"])
        if paddingSize:
            decreaseBy = paddingSize
            break
    assert decreaseBy is not None
    header["totalSfntSize"] -= decreaseBy
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="header-totalSfntSize-001",
    title="Header Total SFNT Size Not a Multiple of 4",
    assertion="The totalSfntSize field contains a value that is missing padding bytes between two tables.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-totalsize-longword-reject",
    data=makeHeaderInvalidTotalSfntSize1()
)

def makeHeaderInvalidTotalSfntSize2():
    header, directory, tableData = defaultTestData()
    header["totalSfntSize"] += 4
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="header-totalSfntSize-002",
    title="Header Total SFNT Size Too Long",
    assertion="The totalSfntSize field contains a value that is is four bytes too long.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-totalsize-longword-reject",
    data=makeHeaderInvalidTotalSfntSize2()
)

def makeHeaderInvalidTotalSfntSize3():
    header, directory, tableData = defaultTestData()
    header["totalSfntSize"] -= 4
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="header-totalSfntSize-003",
    title="Header Total SFNT Size Too Short",
    assertion="The totalSfntSize field contains a value that is is four bytes too short.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-totalsize-longword-reject",
    data=makeHeaderInvalidTotalSfntSize3()
)

# --------------------------------
# File Structure: Header: reserved
# --------------------------------

def makeHeaderInvalidReserved1():
    header, directory, tableData = defaultTestData()
    header["reserved"] = 1
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="header-reserved-001",
    title="Header Reserved Invalid Value",
    assertion="The reserved field contains 1.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-reserved-reject",
    data=makeHeaderInvalidReserved1()
)

# --------------------------------------------
# File Structure: Data Blocks: Extraneous Data
# --------------------------------------------

# between table directory and table data

def makeExtraneousData1():
    header, directory, tableData = defaultTestData()
    bogusByteLength = 4
    bogusBytes = "\0" * bogusByteLength
    for entry in directory:
        entry["offset"] += bogusByteLength
    header["length"] += bogusByteLength
    data = packTestHeader(header) + packTestDirectory(directory) + bogusBytes + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="blocks-extraneous-data-001",
    title="Extraneous Data Between Directory and Table Data",
    assertion="There are four null bytes between the table directory and the table data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData1()
)

# between tables

def makeExtraneousData2():
    header, directory, tableData = defaultTestData()
    bogusByteLength = 4
    bogusBytes = "\0" * bogusByteLength
    inserted = False
    # do not apply to the last table
    for entry in directory[:-1]:
        tag = entry["tag"]
        origData, compData = tableData[tag]
        compData += bogusBytes
        header["length"] += bogusByteLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="blocks-extraneous-data-002",
    title="Extraneous Data Between Tables",
    assertion="There are four null bytes between each of the table data blocks.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData2()
)

# after table data with no metadata or private data

def makeExtraneousData3():
    header, directory, tableData = defaultTestData()
    bogusByteLength = 4
    bogusBytes = "\0" * bogusByteLength
    header["length"] += bogusByteLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + bogusBytes
    return data

writeFileStructureTest(
    identifier="blocks-extraneous-data-003",
    title="Extraneous Data After Table Data",
    assertion="There are four null bytes after the table data block and there is no metadata or private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData3()
)

# between tabledata and metadata

def makeExtraneousData4():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    bogusByteLength = 4
    bogusBytes = "\0" * bogusByteLength
    header["length"] += bogusByteLength
    header["metaOffset"] += bogusByteLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + bogusBytes + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="blocks-extraneous-data-004",
    title="Extraneous Data Between Table Data and Metadata",
    assertion="There are four null bytes between the table data and the metadata.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData4()
)

# between tabledata and private data

def makeExtraneousData5():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    bogusByteLength = 4
    bogusBytes = "\0" * bogusByteLength
    header["length"] += bogusByteLength
    header["privOffset"] += bogusByteLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + bogusBytes + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="blocks-extraneous-data-005",
    title="Extraneous Data Between Table Data and Private Data",
    assertion="There are four null bytes between the table data and the private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData5()
)

# between metadata and private data

def makeExtraneousData6():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    bogusByteLength = 4
    bogusBytes = "\0" * bogusByteLength
    header["length"] += bogusByteLength
    header["privOffset"] += bogusByteLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata, havePrivateData=True) + bogusBytes + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="blocks-extraneous-data-006",
    title="Extraneous Data Between Metdata and Private Data",
    assertion="There are four null bytes between the metadata and the private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData6()
)

# after metadata with no private data

def makeExtraneousData7():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    bogusByteLength = 4
    bogusBytes = "\0" * bogusByteLength
    header["length"] += bogusByteLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata) + bogusBytes
    return data

writeFileStructureTest(
    identifier="blocks-extraneous-data-007",
    title="Extraneous Data After Metadata",
    assertion="There are four null bytes after the metadata and there is no private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData7()
)

# after private data

def makeExtraneousData8():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    bogusByteLength = 4
    bogusBytes = "\0" * bogusByteLength
    header["length"] += bogusByteLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestPrivateData(privateData) + bogusBytes
    return data

writeFileStructureTest(
    identifier="blocks-extraneous-data-008",
    title="Extraneous Data After Private Data",
    assertion="There are four null bytes after the private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData8()
)

# -------------------------------------
# File Structure: Data Blocks: Overlaps
# -------------------------------------

# two tables overlap

def makeOverlappingData1():
    header, directory, tableData = defaultTestData()
    overlapLength = 4
    # slice some data off the first table's compressed data
    entry = directory[0]
    tag = entry["tag"]
    assert entry["compLength"] > overlapLength
    origData, compData = tableData[tag]
    tableData[tag] = (origData, compData[:-overlapLength])
    # shift the offsets for all the other tables
    for entry in directory[1:]:
        entry["offset"] -= overlapLength
    # adjust the header
    header["length"] -= overlapLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="blocks-overlap-001",
    title="Table Data Blocks Overlap",
    assertion="The second table's offset is four bytes before the end of the first table's data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData1()
)

# metadata overlaps the table data

def makeOverlappingData2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    overlapLength = 4
    header["metaOffset"] -= overlapLength
    header["length"] -= overlapLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)[:-overlapLength] + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="blocks-overlap-002",
    title="Metadata Overlaps Table Data",
    assertion="The metadata offset is four bytes before the end of the table data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData2()
)

# private data overlaps the table data

def makeOverlappingData3():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    overlapLength = 4
    header["privOffset"] -= overlapLength
    header["length"] -= overlapLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)[:-overlapLength] + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="blocks-overlap-003",
    title="Private Data Overlaps Table Data",
    assertion="The private data offset is four bytes before the end of the table data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData3()
)

# private data overlaps the metadata

def makeOverlappingData4():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    overlapLength = 4
    header["privOffset"] -= overlapLength
    header["length"] -= overlapLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata, havePrivateData=True)[:-overlapLength] + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="blocks-overlap-004",
    title="Private Data Overlaps Metadata",
    assertion="The private data offset is four bytes before the end of the metadata.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData4()
)

# ------------------------------------------------
# File Structure: Table Directory: 4-Byte Boundary
# ------------------------------------------------

# one table is not padded and, therefore, the next table does not begin on four byte boundary
# this test will trigger other failures. there doesn't seem to be a way around that.

def makeTableData4Byte1():
    header, directory, tableData = defaultTestData()
    data1 = "\x01" * 3
    data2 = "\x01" * 5
    # update the header
    header["length"] += 8 + (woffDirectoryEntrySize * 2)
    header["numTables"] += 2
    header["totalSfntSize"] += 8 + (sfntDirectoryEntrySize * 2)
    # update the directory
    offset = woffHeaderSize + (woffDirectoryEntrySize * header["numTables"])
    directoryAdditions = []
    for tag, data in [("AAAA", data1), ("AAAB", data2)]:
        entry = dict(
            tag=tag,
            offset=offset,
            compLength=len(data),
            origLength=len(data),
            origChecksum=calcTableChecksum(tag, data)
        )
        tableData[tag] = (data, data)
        directoryAdditions.append(entry)
        offset += len(data)
    shift = 8 + (woffDirectoryEntrySize * 2)
    for entry in directory:
        entry["offset"] += shift
    directory = directoryAdditions + directory
    # pack the table data
    packedTableData = []
    for entry in directory:
        tag = entry["tag"]
        origData, compData = tableData[tag]
        if tag not in ("AAAA", "AAAB"):
            compData = padData(compData)
        packedTableData.append(compData)
    packedTableData = "".join(packedTableData)
    data = packTestHeader(header) + packTestDirectory(directory) + packedTableData
    return data

writeFileStructureTest(
    identifier="directory-4-byte-001",
    title="Font Table Data Not On 4-Byte Boundary",
    assertion="Two vendor-space tables are inserted into the table directory and data: AAAA is three bytes long. AAAB is five bytes long. AAAA is not padded so that the AAAB table does not begin on a four-byte boundary. The tables that follow are all aligned correctly.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-tablesize-longword",
    data=makeTableData4Byte1()
)

# final table is not padded

def makeTableData4Byte2():
    # table data
    tableData = deepcopy(sfntCFFTableData)
    tag = "zzzz"
    data = "\0" * 2
    paddingLength = calcPaddingLength(len(data))
    tableData[tag] = (data, data)
    # directory
    directory = deepcopy(testCFFDataWOFFDirectory)
    entry = dict(
        tag=tag,
        origChecksum=0,
        origLength=0,
        compLength=0,
        offset=0
    )
    directory.append(entry)
    # update the structures
    header, directory, tableData = defaultTestData(directory=directory, tableData=tableData)
    header["length"] -= paddingLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    data = data[:-paddingLength]
    return data

writeFileStructureTest(
    identifier="directory-4-byte-002",
    title="Final Font Table Data Not Padded",
    assertion="The final table in the table data block is not padded to a 4-byte boundary.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-tablesize-longword",
    data=makeTableData4Byte2()
)

# -----------------------------------------
# File Structure: Table Directory: Overlaps
# -----------------------------------------

# offset after end of file

def makeTableDataByteRange1():
    header, directory, tableData = defaultTestData()
    directory[-1]["offset"] = header["length"] + 4
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="directory-overlaps-001",
    title="Font Table Data Offset Past End of File",
    assertion="The offset to the data block for the final table data is four bytes beyond the end of the file.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange1()
)

# offset + length goes past the end of the file

def makeTableDataByteRange2():
    header, directory, tableData = defaultTestData()
    directory[-1]["compLength"] += 4
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="directory-overlaps-002",
    title="Font Table Data Offset+Length Past End of File",
    assertion="The defined length for the final table causes the data block to be four bytes beyond the end of the file.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange2()
)

# overlaps metadata

def makeTableDataByteRange3():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    # grab the last table entry
    entry = directory[-1]
    entryLength = entry["compLength"] + calcPaddingLength(entry["compLength"])
    compData = tableData[entry["tag"]][1]
    # make the bogus offset
    entry["offset"] = header["metaOffset"] + 4
    # remove the length for the table from the total length
    header["length"] -= entryLength
    # pack the header and directory
    data = packTestHeader(header) + packTestDirectory(directory)
    # pad and combine all tables
    tableData = packTestTableData(directory, tableData)
    # slice the final table off of the table data
    tableData = tableData[:-entryLength]
    # pack the metadata
    metadata = packTestMetadata(metadata)
    assert len(metadata) > len(compData)
    # write the table data over the top of the metadata
    metadata = metadata[:4] + compData + metadata[4 + len(compData):]
    # combine everything
    data += tableData + metadata
    return data

writeFileStructureTest(
    identifier="directory-overlaps-003",
    title="Font Table Data Overlaps Metadata",
    assertion="The final table starts four bytes after the start of the metadata. This will fail for another reason: the calculated length (header length + directory length + entry lengths + metadata length) will not match the stored length in the header.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange3()
)

# overlaps private data

def makeTableDataByteRange4():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    # grab the last table entry
    entry = directory[-1]
    entryLength = entry["compLength"] + calcPaddingLength(entry["compLength"])
    compData = tableData[entry["tag"]][1]
    # make the bogus offset
    entry["offset"] = header["privOffset"] + 4
    # remove the length for the table from the total length
    header["length"] -= entryLength
    # pack the header and directory
    data = packTestHeader(header) + packTestDirectory(directory)
    # pad and combine all tables
    tableData = packTestTableData(directory, tableData)
    # slice the final table off of the table data
    tableData = tableData[:-entryLength]
    # pack the private data
    privateData = packTestPrivateData(privateData)
    assert len(privateData) > len(compData)
    # write the table data over the top of the private data
    privateData = privateData[:4] + compData + privateData[4 + len(compData):]
    # combine everything
    data += tableData + privateData
    return data

writeFileStructureTest(
    identifier="directory-overlaps-004",
    title="Font Table Data Overlaps Private Data",
    assertion="The final table starts four bytes after the start of the private data. This will fail for another reason: the calculated length (header length + directory length + entry lengths + private data length) will not match the stored length in the header.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange4()
)

# two tables overlap

def makeTableDataByteRange5():
    header, directory, tableData = defaultTestData()
    # grab the last table entry
    entry = directory[-1]
    entryLength = entry["compLength"] + calcPaddingLength(entry["compLength"])
    compData = tableData[entry["tag"]][1]
    # grab the second to last entry
    prevEntry = directory[-2]
    assert prevEntry["compLength"] > 4
    # make the bogus offset
    entry["offset"] -= 4
    # adjust the total length
    header["length"] = entry["offset"] + entryLength
    # pack the header, directory and table data
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    # slice off everything after the new offset
    data = data[:entry["offset"]]
    # add the table to the data
    data += compData + ("\0" * calcPaddingLength(len(compData)))
    # sanity check
    assert header["length"] == len(data)
    return data

writeFileStructureTest(
    identifier="directory-overlaps-005",
    title="Two Table Data Blocks Overlap",
    assertion="The final table starts four bytes before the end of the previous table. This will fail for another reason: the calculated length (header length + directory length + entry lengths) will not match the stored length in the header.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange5()
)

# -------------------------------------------
# File Structure: Table Directory: compLength
# -------------------------------------------

# some tables have a compressed length that is longer than the original length

def makeTableDataCompressionLength1():
    tableData = deepcopy(sfntCFFTableData)
    haveCompLargerThanOrig = False
    for tag, (origData, compData) in tableData.items():
        if len(compData) < len(origData):
            continue
        compData = zlib.compress(origData)
        if len(compData) > len(origData):
            haveCompLargerThanOrig = True
            tableData[tag] = (origData, compData)
    assert haveCompLargerThanOrig
    header, directory, tableData = defaultTestData(tableData=tableData)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="directory-compLength-001",
    title="Font Table Data Compressed Length Greater Than Original Length",
    assertion="At least one table's compLength is larger than the origLength.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-compressedlarger",
    data=makeTableDataCompressionLength1()
)

# -------------------------------------------
# File Structure: Table Directory: origLength
# -------------------------------------------

# one table has an origLength that is less than the decompressed length

def makeTableDataOriginalLength1():
    header, directory, tableData = defaultTestData()
    shift = 4
    cff = tableData["CFF "]
    cffEntry = [entry for entry in directory if entry["tag"] == "CFF "][0]
    assert cffEntry["compLength"] < cffEntry["origLength"]
    assert cffEntry["origLength"] - shift > entry["compLength"]
    cffEntry["origLength"] -= shift
    header["totalSfntSize"] -= shift
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="directory-origLength-001",
    title="Original Length Less Than Decompressed Length",
    assertion="The CFF table when decompressed has a length that is four bytes longer than the value listed in origLength.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-origLength",
    data=makeTableDataOriginalLength1()
)

# one table has an origLength that is greater than the decompressed length

def makeTableDataOriginalLength2():
    header, directory, tableData = defaultTestData()
    shift = 4
    cff = tableData["CFF "]
    cffEntry = [entry for entry in directory if entry["tag"] == "CFF "][0]
    assert cffEntry["compLength"] < cffEntry["origLength"]
    cffEntry["origLength"] += shift
    header["totalSfntSize"] += shift
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="directory-origLength-002",
    title="Original Length Greater Than Decompressed Length",
    assertion="The CFF table when decompressed has a length that is four bytes shorter than the value listed in origLength.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-origLength",
    data=makeTableDataOriginalLength2()
)

# ---------------------------------------
# File Structure: Table Data: Compression
# ---------------------------------------

# no tables compressed

def makeTableCompressionTest1():
    tableData = deepcopy(sfntCFFTableData)
    for tag, (origData, compData) in tableData.items():
        tableData[tag] = (origData, origData)
    header, directory, tableData = defaultTestData(tableData=tableData)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="tabledata-compression-001",
    title="Font Table Data Not Compressed",
    assertion="None of the tables are stored in compressed form.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-mustuncompress",
    data=makeTableCompressionTest1()
)

# all possible tables are compressed

def makeTableCompressionTest2():
    header, directory, tableData = defaultTestData()
    for tag, (origData, compData) in tableData.items():
        # this is a double check. the default data stores everything
        # possible in compressed form.
        if tag == "head":
            continue
        assert len(compData) <= len(origData)
        if len(compData) == len(origData):
            compTest = zlib.compress(origData)
            assert len(compTest) > len(origData)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="tabledata-compression-002",
    title="Font Table Data Is Compressed When Possible",
    assertion="All of the tables (excpet head) that will be smaller when compressed are stored in their compressed state.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-mustuncompress",
    data=makeTableCompressionTest2()
)

# not all possible tables are compressed

def makeTableCompressionTest3():
    tableData = deepcopy(sfntCFFTableData)
    haveStoredCompressed = True
    for tag, (origData, compData) in tableData.items():
        if haveStoredCompressed and len(compData) < len(origData):
            compData = origData
        elif len(compData) < len(origData):
            haveStoredCompressed = True
        tableData[tag] = (origData, compData)
    assert haveStoredCompressed
    header, directory, tableData = defaultTestData(tableData=tableData)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="tabledata-compression-003",
    title="Not All Font Table Data Is Compressed When Possible",
    assertion="Only one of the tables that would be smaller when compressed is stored in the compressed state.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-mustuncompress",
    data=makeTableCompressionTest3()
)

# varying compression levels

def makeTableCompressionTest4():
    tableData = deepcopy(sfntCFFTableData)
    compressionLevels = set()
    for index, (tag, (origData, compData)) in enumerate(tableData.items()):
        compData = origData
        r = range(1, 10)
        if index % 2:
            r = reversed(r)
        for level in r:
            c = zlib.compress(origData, level)
            if len(c) < len(origData):
                compData = c
                compressionLevels.add(level)
                break
        tableData[tag] = (origData, compData)
    assert len(compressionLevels) > 1
    header, directory, tableData = defaultTestData(tableData=tableData)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="tabledata-compression-004",
    title="Font Table Data Is Compressed At Different Levels",
    assertion="The font data tables are compressed using at least two different levels.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-mustuncompress",
    data=makeTableCompressionTest4()
)

# ----------------------------------------------
# File Structure: Table Data: Compression Format
# ----------------------------------------------

# compression incompatible with zlib

def makeTableZlibCompressionTest1():
    header, directory, tableData = defaultTestData()
    madeBogusTableData = False
    for tag, (origData, compData) in tableData.items():
        if len(origData) == len(compData):
            continue
        compData = "\x01" * len(compData)
        tableData[tag] = (origData, compData)
        madeBogusTableData = True
        break
    assert madeBogusTableData
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="tabledata-zlib-001",
    title="Font Table Data Invalid Compressed Data",
    assertion="One compressed table has had its compressed data replaced with \\01 making it incompatible with zlib.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-mustzlib",
    data=makeTableZlibCompressionTest1()
)

# -----------------------------------
# File Structure: Metadata: No Effect
# -----------------------------------

# have no metadata

def makeMetadataNoEffect1():
    header, directory, tableData = defaultTestData()
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="metadata-noeffect-001",
    title="No Metadata Present",
    assertion="The file has no metadata.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect",
    data=makeMetadataNoEffect1()
)

# have metadata

def makeMetadataNoEffect2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="metadata-noeffect-002",
    title="Metadata Present",
    assertion="The file has metadata.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect",
    metadataIsValid=True,
    metadataDisplaySpecLink="#conform-metadata-maydisplay",
    data=makeMetadataNoEffect2()
)

# ---------------------------------------
# File Structure: Private Data: No Effect
# ---------------------------------------

# have no private data

def makePrivateDataNoEffect1():
    header, directory, tableData = defaultTestData()
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="privatedata-noeffect-001",
    title="No Private Data Present",
    assertion="The file has no private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-private-noeffect",
    data=makePrivateDataNoEffect1()
)

# have private data

def makePrivateDataNoEffect2():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="privatedata-noeffect-002",
    title="Private Data Present",
    assertion="The file has private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-private-noeffect",
    data=makePrivateDataNoEffect2()
)

# -------------------------------
# Metadata Display: Authoritative
# -------------------------------

metadataAuthoritativeXML = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="PASS" />
    <description>
        <text>
            PASS
        </text>
    </description>
    <copyright>
        <text>
            PASS
        </text>
    </copyright>
    <trademark>
        <text>
            PASS
        </text>
    </trademark>
    <vendor name="PASS" url="PASS" />
    <credits>
        <credit name="PASS" url="PASS" />
    </credits>
    <license url="PASS">
        <text>
            PASS
        </text>
    </license>
</metadata>
""".strip().replace("    ", "\t")

def makeMetadataAuthoritativeTest1():
    from cStringIO import StringIO
    from fontTools.ttLib import TTFont
    from fontTools.ttLib.tables._n_a_m_e import NameRecord
    from testCaseGeneratorLib.paths import sfntCFFSourcePath
    from testCaseGeneratorLib.sfnt import getSFNTData
    from testCaseGeneratorLib.defaultData import sfntCFFTableOrder
    setToFAIL = [
        0,  # copyright
        3,  # unique id
        7,  # trademark
        8,  # manufacturer
        9,  # designer
        10, # description
        11, # vendor url
        12, # designer url
        13, # license
        14  # license url
    ]
    # open the SFNT
    font = TTFont(sfntCFFSourcePath)
    # overwrite parts of the name table that overlap the metadata
    nameTable = font["name"]
    newNames = []
    for record in nameTable.names:
        if record.nameID in setToFAIL:
            continue
        newNames.append(record)
    string = "FAIL".encode("utf8")
    for nameID in setToFAIL:
        for platformID, platEncID, langID in [(1, 0, 0), (3, 1, 1033)]:
            record = NameRecord()
            record.nameID = nameID
            record.platformID = platformID
            record.platEncID = platEncID
            record.langID = langID
            if record.platformID == 0 or (record.platformID == 3 and record.platEncID in (0, 1)):
                record.string = string.encode("utf_16_be")
            else:
                record.string = string.encode("latin1")
            newNames.append(record)
    newNames.sort()
    nameTable.names = newNames
    # save the SFNT
    f = StringIO()
    font.save(f, reorderTables=False)
    f.seek(0)
    # load the table data
    tableData, tableOrder, tableChecksums = getSFNTData(f)
    # make sure that the table order is the same as the original
    assert tableOrder == sfntCFFTableOrder
    # compile the WOFF
    header, directory, tableData, metadata = defaultTestData(tableData=tableData, metadata=metadataAuthoritativeXML)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="metadatadisplay-authoritative-001",
    title="Metadata Out of Sync With name Table",
    assertion="The name table and metadata fields are out of sync. The name table contains FAIL and the metadata contains PASS for unique id, vendor name, vendor url, credit name, credit url, description, license, license url, copyright and trademark.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    metadataToDisplay=metadataAuthoritativeXML,
    metadataDisplaySpecLink="#conform-metadata-authoritative",
    data=makeMetadataAuthoritativeTest1(),
    extraMetadataNotes=["The Extended Metadata Block test fails if the word FAIL appears in the metadata display."]
)

# -----------------------------
# Metadata Display: Compression
# -----------------------------

def makeMetadataCompression1():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    metadata = metadata[0], metadata[0]
    diff = header["metaOrigLength"] - header["metaLength"]
    header["length"] += diff
    header["metaLength"] = header["metaOrigLength"]
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="metadatadisplay-compression-001",
    title="Metadata Invalid Compression",
    assertion="The metadata is stored in an uncompressed state and therefore does not have the proper compression format.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    metadataIsValid=False,
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    data=makeMetadataCompression1(),
)

# --------------------------------
# Metadata Display: metaOrigLength
# --------------------------------

# <

def makeMetaOrigLengthTest1():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    metaOrigLength = header["metaOrigLength"]
    metaOrigLength += 1
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="metadatadisplay-metaOrigLength-001",
    title="Decompressed Metadata Length Less Than metaOrigLength",
    assertion="The metadata decompressed to a length that is 1 byte smaller than the length defined in metaOrigLength",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    metadataIsValid=False,
    sfntDisplaySpecLink="#conform-metaOrigLength",
    data=makeMetaOrigLengthTest1()
)

# >

def makeMetaOrigLengthTest2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    metaOrigLength = header["metaOrigLength"]
    metaOrigLength -= 1
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="metadatadisplay-metaOrigLength-002",
    title="Decompressed Metadata Length Greater Than metaOrigLength",
    assertion="The metadata decompressed to a length that is 1 byte greater than the length defined in metaOrigLength",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    metadataIsValid=False,
    sfntDisplaySpecLink="#conform-metaOrigLength",
    data=makeMetaOrigLengthTest2()
)


# -----------------------------
# Metadata Display: Well-Formed
# -----------------------------

# <

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text < text.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-001",
    title="Unescaped < in Content",
    assertion="The text element in the description element contains an unescaped <.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=m
)

# &

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text & text.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-002",
    title="Unescaped & in Content",
    assertion="The text element in the description element contains an unescaped &.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=m
)

# mismatched elements

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </mismatch>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-003",
    title="Mismatched Element Tags",
    assertion="One element begins with <description> but ends with </mismatch>.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=m
)

# unclosed element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-004",
    title="Unclosed Element Tag",
    assertion="The text element element in the description element is not closed.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=m
)

# case mismatch

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </DESCRIPTION>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-005",
    title="Case Mismatch in Element Tags",
    assertion="The <description> element is closed with <DESCRIPTION>.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=m
)

# more than one root

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </description>
</metadata>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-006",
    title="More Than One Root Element",
    assertion="The metadata root element occurs twice.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=m
)

# unknown encoding

m = """
<?xml version="1.0" encoding="VSCACS-GFV-X-CQ34QTAB2Q-IS-NOT-A-VALID-ENCODING"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-007",
    title="Unknown Encoding",
    assertion="The xml encoding is set to 'VSCACS-GFV-X-CQ34QTAB2Q-IS-NOT-A-VALID-ENCODING'.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=m
)

# --------------------------
# Metadata Display: Encoding
# --------------------------

# UTF-8

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-001",
    title="UTF-8 Encoding",
    assertion="The xml encoding is set to UTF-8.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# UTF-16

m = """
<?xml version="1.0" encoding="UTF-16"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
""".strip().replace("    ", "\t").encode("utf-16")

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-002",
    title="UTF-16 Encoding",
    assertion="The xml encoding is set to UTF-16.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# Invalid

m = """
<?xml version="1.0" encoding="ISO-8859-1"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-003",
    title="Invalid Encoding",
    assertion="The xml encoding is set to ISO-8859-1.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=m
)

# -------------------------------------------
# Metadata Display: Schema Validity: metadata
# -------------------------------------------

# valid

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-001",
    title="Valid metadata Element",
    assertion="The metadata element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# missing version

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-002",
    title="No version Attribute in metadata Element",
    assertion="The metadata element does not contain the required version attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# invalid version

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="ABC">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-003",
    title="Invalid version Attribute Value in metadata Element",
    assertion="The metadata element version attribute is set to 'ABC'.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0" unknownattribute="Text">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-004",
    title="Unknown Attrbute in metadata Element",
    assertion="The metadata element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <unknown attribute="Text" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-005",
    title="Unknown Child Element metadata Element",
    assertion="The metadata element contains an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-001",
    title="Valid uniqueid Element",
    assertion="The uniqueid element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# does not exist

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-002",
    title="No uniqueid Element",
    assertion="The uniqueid element doesn't exist.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# duplicate

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-003",
    title="More Than One uniqueid Element",
    assertion="The uniqueid element occurs twice.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# missing id attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-004",
    title="No id Attribute in uniqueid Element",
    assertion="The uniqueid element does not contain the required id attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-metadata-id-required",
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" unknownattribute="Text" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-005",
    title="Unknown Attribute in uniqueid Element",
    assertion="The uniqueid element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown child

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest">
        <unknown attribute="Text" />
    </uniqueid>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-006",
    title="Child Element in uniqueid Element",
    assertion="The uniqueid element contains a child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest">
        Text
    </uniqueid>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-007",
    title="Content in uniqueid Element",
    assertion="The uniqueid element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# -----------------------------------------
# Metadata Display: Schema Validity: vendor
# -----------------------------------------

# valid

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-001",
    title="Valid vendor Element",
    assertion="The vendor element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-002",
    title="Valid vendor Element Without url Attribute",
    assertion="The vendor element does not contain a url attribute but it still matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# does not exist

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-003",
    title="No vendor Element",
    assertion="The vendor element doesn't exist.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# duplicate

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" />
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-004",
    title="More Than One vendor Element",
    assertion="The vendor element occurs twice.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# missing name attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor url="http://w3c.org/Fonts" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-005",
    title="No name Attribute in vendor Element",
    assertion="The vendor element does not contain the required name attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataDisplaySpecLink="#conform-metadata-vendor-required",
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" unknownattribute="Text" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-006",
    title="Unknown Attribute in vendor Element",
    assertion="The vendor element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown child

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts">
        <unknown attribute="Text" />
    </vendor>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-007",
    title="Child Element in vendor Element",
    assertion="The vendor element contains a child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts">
        Text
    </vendor>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-008",
    title="Content in vendor Element",
    assertion="The vendor element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# ------------------------------------------
# Metadata Display: Schema Validity: credits
# ------------------------------------------

# valid - no lang, single credit element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-001",
    title="Valid credits Element With No Language Attribute And A Single credit Element",
    assertion="The credits element does not contain a language attribute but it still matches the schema and it contains one credit child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid - lang, single credit element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits lang="en">
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-002",
    title="Valid credits Element With A Language Attribute And A Single credit Element",
    assertion="The credits element contains contains a language attribute and it matches the schema and it contains one credit child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid - multiple credit elements

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
        <credit name="Credit 2" role="Role 2" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-003",
    title="Valid credits Element With Two credit Elements",
    assertion="The credits element matches the schema and it contains two credit child elements.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# more than one credits

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
    <credits lang="fr">
        <credit name="Credit 1 fr" role="Role 1 fr" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-004",
    title="More Than One credits Element",
    assertion="The credits element occurs more than once.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# missing credit element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-005",
    title="No credit Element in credits Element",
    assertion="The credits element does not contain a credit child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits unknownattribute="Text">
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-006",
    title="Unknown Attribute in credits Element",
    assertion="The credits element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
        <unknown attribute="Text" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-007",
    title="Unknown Child Element in credits Element",
    assertion="The credits element contains an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        Text
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-008",
    title="Content in credits Element",
    assertion="The credits element contains an content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# -----------------------------------------
# Metadata Display: Schema Validity: credit
# -----------------------------------------

# valid

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-001",
    title="Valid credit Element",
    assertion="The credit element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid no url

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-002",
    title="Valid credit Element Without url Attribute",
    assertion="The credit element does not contain a url attribute but it still matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid no role

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-003",
    title="Valid credit Element Without role Attribute",
    assertion="The credit element does not contain a role attribute but it still matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# no name

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-004",
    title="No name attribute in credit Element",
    assertion="The credit element does not contain a name attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" unknownattribute="Test" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-005",
    title="Unknown attribute in credit Element",
    assertion="The credit element contains and unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts">
            <unknown attribute="Text" />
        </credit>
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-006",
    title="Child Element in credit Element",
    assertion="The credit element contains a child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        Text
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-007",
    title="Content in credit Element",
    assertion="The credit element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# ----------------------------------------------
# Metadata Display: Schema Validity: description
# ----------------------------------------------

# valid with url

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-001",
    title="Valid description Element",
    assertion="The description element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid without url

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-002",
    title="Valid description Element Without url Attribute",
    assertion="The description element does not contain a url attribute but it still matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid one text element no language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-003",
    title="Valid description Element With One No Language Tagged text Element",
    assertion="The description element matches the schema. It contains one text element that does not have a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid one text element with language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text lang="en">
            Description with "en" language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-004",
    title="Valid description Element With One Language Tagged text Element",
    assertion="The description element matches the schema. It contains one text element that has a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two text elements no language and language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
        <text lang="en">
            Description with "en" language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-005",
    title="Valid description Element With Mixed text Element Language Tags 1",
    assertion="The description element matches the schema. One text element does not have a language tag. One text element has a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two text elements language and language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text lang="en">
            Description with "en" language.
        </text>
        <text lang="fr">
            Description with "fr" language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-006",
    title="Valid description Element With Mixed text Element Language Tags 2",
    assertion="The description element matches the schema. Two text elements have a language tags.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# more than one description

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
    </description>
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-007",
    title="More Than One description Element",
    assertion="The description element occurs more than once.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# no text element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-008",
    title="No text Element in description Element",
    assertion="The description element does not contain a text child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts" unknownattribute="Text">
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-009",
    title="Unknown Attribute in description Element",
    assertion="The description element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
        <unknown attribute="Text" />
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-010",
    title="Unknown Child Element in description Element",
    assertion="The description element contains an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        Text
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-011",
    title="Content in description Element",
    assertion="The description element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# text element unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text unknownattribute="Text">
            Description without language.
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-012",
    title="Unknown Attribute in description Element text Element",
    assertion="The description element contains a text element with an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# text element child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
            <unknown attribute="Text" />
        </text>
    </description>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-013",
    title="Unknown Child Element in description Element text Element",
    assertion="The description element contains a text element with an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# ------------------------------------------
# Metadata Display: Schema Validity: license
# ------------------------------------------

# valid with url and license

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-001",
    title="Valid license Element",
    assertion="The license element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid no url

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license id="License ID">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-002",
    title="Valid license Element",
    assertion="The license element does not have a url attribute but it still matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid no id

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-003",
    title="Valid license Element",
    assertion="The license element does not have an id attribute but it still matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid one text element no language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-004",
    title="Valid license Element With One No Language Tagged text Element",
    assertion="The license element matches the schema. It contains one text element that does not have a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid one text element with language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text lang="en">
            License with "en" language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-005",
    title="Valid license Element With One Language Tagged text Element",
    assertion="The license element matches the schema. It contains one text element that has a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two text elements no language and language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
        <text lang="en">
            License with "en" language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-006",
    title="Valid license Element With Mixed text Element Language Tags 1",
    assertion="The license element matches the schema. One text element does not have a language tag. One text element has a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two text elements language and language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text lang="en">
            License with "en" language.
        </text>
        <text lang="fr">
            License with "fr" language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-007",
    title="Valid license Element With Mixed text Element Language Tags 2",
    assertion="The license element matches the schema. Two text elements have a language tags.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# more than one license

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
    </license>
    <license url="http://w3c.org/Fonts">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-008",
    title="More Than One license Element",
    assertion="The license element occurs more than once.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# no text element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-009",
    title="No text Element in license Element",
    assertion="The license element does not contain a text child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID" unknownattribute="Text">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-010",
    title="Unknown Attribute in license Element",
    assertion="The license element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
        <unknown attribute="Text" />
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-011",
    title="Unknown Child Element in license Element",
    assertion="The license element contains an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        Text
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-012",
    title="Content in license Element",
    assertion="The license element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# text element unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text unknownattribute="Text">
            License without language.
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-013",
    title="Unknown Attribute in license Element text Element",
    assertion="The license element contains a text element with an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# text element child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
            <unknown attribute="Text" />
        </text>
    </license>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-014",
    title="Unknown Child Element in license Element text Element",
    assertion="The license element contains a text element with an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# --------------------------------------------
# Metadata Display: Schema Validity: copyright
# --------------------------------------------

# valid one text element no language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-001",
    title="Valid copyright Element With One No Language Tagged text Element",
    assertion="The copyright element matches the schema. It contains one text element that does not have a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid one text element with language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text lang="en">
            Copyright with "en" language.
        </text>
    </copyright>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-002",
    title="Valid copyright Element With One Language Tagged text Element",
    assertion="The copyright element matches the schema. It contains one text element that has a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two text elements no language and language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
        </text>
        <text lang="en">
            Copyright with "en" language.
        </text>
    </copyright>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-003",
    title="Valid copyright Element With Mixed text Element Language Tags 1",
    assertion="The copyright element matches the schema. One text element does not have a language tag. One text element has a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two text elements language and language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text lang="en">
            Copyright with "en" language.
        </text>
        <text lang="fr">
            Copyright with "fr" language.
        </text>
    </copyright>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-004",
    title="Valid copyright Element With Mixed text Element Language Tags 2",
    assertion="The copyright element matches the schema. Two text elements have a language tags.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# more than one copyright

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
        </text>
    </copyright>
    <copyright>
        <text>
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-005",
    title="More Than One copyright Element",
    assertion="The copyright element occurs more than once.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# no text element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-006",
    title="No text Element in copyright Element",
    assertion="The copyright element does not contain a text child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright unknownattribute="Text">
        <text>
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-007",
    title="Unknown Attribute in copyright Element",
    assertion="The copyright element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
        </text>
    </copyright>
    <unknown attribute="Text" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-008",
    title="Unknown Child Element in copyright Element",
    assertion="The copyright element contains an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        Text
        <text>
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-009",
    title="Content in copyright Element",
    assertion="The copyright element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# text element unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text unknownattribute="Text">
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-010",
    title="Unknown Attribute in copyright Element text Element",
    assertion="The copyright element contains a text element with an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# text element child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
            <unknown attribute="Text" />
        </text>
    </copyright>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-011",
    title="Unknown Child Element in copyright Element text Element",
    assertion="The copyright element contains a text element with an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# --------------------------------------------
# Metadata Display: Schema Validity: trademark
# --------------------------------------------

# valid one text element no language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-001",
    title="Valid trademark Element With One No Language Tagged text Element",
    assertion="The trademark element matches the schema. It contains one text element that does not have a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid one text element with language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text lang="en">
            Trademark with "en" language.
        </text>
    </trademark>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-002",
    title="Valid trademark Element With One Language Tagged text Element",
    assertion="The trademark element matches the schema. It contains one text element that has a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two text elements no language and language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
        </text>
        <text lang="en">
            Trademark with "en" language.
        </text>
    </trademark>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-003",
    title="Valid trademark Element With Mixed text Element Language Tags 1",
    assertion="The trademark element matches the schema. One text element does not have a language tag. One text element has a language tag.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two text elements language and language

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text lang="en">
            Trademark with "en" language.
        </text>
        <text lang="fr">
            Trademark with "fr" language.
        </text>
    </trademark>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-004",
    title="Valid trademark Element With Mixed text Element Language Tags 2",
    assertion="The trademark element matches the schema. Two text elements have a language tags.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# more than one trademark

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
        </text>
    </trademark>
    <trademark>
        <text>
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-005",
    title="More Than One trademark Element",
    assertion="The trademark element occurs more than once.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# no text element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-006",
    title="No text Element in trademark Element",
    assertion="The trademark element does not contain a text child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark unknownattribute="Text">
        <text>
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-007",
    title="Unknown Attribute in trademark Element",
    assertion="The trademark element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
        </text>
    </trademark>
    <unknown attribute="Text" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-008",
    title="Unknown Child Element in trademark Element",
    assertion="The trademark element contains an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        Text
        <text>
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-009",
    title="Content in trademark Element",
    assertion="The trademark element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# text element unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text unknownattribute="Text">
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-010",
    title="Unknown Attribute in trademark Element text Element",
    assertion="The trademark element contains a text element with an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# text element child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
            <unknown attribute="Text" />
        </text>
    </trademark>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-011",
    title="Unknown Child Element in trademark Element text Element",
    assertion="The trademark element contains a text element with an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-001",
    title="Valid licensee Element",
    assertion="The uniqueid element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# duplicate

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" />
    <licensee name="Licensee Name" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-002",
    title="More Than One licensee Element",
    assertion="The uniqueid element occurs more than once.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# missing name

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-003",
    title="No name Attribute in licensee Element",
    assertion="The uniqueid element does not contain the required name attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" unknownattribute="Text" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-004",
    title="Unknown Attribute in licensee Element",
    assertion="The uniqueid element occures more than once.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name">
        <unknown attribute="Text" />
    </licensee>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-005",
    title="Child Element in licensee Element",
    assertion="The uniqueid element contains a child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name">
        Text
    </licensee>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-006",
    title="Content in licensee Element",
    assertion="The uniqueid element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# --------------------------------------------
# Metadata Display: Schema Validity: extension
# --------------------------------------------

# valid

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-001",
    title="Valid extension Element",
    assertion="The extension element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two extensions

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
    <extension id="Extension 2">
        <name>Extension 2 - Name Without Language</name>
        <item id="Extension 2 - Item 1 ID">
            <name>Extension 2 - Item 1 - Name Without Language</name>
            <value>Extension 2 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-002",
    title="Two Valid extension Elements",
    assertion="Two extension elements match the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid no id

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension>
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-003",
    title="Valid extension Element Without id Attribute",
    assertion="The extension element does not have an id attribute but it still matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid no name

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-004",
    title="Valid extension Element Without name Element",
    assertion="The extension element does not have a name child element but it still matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid one untagged name one tagged name

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <name lang="en">Extension 1 - Name With "en" Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-005",
    title="Valid extension Element With Two name Elements 1",
    assertion="The extension element contains one name element without a lang attribute and another with a lang attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid two tagged names

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name lang="en">Extension 1 - Name With "en" Language</name>
        <name lang="fr">Extension 1 - Name With "fr" Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-006",
    title="Valid extension Element With Two name Elements 2",
    assertion="The extension element contains two name elements with lang attributes.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid more than one item

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
        <item id="Extension 1 - Item 2 ID">
            <name>Extension 1 - Item 2 - Name Without Language</name>
            <value>Extension 1 - Item 2 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-007",
    title="Valid extension Element With Two item Elements",
    assertion="The extension element contains two item child elements.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# no item

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-008",
    title="No item Element in extension Element",
    assertion="The extension element does not contain an item child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1" unknownattribute="Text">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-009",
    title="Unknown Attribute in extension Element",
    assertion="The extension element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown child

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
    <unknown attribute="Text" />
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-010",
    title="Unknown Child Element in extension Element",
    assertion="The extension element contains an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)


# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        Text
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-011",
    title="Content in extension Element",
    assertion="The extension element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - item
# ---------------------------------------------------

# valid

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-012",
    title="Valid item Element in extension Element",
    assertion="The item element in the extension element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid multiple languages

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <name lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
            <name lang="fr">Extension 1 - Item 1 - Name With "fr" Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
            <value lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
            <value lang="fr">Extension 1 - Item 1 - Value With "fr" Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-013",
    title="Valid item Element With Multiple Languages in extension Element",
    assertion="The item element in the extension element contains a variety of languages.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid no id

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item>
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-014",
    title="Valid item Element Without id Attribute in extension Element",
    assertion="The item element in the extension element does not contain an id attribute but it still matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid name no tag and tagged

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <name lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-015",
    title="Valid item Element With Two name Elements in extension Element 1",
    assertion="The item element in the extension element contains one name child element with no lang attribute and one with a lang attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid name two tagged

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
            <name lang="fr">Extension 1 - Item 1 - Name With "fr" Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-016",
    title="Valid item Element With Two name Elements in extension Element 2",
    assertion="The item element in the extension element contains two name child elements with lang attributes.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid value no tag and tagged

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
            <value lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-017",
    title="Valid item Element With Two value Elements in extension Element 1",
    assertion="The item element in the extension element contains one value child element with no lang attribute and one with a lang attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid value two tagged

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
            <value lang="fr">Extension 1 - Item 1 - Value With "fr" Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-018",
    title="Valid item Element With Two value Elements in extension Element 2",
    assertion="The item element in the extension element contains two value child elements with lang attributes.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# no name

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-019",
    title="No name Element in item Element in extension Element",
    assertion="The item element in the extension element does not contain a name child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# no value

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-020",
    title="No value Element in item Element in extension Element",
    assertion="The item element in the extension element does not contain a value child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID" unknownattribute="Text">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-021",
    title="Unknown Attribute in item Element in extension Element",
    assertion="The item element in the extension element contains an unknown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# unknown child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
            <unknown attribute="Text" />
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-022",
    title="Unknown Child Element in item Element in extension Element",
    assertion="The item element in the extension element contains an unknown child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# content

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            Text
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-023",
    title="Content in item Element in extension Element",
    assertion="The item element in the extension element contains content.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# ----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - name
# ----------------------------------------------------------

# valid no lang

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-024",
    title="Valid name Element in item Element in extension Element",
    assertion="The name element in the item element in the extension element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid lang

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-025",
    title="Valid name Element With lang Attribute in item Element in extension Element",
    assertion="The name element in the item element in the extension element contains a lang attribute and it matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name unknownattribute="Text">Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-026",
    title="Unkown Attribute in name Element in item Element in extension Element",
    assertion="The name element in the item element in the extension element contains an unkown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)


# child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>
                Extension 1 - Item 1 - Name Without Language
                <unknown attribute="Text" />
            </name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-027",
    title="Child Element in name Element in item Element in extension Element",
    assertion="The name element in the item element in the extension element contains a child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# -----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - value
# -----------------------------------------------------------

# valid no lang

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-028",
    title="Valid value Element in item Element in extension Element",
    assertion="The value element in the item element in the extension element matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# valid lang

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-029",
    title="Valid value Element With lang Attribute in item Element in extension Element",
    assertion="The value element in the item element in the extension element contains a lang attribute and it matches the schema.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=True,
    metadata=m
)

# unknown attribute

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value unknownattribute="Text">Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-030",
    title="Unkown Attribute in value Element in item Element in extension Element",
    assertion="The value element in the item element in the extension element contains an unkown attribute.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# child element

m = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>
                Extension 1 - Item 1 - Value Without Language
                <unknown attribute="Text" />
            </value>
        </item>
    </extension>
</metadata>
"""

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-031",
    title="Child Element in value Element in item Element in extension Element",
    assertion="The value element in the item element in the extension element contains a child element.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    metadataIsValid=False,
    metadata=m
)

# ------------------
# Generate the Index
# ------------------

print "Compiling index..."

testGroups = []

for tag, title, url in groupDefinitions:
    group = dict(title=title, url=url, testCases=testRegistry[tag])
    testGroups.append(group)

generateSFNTDisplayIndexHTML(directory=userAgentTestDirectory, testCases=testGroups)

# -----------------------
# Check for Unknown Files
# -----------------------

skip = "testcaseindex".split(" ")

xhtPattern = os.path.join(userAgentTestDirectory, "*.xht")
woffPattern = os.path.join(userAgentTestResourcesDirectory, "*.woff")

filesOnDisk = glob.glob(xhtPattern)
filesOnDisk += glob.glob(woffPattern)

for path in filesOnDisk:
    identifier = os.path.basename(path)
    identifier = identifier.split(".")[0]
    identifier = identifier.replace("-ref", "")
    if identifier not in registeredIdentifiers and identifier not in skip:
        print "Unknown file:", path