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
    ("directory", "WOFF Table Directory Tests", specificationURL+"#TableDirectory"),
    ("blocks", "WOFF Header Tests", specificationURL+"#OverallStructure"),
]

testRegistry = {}
for group in groupDefinitions:
    tag = group[0]
    testRegistry[tag] = []

# ---------------
# File Generators
# ---------------

registeredIdentifiers = set()

def writeFileStructureTest(identifier, flavor="CFF", title=None, assertion=None, specLink=None, credits=[], flags=[], shouldDisplaySFNT=None, data=None):
    print "Compiling %s..." % identifier
    assert identifier not in registeredIdentifiers, "Duplicte identifier! %s" % identifier
    registeredIdentifiers.add(identifier)

    if specLink is None:
        specLink = ""
    specLink = specificationURL + specLink
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
        specLink=specLink,
        assertion=assertion,
        credits=credits,
        flags=flags,
        shouldDisplay=shouldDisplaySFNT
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
            assertion=assertion
        )
    )


#def registerMetadataDisplayTest(title=None, assertion=None, shouldDisplayMetadata=None, specLink=None, data=None):
#    assert title is not None
#    assert assertion is not None
#    assert shouldDisplayMetadata is not None
#    assert data is not None

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
    data=makeValidWOFF2()
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
    data=makeValidWOFF4()
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
    data=makeValidWOFF6()
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
    data=makeValidWOFF8()
)

## ---------------------------------
## File Structure: Header: Structure
## ---------------------------------
#
#def makeHeaderInvalidStructure1():
#    header, directory, tableData = defaultTestData()
#    data = "\0" * len(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
#    return data
#
#writeFileStructureTest(
#    identifier="header-structure-001",
#    title="Header Structure 1",
#    assertion="Header does not have the correct structure.",
#    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
#    shouldDisplaySFNT=False,
#    data=makeHeaderInvalidStructure1()
#)

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
    specLink="#conform-nonmagicnumber-reject",
    data=makeHeaderInvalidSignature1()
)

## ------------------------------
## File Structure: Header: flavor
## ------------------------------
#
#def makeHeaderInvalidFlavor2():
#    header, directory, tableData = defaultTestData(flavor="cff")
#    header["flavor"] = "\000\001\000\000"
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
#    return data
#
#writeFileStructureTest(
#    identifier="header-flavor-002",
#    title="Header Flavor 2",
#    assertion="Header flavor is 0x00010000 but the SFNT data contains a CFF table.",
#    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
#    shouldDisplaySFNT=False,
#    data=makeHeaderInvalidFlavor2()
#)
#
#def makeHeaderInvalidFlavor3():
#    header, directory, tableData = defaultTestData(flavor="ttf")
#    header["flavor"] = "OTTO"
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
#    return data
#
#writeFileStructureTest(
#    identifier="header-flavor-003",
#    title="Header Flavor 3",
#    assertion="Header flavor is OTTO but the SFNT data does not a CFF table.",
#    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
#    shouldDisplaySFNT=False,
#    data=makeHeaderInvalidFlavor3()
#)

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
    data=makeHeaderInvalidLength2()
)

# ---------------------------------
# File Structure: Header: numTables
# ---------------------------------

#def makeHeaderInvalidNumTables1():
#    header, directory, tableData = defaultTestData()
#    header["numTables"] = 0
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
#    return data
#
#writeFileStructureTest(
#    title="Header Number of Tables 1",
#    assertion="Header contains 0 for the number of tables.",
#    shouldDisplaySFNT=False,
#    data=makeHeaderInvalidNumTables1()
#)
#
#def makeHeaderInvalidNumTables2():
#    header, directory, tableData = defaultTestData()
#    header["numTables"] += 1
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
#    return data
#
#writeFileStructureTest(
#    title="Header Number of Tables 2",
#    assertion="Header contains one more table defined in the number of tables than is packed.",
#    shouldDisplaySFNT=False,
#    data=makeHeaderInvalidNumTables2()
#)

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
    specLink="#conform-totalsize-longword-reject",
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
    specLink="#conform-totalsize-longword-reject",
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
    specLink="#conform-totalsize-longword-reject",
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
    specLink="#conform-reserved-reject",
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
    specLink="#conform-extraneous-reject",
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
    specLink="#conform-extraneous-reject",
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
    specLink="#conform-extraneous-reject",
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
    specLink="#conform-extraneous-reject",
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
    specLink="#conform-extraneous-reject",
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
    specLink="#conform-extraneous-reject",
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
    specLink="#conform-extraneous-reject",
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
    specLink="#conform-extraneous-reject",
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
    specLink="#conform-overlap-reject",
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
    specLink="#conform-overlap-reject",
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
    specLink="#conform-overlap-reject",
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
    specLink="#conform-overlap-reject",
    data=makeOverlappingData4()
)

# -------------------------------------------------
# File Structure: Data Blocks: Metadata Not Present
# -------------------------------------------------

# metadata length is not 0 but the offset = 0

def makeMetadataZeroData1():
    header, directory, tableData = defaultTestData()
    header["metaOffset"] = 0
    header["metaLength"] = 1
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="blocks-metadata-absent-001",
    title="Metadata Length Not Set to Zero",
    assertion="The metadata length is set to one but the offset is zero. This test case also fails for other reasons: the offset/length creates an overlap with the header block, the metadata won't decompress.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    specLink="#conform-zerometaprivate",
    data=makeMetadataZeroData1()
)

# metadata length = zero but the offset > zero

def makeMetadataZeroData2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    header["metaLength"] = 0
    header["metaOffset"] = header["length"]
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="blocks-metadata-absent-002",
    title="Metadata Offset Not Set to Zero",
    assertion="The metadata length is set to zero but the offset is set to the end of the file.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    specLink="#conform-zerometaprivate",
    data=makeMetadataZeroData2()
)

# -----------------------------------------------------
# File Structure: Data Blocks: Private Data Not Present
# -----------------------------------------------------

# private data length > 0 but the offset = 0

def makePrivateDataZeroData1():
    header, directory, tableData = defaultTestData()
    header["privOffset"] = 0
    header["privLength"] = 1
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="blocks-private-absent-001",
    title="Private Data Length Not Set to Zero",
    assertion="The private data length is set to one but the offset is zero. This test case also fails for another reason: the offset/length creates an overlap with the header block.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    specLink="#conform-zerometaprivate",
    data=makePrivateDataZeroData1()
)

# private data length = 0 but the offset > 0

def makePrivateDataZeroData2():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    header["privLength"] = 0
    header["privOffset"] = header["length"]
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="blocks-private-absent-002",
    title="Private Data Offset Not Set to Zero",
    assertion="The private data length is set to zero but the offset is set to the end of the file.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    specLink="#conform-zerometaprivate",
    data=makePrivateDataZeroData2()
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
    specLink="#conform-tablesize-longword",
    data=makeTableData4Byte1()
)

# table is padded with something other than null bytes

def makeTableData4Byte2():
    header, directory, tableData = defaultTestData()
    paddedAtLeastOne = False
    for tag, (origData, compData) in tableData.items():
        paddingLength = calcPaddingLength(len(compData))
        if paddingLength:
            paddedAtLeastOne = True
        compData += "\x01" * paddingLength
        tableData[tag] = (origData, compData)
    assert paddedAtLeastOne
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="directory-4-byte-002",
    title="Font Table Data Padded With Non-Null",
    assertion="Table data is padded with \\01 instead of \\00.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    specLink="#conform-tablesize-longword",
    data=makeTableData4Byte2()
)

# final table is not padded

def makeTableData4Byte3():
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
    identifier="directory-4-byte-003",
    title="Final Font Table Data Not Padded",
    assertion="The final table in the table data block is not padded to a 4-byte boundary.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    specLink="#conform-tablesize-longword",
    data=makeTableData4Byte3()
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
    specLink="#conform-diroverlap-reject",
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
    specLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange2()
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
    specLink="#conform-compressedlarger",
    data=makeTableDataCompressionLength1()
)

# ------------------------------------------------
# File Structure: Table Directory: Ascending Order
# ------------------------------------------------

def makeTableDirectoryAscending1():
    header, directory, tableData = defaultTestData()
    directory = [(entry["tag"], entry) for entry in directory]
    directoryData = ""
    for tag, table in reversed(sorted(directory)):
        directoryData += sstruct.pack(woffDirectoryEntryFormat, table)
    directory = [i[1] for i in directory]
    data = packTestHeader(header) + directoryData + packTestTableData(directory, tableData)
    return data

writeFileStructureTest(
    identifier="directory-ascending-001",
    title="Font Table Directory Not In Ascending Order",
    assertion="The tables in the directory are in descending order.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    specLink="#conform-ascending",
    data=makeTableDirectoryAscending1()
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
    identifier="directory-zlib-001",
    title="Font Table Data Invalid Compressed Data",
    assertion="One compressed table has had its compressed data replaced with \\01 making it incompatible with zlib.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=False,
    specLink="#conform-mustzlib",
    data=makeTableZlibCompressionTest1()
)

## --------------------------------------
## Metadata Display: Invalid: Compression
## --------------------------------------
#
#def makeMetadataCompressionTest1():
#    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
#    metaLength = header["metaLength"]
#    metaOrigLength = header["metaOrigLength"]
#    assert metaOrigLength > metaLength
#    header["metaLength"] = metaOrigLength
#    header["length"] += metaOrigLength - metaLength
#    origMetadata, compMetadata = metadata
#    metadata = (origMetadata, origMetadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Compression 1",
#    assertion="Metadata is not compressed.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-invalid-mustignore",
#    data=makeMetadataCompressionTest1()
#)
#
## --------------------------------------
## Metadata Display: Invalid: Well-Formed
## --------------------------------------
#
#def makeMetadataWellFormedTest1():
#    # strip off the closing >
#    metadata = testDataWOFFMetadata[:-1]
#    assert metadata[-1] != ">"
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Well-Formed 1",
#    assertion="Metadata is not well-formed.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-invalid-mustignore",
#    data=makeMetadataWellFormedTest1()
#)
#
## -----------------------------------
## Metadata Display: Invalid: Encoding
## -----------------------------------
#
#def makeMetadataEncodingTest1():
#    metadata = testDataWOFFMetadata.replace("encoding=\"UTF-8\"", "encoding=\"ISO-8859-1\"")
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Encoding 1",
#    assertion="Metadata is not encoded with UTF-8 or UTF-16.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-invalid-mustignore",
#    data=makeMetadataEncodingTest1()
#)
#
## -------------------------------------------
## Metadata Display: Schema Validity: metadata
## -------------------------------------------
#
#def makeMetadataElementTest1():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <notmetadata>
#    </notmetadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Element Missing 1",
#    assertion="No metadata element.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataElementTest1()
#)
#
## ------------------------------------------
## Metadata Display: Schema Validity: version
## ------------------------------------------
#
## missing
#
#def makeMetadataVersionTest1():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata>
#        <uniqueid id="org.w3.webfonts.wofftest" />
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Version Attribute Missing 1",
#    assertion="Metadata element does not contain version attribute.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataVersionTest1()
#)
#
## not 1.0
#
#def makeMetadataVersionTest2():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="10.0">
#        <uniqueid id="org.w3.webfonts.wofftest" />
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Version Attribute Missing 2",
#    assertion="Metadata element contains version attribute with a value other than 1.0. *** Is this a requirement?",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataVersionTest2()
#)
#
## -------------------------------------------
## Metadata Display: Schema Validity: uniqueid
## -------------------------------------------
#
## missing
#
#def makeMetadataUniqueIDTest1():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <uniqueid />
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Unique ID 1",
#    assertion="Unique ID element does not contain ID attribute.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataUniqueIDTest1()
#)
#
## -----------------------------------------
## Metadata Display: Schema Validity: vendor
## -----------------------------------------
#
#def makeMetadataVendorTest1():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <vendor />
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Vendor 1",
#    assertion="Vendor element does not contain name attribute.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataVendorTest1()
#)
#
## -----------------------------------------
## Metadata Display: Schema Validity: credit
## -----------------------------------------
#
#def makeMetadataCreditTest1():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <credits>
#            <credit />
#        </credits>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Credit 1",
#    assertion="Credit element does not contain name attribute.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataCreditTest1()
#)
#
## ------------------------------------------
## Metadata Display: Schema Validity: license
## ------------------------------------------
#
## no text sub element in license
#
#def makeMetadataMissingTextSubelementTest2():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <license>
#        </license>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Missing Text Subelement 2",
#    assertion="No text subelement in license element.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataMissingTextSubelementTest2()
#)
#
## ----------------------------------------------
## Metadata Display: Schema Validity: assertion
## ----------------------------------------------
#
## no text sub element in assertion
#
#def makeMetadataMissingTextSubelementTest1():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <assertion>
#        </assertion>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Missing Text Subelement 1",
#    assertion="No text subelement in assertion element.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataMissingTextSubelementTest1()
#)
#
## --------------------------------------------
## Metadata Display: Schema Validity: copyright
## --------------------------------------------
#
## no lang defined
#
#def makeMetadataTextLanguageTest1():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <copyright>
#            <text>
#                Some text.
#            </text>
#        </copyright>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Text Language 1",
#    assertion="Text subelement in copyright element does not have language definition.",
#    shouldDisplayMetadata=True,
#    data=makeMetadataTextLanguageTest1()
#)
#
## lang defined
#
#def makeMetadataTextLanguageTest2():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <copyright>
#            <text lang="en">
#                Some text.
#            </text>
#        </copyright>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Text Language 2",
#    assertion="Text subelement in copyright element does have language definition.",
#    shouldDisplayMetadata=True,
#    data=makeMetadataTextLanguageTest2()
#)
#
## no text sub element in copyright
#
#def makeMetadataMissingTextSubelementTest3():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <copyright>
#        </copyright>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Missing Text Subelement 3",
#    assertion="No text subelement in copyright element.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataMissingTextSubelementTest3()
#)
#
## --------------------------------------------
## Metadata Display: Schema Validity: trademark
## --------------------------------------------
#
## no text sub element in trademark
#
#def makeMetadataMissingTextSubelementTest4():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <trademark>
#        </trademark>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Missing Text Subelement 4",
#    assertion="No text subelement in trademark element.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataMissingTextSubelementTest4()
#)
#
## -------------------------------------------
## Metadata Display: Schema Validity: licensee
## -------------------------------------------
#
#def makeMetadataCreditTest1():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <licensee />
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Credit 1",
#    assertion="Licensee element does not contain name attribute.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataCreditTest1()
#)
#
## --------------------------------------------
## Metadata Display: Schema Validity: extension
## --------------------------------------------
#
#def makeMetadataExtensionTest1():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <extension>
#            <item>
#                <name>Name</name>
#                <value>Value</value>
#            </item>
#        </extension>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Extension 1",
#    assertion="Extension element does not contain a name subelement.",
#    shouldDisplayMetadata=True,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataExtensionTest1()
#)
#
## no item
#
#def makeMetadataExtensionTest2():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <extension>
#            <name>Name</name>
#        </extension>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Extension 2",
#    assertion="Extension element does not contain an item subelement.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-metadata-schemavalid",
#    data=makeMetadataExtensionTest2()
#)
#
## no name in item
#
#def makeMetadataExtensionTest3():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <extension>
#            <item>
#                <value>Value</value>
#            </item>
#        </extension>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Extension 3",
#    assertion="Item subelement in extension element does not contain name subelement.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-noname-ignore",
#    data=makeMetadataExtensionTest3()
#)
#
## no value in item
#
#def makeMetadataExtensionTest4():
#    metadata = """
#    <?xml version="1.0" encoding="UTF-8"?>
#    <metadata version="1.0">
#        <extension>
#            <item>
#                <name>Name</name>
#            </item>
#        </extension>
#    </metadata>
#    """.strip()
#    metadata = stripMetadata(metadata)
#    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
#    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
#    return data
#
#registerMetadataDisplayTest(
#    title="Metadata Extension 4",
#    assertion="Item subelement in extension element does not contain value subelement.",
#    shouldDisplayMetadata=False,
#    specLink="#conform-novalue-ignore",
#    data=makeMetadataExtensionTest4()
#)

# ------------------
# Generate the Index
# ------------------

print "Compiling index..."

testGroups = []

for tag, title, url in groupDefinitions:
    group = dict(title=title, url=url, testCases=testRegistry[tag])
    testGroups.append(group)

generateSFNTDisplayIndexHTML(directory=userAgentTestDirectory, testCases=testGroups)
