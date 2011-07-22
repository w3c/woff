import os
import shutil
import glob
import struct
import sstruct
from testCaseGeneratorLib.woff import packTestHeader, packTestDirectory, packTestTableData, packTestMetadata, packTestPrivateData
from testCaseGeneratorLib.defaultData import defaultTestData, testDataWOFFMetadata, testDataWOFFPrivateData
from testCaseGeneratorLib.paths import resourcesDirectory, formatDirectory, formatTestDirectory, formatResourcesDirectory
from testCaseGeneratorLib.html import generateFormatIndexHTML
from testCaseGeneratorLib import sharedCases
from testCaseGeneratorLib.sharedCases import *

# ------------------------
# Specification URL
# This is used frequently.
# ------------------------

specificationURL = "http://dev.w3.org/webfonts/WOFF/spec/"

# ------------------
# Directory Creation
# (if needed)
# ------------------

if not os.path.exists(formatDirectory):
    os.mkdir(formatDirectory)
if not os.path.exists(formatTestDirectory):
    os.mkdir(formatTestDirectory)
if not os.path.exists(formatResourcesDirectory):
    os.mkdir(formatResourcesDirectory)

# -------------------
# Move HTML Resources
# -------------------

# index css
destPath = os.path.join(formatResourcesDirectory, "index.css")
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
    ("valid", "Valid WOFFs", None),
    ("header", "WOFF Header Tests", specificationURL+"#WOFFHeader"),
    ("blocks", "WOFF Data Block Tests", specificationURL+"#OverallStructure"),
    ("directory", "WOFF Table Directory Tests", specificationURL+"#TableDirectory"),
    ("tabledata", "WOFF Table Data Tests", specificationURL+"#DataTables"),
    ("metadata", "WOFF Metadata Tests", specificationURL+"#Metadata"),
    ("privatedata", "WOFF Private Data Tests", specificationURL+"#Private")
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

def writeTest(identifier, title, description, data, specLink=None, credits=[], valid=False):
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

    # generate the WOFF
    woffPath = os.path.join(formatTestDirectory, identifier) + ".woff"
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
            valid=valid,
            specLink=specLink
        )
    )

def writeMetadataTest(identifier, title=None, description=None, credits=[], specLink=None, valid=False, metadata=None):
    """
    This is a convenience functon that eliminates the need to make a complete
    WOFF when only the metadata is being tested.
    """
    # dynamically get some data from the shared cases as needed
    if title is None:
        assert description is None
        assert metadata is None
        parts = identifier.split("-")
        assert parts[0] == "metadata"
        number = int(parts[-1])
        group = parts[1:-1]
        group = [i.title() for i in group]
        group = "".join(group)
        importBase = "metadata" + group + str(number)
        title = getattr(sharedCases, importBase + "Title")
        description = getattr(sharedCases, importBase + "Description")
        credits = getattr(sharedCases, importBase + "Credits")
        metadata = getattr(sharedCases, importBase + "Metadata")
    assert metadata is not None
    assert valid is not None
    # compile the WOFF
    data, metadata = makeMetadataTest(metadata)
    # pass to the more verbose function
    if specLink is None:
        specLink = "#Metadata"
    kwargs = dict(
        title=title,
        description=description,
        credits=credits,
        specLink=specLink,
        valid=valid,
        data=data
    )
    writeTest(
        identifier,
        **kwargs
    )

# -----------
# Valid Files
# -----------

# CFF

writeTest(
    identifier="valid-001",
    title=makeValidWOFF1Title,
    description=makeValidWOFF1Description,
    credits=makeValidWOFF1Credits,
    valid=True,
    data=makeValidWOFF1()
)

writeTest(
    identifier="valid-002",
    title=makeValidWOFF2Title,
    description=makeValidWOFF2Description,
    credits=makeValidWOFF2Credits,
    valid=True,
    data=makeValidWOFF2(),
)

writeTest(
    identifier="valid-003",
    title=makeValidWOFF3Title,
    description=makeValidWOFF3Description,
    credits=makeValidWOFF3Credits,
    valid=True,
    data=makeValidWOFF3()
)

writeTest(
    identifier="valid-004",
    title=makeValidWOFF4Title,
    description=makeValidWOFF4Description,
    credits=makeValidWOFF4Credits,
    valid=True,
    data=makeValidWOFF4(),
)

# TTF

writeTest(
    identifier="valid-005",
    title=makeValidWOFF5Title,
    description=makeValidWOFF5Description,
    credits=makeValidWOFF5Credits,
    valid=True,
    data=makeValidWOFF5()
)

writeTest(
    identifier="valid-006",
    title=makeValidWOFF6Title,
    description=makeValidWOFF6Description,
    credits=makeValidWOFF6Credits,
    valid=True,
    data=makeValidWOFF6(),
)

writeTest(
    identifier="valid-007",
    title=makeValidWOFF7Title,
    description=makeValidWOFF7Description,
    credits=makeValidWOFF7Credits,
    valid=True,
    data=makeValidWOFF7()
)

writeTest(
    identifier="valid-008",
    title=makeValidWOFF8Title,
    description=makeValidWOFF8Description,
    credits=makeValidWOFF8Credits,
    valid=True,
    data=makeValidWOFF8(),
)

# ---------------------------------
# File Structure: Header: signature
# ---------------------------------

writeTest(
    identifier="header-signature-001",
    title=makeHeaderInvalidSignature1Title,
    description=makeHeaderInvalidSignature1Description,
    credits=makeHeaderInvalidSignature1Credits,
    valid=False,
    specLink="#conform-magicnumber",
    data=makeHeaderInvalidSignature1()
)

# ------------------------------
# File Structure: Header: flavor
# ------------------------------

# TTF flavor but CFF data

def makeHeaderInvalidFlavor1():
    header, directory, tableData = defaultTestData()
    header["flavor"] = "\000\001\000\000"
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeTest(
    identifier="header-flavor-001",
    title="Header Flavor Incorrectly Set to 0x00010000",
    description="The header flavor is set to 0x00010000 but the table data contains CFF data, not TTF data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#WOFFHeader",
    data=makeHeaderInvalidFlavor1()
)

# CFF flavor but TTF data

def makeHeaderInvalidFlavor2():
    header, directory, tableData = defaultTestData(flavor="ttf")
    header["flavor"] = "OTTO"
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeTest(
    identifier="header-flavor-002",
    title="Header Flavor Incorrectly Set to OTTO",
    description="The header flavor is set to OTTO but the table data contains TTF data, not CFF data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#WOFFHeader",
    data=makeHeaderInvalidFlavor2()
)

# ------------------------------
# File Structure: Header: length
# ------------------------------

writeTest(
    identifier="header-length-001",
    title=makeHeaderInvalidLength1Title,
    description=makeHeaderInvalidLength1Description,
    credits=makeHeaderInvalidLength1Credits,
    valid=False,
    specLink="#WOFFHeader",
    data=makeHeaderInvalidLength1()
)

writeTest(
    identifier="header-length-002",
    title=makeHeaderInvalidLength2Title,
    description=makeHeaderInvalidLength2Description,
    credits=makeHeaderInvalidLength2Credits,
    valid=False,
    specLink="#WOFFHeader",
    data=makeHeaderInvalidLength2()
)

# ---------------------------------
# File Structure: Header: numTables
# ---------------------------------

writeTest(
    identifier="header-numTables-001",
    title=makeHeaderInvalidNumTables1Title,
    description=makeHeaderInvalidNumTables1Description,
    credits=makeHeaderInvalidNumTables1Credits,
    valid=False,
    specLink="#WOFFHeader",
    data=makeHeaderInvalidNumTables1()
)

# -------------------------------------
# File Structure: Header: totalSfntSize
# -------------------------------------

writeTest(
    identifier="header-totalSfntSize-001",
    title=makeHeaderInvalidTotalSfntSize1Title,
    description=makeHeaderInvalidTotalSfntSize1Description,
    credits=makeHeaderInvalidTotalSfntSize1Credits,
    valid=False,
    specLink="#conform-totalsize-longword",
    data=makeHeaderInvalidTotalSfntSize1()
)

writeTest(
    identifier="header-totalSfntSize-002",
    title=makeHeaderInvalidTotalSfntSize2Title,
    description=makeHeaderInvalidTotalSfntSize2Description,
    credits=makeHeaderInvalidTotalSfntSize2Credits,
    valid=False,
    specLink="#conform-totalsize-longword",
    data=makeHeaderInvalidTotalSfntSize2()
)

writeTest(
    identifier="header-totalSfntSize-003",
    title=makeHeaderInvalidTotalSfntSize3Title,
    description=makeHeaderInvalidTotalSfntSize3Description,
    credits=makeHeaderInvalidTotalSfntSize3Credits,
    valid=False,
    specLink="#conform-totalsize-longword",
    data=makeHeaderInvalidTotalSfntSize3()
)

# --------------------------------
# File Structure: Header: reserved
# --------------------------------

writeTest(
    identifier="header-reserved-001",
    title=makeHeaderInvalidReserved1Title,
    description=makeHeaderInvalidReserved1Description,
    credits=makeHeaderInvalidReserved1Credits,
    valid=False,
    specLink="#conform-reserved",
    data=makeHeaderInvalidReserved1()
)

# --------------------------------------------
# File Structure: Data Blocks: Extraneous Data
# --------------------------------------------

# between table directory and table data

writeTest(
    identifier="blocks-extraneous-data-001",
    title=makeExtraneousData1Title,
    description=makeExtraneousData1Description,
    credits=makeExtraneousData1Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData1()
)

# after table data with no metadata or private data

writeTest(
    identifier="blocks-extraneous-data-002",
    title=makeExtraneousData2Title,
    description=makeExtraneousData2Description,
    credits=makeExtraneousData2Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData2()
)

# between tabledata and metadata

writeTest(
    identifier="blocks-extraneous-data-003",
    title=makeExtraneousData3Title,
    description=makeExtraneousData3Description,
    credits=makeExtraneousData3Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData3()
)

# between tabledata and private data

writeTest(
    identifier="blocks-extraneous-data-004",
    title=makeExtraneousData4Title,
    description=makeExtraneousData4Description,
    credits=makeExtraneousData4Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData4()
)

# between metadata and private data

writeTest(
    identifier="blocks-extraneous-data-005",
    title=makeExtraneousData5Title,
    description=makeExtraneousData5Description,
    credits=makeExtraneousData5Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData5()
)

# after metadata with no private data

writeTest(
    identifier="blocks-extraneous-data-006",
    title=makeExtraneousData6Title,
    description=makeExtraneousData6Description,
    credits=makeExtraneousData6Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData6()
)

# after private data

writeTest(
    identifier="blocks-extraneous-data-007",
    title=makeExtraneousData7Title,
    description=makeExtraneousData7Description,
    credits=makeExtraneousData7Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData7()
)

# -------------------------------------
# File Structure: Data Blocks: Overlaps
# -------------------------------------

# metadata overlaps the table data

writeTest(
    identifier="blocks-overlap-001",
    title=makeOverlappingData1Title,
    description=makeOverlappingData1Description,
    credits=makeOverlappingData1Credits,
    valid=False,
    specLink="#conform-overlap-reject",
    data=makeOverlappingData1()
)

# private data overlaps the table data

writeTest(
    identifier="blocks-overlap-002",
    title=makeOverlappingData2Title,
    description=makeOverlappingData2Description,
    credits=makeOverlappingData2Credits,
    valid=False,
    specLink="#conform-overlap-reject",
    data=makeOverlappingData2()
)

# private data overlaps the metadata

writeTest(
    identifier="blocks-overlap-003",
    title=makeOverlappingData3Title,
    description=makeOverlappingData3Description,
    credits=makeOverlappingData3Credits,
    valid=False,
    specLink="#conform-overlap-reject",
    data=makeOverlappingData3()
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

writeTest(
    identifier="blocks-metadata-absent-001",
    title="Metadata Length Not Set to Zero",
    description="The metadata length is set to one but the offset is zero. This test case also fails for other reasons: the offset/length creates an overlap with the header block, the metadata won't decompress.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
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

writeTest(
    identifier="blocks-metadata-absent-002",
    title="Metadata Offset Not Set to Zero",
    description="The metadata length is set to zero but the offset is set to the end of the file.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
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

writeTest(
    identifier="blocks-private-absent-001",
    title="Private Data Length Not Set to Zero",
    description="The private data length is set to one but the offset is zero. This test case also fails for another reason: the offset/length creates an overlap with the header block.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
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

writeTest(
    identifier="blocks-private-absent-002",
    title="Private Data Offset Not Set to Zero",
    description="The private data length is set to zero but the offset is set to the end of the file.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-zerometaprivate",
    data=makePrivateDataZeroData2()
)

# ---------------------------------------------
# File Structure: Data Blocks: Metadata Padding
# ---------------------------------------------

# padding after metadata but no private data

def makeMetadataPadding():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    metadata = packTestMetadata(metadata)
    paddingLength = calcPaddingLength(len(metadata))
    assert paddingLength
    header["length"] += paddingLength
    metadata += "\0" * paddingLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + metadata
    return data

writeTest(
    identifier="blocks-metadata-padding-001",
    title="Metadata Has Unnecessary Padding",
    description="The metadata block is padded to a four-byte boundary but there is no private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-metadata-noprivatepad",
    data=makeMetadataPadding()
)

# -------------------------------------
# File Structure: Data Blocks: Ordering
# -------------------------------------

# font data after metadata

def makeDataBlockOrdering1():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    # move the metadata
    metadataStart = header["metaOffset"] = directory[0]["offset"]
    metadataLength = header["metaLength"]
    # pad
    metadata, compMetadata = metadata
    compMetadata += "\0" * calcPaddingLength(len(compMetadata))
    metadata = (metadata, compMetadata)
    # offset tables
    offset = metadataStart + metadataLength + calcPaddingLength(metadataLength)
    for entry in directory:
        entry["offset"] = offset
        offset += entry["compLength"] + calcPaddingLength(entry["compLength"])
    # pack
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    # done
    return data

writeTest(
    identifier="blocks-ordering-001",
    title="Table Data After Metadata",
    description="The table data block is stored after the metadata block.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-afterdirectory",
    data=makeDataBlockOrdering1()
)

# font data after private

def makeDataBlockOrdering2():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    # move the private data
    privateStart = header["privOffset"] = directory[0]["offset"]
    privateLength = header["privLength"]
    # pad
    assert calcPaddingLength(privateLength) == 0
    # offset tables
    offset = privateStart + privateLength
    for entry in directory:
        entry["offset"] = offset
        offset += entry["compLength"] + calcPaddingLength(entry["compLength"])
    # pack
    data = packTestHeader(header) + packTestDirectory(directory) + packTestPrivateData(privateData) + packTestTableData(directory, tableData)
    # done
    return data

writeTest(
    identifier="blocks-ordering-002",
    title="Table Data After Private Data",
    description="The table data block is stored after the private data block.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-afterdirectory",
    data=makeDataBlockOrdering2()
)

# metadata after private

def makeDataBlockOrdering3():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    # move the metadata
    header["privOffset"] = header["metaOffset"]
    privateLength = header["privLength"]
    header["metaOffset"] = header["privOffset"] + privateLength
    # remove padding
    assert calcPaddingLength(privateLength) == 0
    metaPaddingLength = calcPaddingLength(header["metaLength"])
    if metaPaddingLength:
        header["length"] -= metaPaddingLength
        metadata, compMetadata = metadata
        compMetadata = compMetadata[:-metaPaddingLength]
        metadata = (metadata, compMetadata)
    # pack
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestPrivateData(privateData) + packTestMetadata(metadata)
    # done
    return data

writeTest(
    identifier="blocks-ordering-003",
    title="Metadata After Private Data",
    description="The metadata block is stored after the private data block.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#metadata-afterfonttable",
    data=makeDataBlockOrdering3()
)

writeTest(
    identifier="blocks-ordering-004",
    title="Private Data Before Metadata",
    description="The private data block is stored before the metadata block.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#private-last",
    data=makeDataBlockOrdering3()
)

# ------------------------------------------------
# File Structure: Table Directory: 4-Byte Boundary
# ------------------------------------------------

writeTest(
    identifier="directory-4-byte-001",
    title=makeTableData4Byte1Title,
    description=makeTableData4Byte1Description,
    credits=makeTableData4Byte1Credits,
    valid=False,
    specLink="#conform-tablesize-longword",
    data=makeTableData4Byte1()
)

# final table is not padded

writeTest(
    identifier="directory-4-byte-002",
    title=makeTableData4Byte2Title,
    description=makeTableData4Byte2Description,
    credits=makeTableData4Byte2Credits,
    valid=False,
    specLink="#conform-tablesize-longword",
    data=makeTableData4Byte2()
)

# table is padded with something other than null bytes

def makeTableData4Byte3():
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

writeTest(
    identifier="directory-4-byte-003",
    title="Font Table Data Padded With Non-Null",
    description="Table data is padded with \\01 instead of \\00.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-tablesize-longword",
    data=makeTableData4Byte3()
)

# -----------------------------------------
# File Structure: Table Directory: Overlaps
# -----------------------------------------

# offset after end of file

writeTest(
    identifier="directory-overlaps-001",
    title=makeTableDataByteRange1Title,
    description=makeTableDataByteRange1Description,
    credits=makeTableDataByteRange1Credits,
    valid=False,
    specLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange1()
)

# offset + length goes past the end of the file

writeTest(
    identifier="directory-overlaps-002",
    title=makeTableDataByteRange2Title,
    description=makeTableDataByteRange2Description,
    credits=makeTableDataByteRange2Credits,
    valid=False,
    specLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange2()
)

# overlaps metadata

writeTest(
    identifier="directory-overlaps-003",
    title=makeTableDataByteRange3Title,
    description=makeTableDataByteRange3Description,
    credits=makeTableDataByteRange3Credits,
    valid=False,
    specLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange3()
)

# overlaps private data

writeTest(
    identifier="directory-overlaps-004",
    title=makeTableDataByteRange4Title,
    description=makeTableDataByteRange4Description,
    credits=makeTableDataByteRange4Credits,
    valid=False,
    specLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange4()
)

# two tables overlap

writeTest(
    identifier="directory-overlaps-005",
    title=makeTableDataByteRange5Title,
    description=makeTableDataByteRange5Description,
    credits=makeTableDataByteRange5Credits,
    valid=False,
    specLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange5()
)

# ------------------------------------------------
# File Structure: Table Directory: Extraneous Data
# ------------------------------------------------

# between tables

writeTest(
    identifier="directory-extraneous-data-001",
    title=makeTableDataExtraneousData1Title,
    description=makeTableDataExtraneousData1Description,
    credits=makeTableDataExtraneousData1Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeTableDataExtraneousData1()
)

# -------------------------------------------
# File Structure: Table Directory: compLength
# -------------------------------------------

# some tables have a compressed length that is longer than the original length

writeTest(
    identifier="directory-compLength-001",
    title=makeTableDataCompressionLength1Title,
    description=makeTableDataCompressionLength1Description,
    credits=makeTableDataCompressionLength1Credits,
    valid=False,
    specLink="#conform-compressedlarger",
    data=makeTableDataCompressionLength1()
)

# -------------------------------------------
# File Structure: Table Directory: origLength
# -------------------------------------------

# one table has an origLength that is less than the decompressed length

writeTest(
    identifier="directory-origLength-001",
    title=makeTableDataOriginalLength1Title,
    description=makeTableDataOriginalLength1Description,
    credits=makeTableDataOriginalLength1Credits,
    valid=False,
    specLink="#conform-origLength",
    data=makeTableDataOriginalLength1()
)

# one table has an origLength that is greater than the decompressed length

writeTest(
    identifier="directory-origLength-002",
    title=makeTableDataOriginalLength2Title,
    description=makeTableDataOriginalLength2Description,
    credits=makeTableDataOriginalLength2Credits,
    valid=False,
    specLink="#conform-origLength",
    data=makeTableDataOriginalLength2()
)

# ---------------------------------------------
# File Structure: Table Directory: origCheckSum
# ---------------------------------------------

# bad checksum

def makeTableDirectoryCheckSum1():
    header, directory, tableData = defaultTestData()
    modifiedTable = False
    for entry in directory:
        if entry["tag"] != "CFF ":
            continue
        assert entry["origChecksum"] != 0
        entry["origChecksum"] = 0
        modifiedTable = True
        break
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData)
    return data

writeTest(
    identifier="directory-origCheckSum-001",
    title="Font Table Directory Contains Invalid Original CheckSum",
    description="The checksum for the CFF table is set to 0.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-checksumvalidate",
    data=makeTableDirectoryCheckSum1()
)

# bad head checksum

def makeTableDirectoryCheckSum2():
    header, directory, tableData = defaultTestData()
    origData, compData = tableData["head"]
    assert origData == compData
    origValue = origData[8:12]
    newValue = struct.pack(">L", 0)
    assert origValue != newValue
    newData = origData[:8] + newValue + origData[12:]
    tableData["head"] = (newData, newData)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData, calcCheckSum=False)
    return data

writeTest(
    identifier="directory-origCheckSum-002",
    title="Font head Table Incorrect CheckSum Adjustment",
    description="The head table checksum adjustment is set to 0.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-checksumvalidate",
    data=makeTableDirectoryCheckSum2()
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

writeTest(
    identifier="directory-ascending-001",
    title="Font Table Directory Not In Ascending Order",
    description="The tables in the directory are in descending order.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-ascending",
    data=makeTableDirectoryAscending1()
)


# ---------------------------------------
# File Structure: Table Data: Compression
# ---------------------------------------

# no tables compressed

writeTest(
    identifier="tabledata-compression-001",
    title=makeTableCompressionTest1Title,
    description=makeTableCompressionTest1Description,
    credits=makeTableCompressionTest1Credits,
    valid=True,
    specLink="#conform-mustuncompress",
    data=makeTableCompressionTest1()
)

# all possible tables are compressed

writeTest(
    identifier="tabledata-compression-002",
    title=makeTableCompressionTest2Title,
    description=makeTableCompressionTest2Description,
    credits=makeTableCompressionTest2Credits,
    valid=True,
    specLink="#conform-mustuncompress",
    data=makeTableCompressionTest2()
)

# not all possible tables are compressed

writeTest(
    identifier="tabledata-compression-003",
    title=makeTableCompressionTest3Title,
    description=makeTableCompressionTest3Description,
    credits=makeTableCompressionTest3Credits,
    valid=True,
    specLink="#conform-mustuncompress",
    data=makeTableCompressionTest3()
)

# varying compression levels

writeTest(
    identifier="tabledata-compression-004",
    title=makeTableCompressionTest4Title,
    description=makeTableCompressionTest4Description,
    credits=makeTableCompressionTest4Credits,
    valid=True,
    specLink="#conform-mustuncompress",
    data=makeTableCompressionTest4()
)

# ----------------------------------------------
# File Structure: Table Data: Compression Format
# ----------------------------------------------

# compression incompatible with zlib

writeTest(
    identifier="tabledata-zlib-001",
    title=makeTableZlibCompressionTest1Title,
    description=makeTableZlibCompressionTest1Description,
    credits=makeTableZlibCompressionTest1Credits,
    valid=False,
    specLink="#conform-mustzlib",
    data=makeTableZlibCompressionTest1()
)

# -----------------------------
# Metadata Display: Compression
# -----------------------------

writeTest(
    identifier="metadata-compression-001",
    title=makeMetadataCompression1Title,
    description=makeMetadataCompression1Description,
    credits=makeMetadataCompression1Credits,
    valid=False,
    data=makeMetadataCompression1(),
    specLink="#conform-metadata-alwayscompress"
)

# --------------------------------
# Metadata Display: metaOrigLength
# --------------------------------

# <

writeTest(
    identifier="metadata-metaOrigLength-001",
    title=makeMetaOrigLengthTest1Title,
    description=makeMetaOrigLengthTest1Description,
    credits=makeMetaOrigLengthTest1Credits,
    valid=False,
    specLink="#conform-metaOrigLength",
    data=makeMetaOrigLengthTest1()
)

# >

writeTest(
    identifier="metadata-metaOrigLength-002",
    title=makeMetaOrigLengthTest2Title,
    description=makeMetaOrigLengthTest2Description,
    credits=makeMetaOrigLengthTest2Credits,
    valid=False,
    specLink="#conform-metaOrigLength",
    data=makeMetaOrigLengthTest2()
)

# -----------------------------
# Metadata Display: Well-Formed
# -----------------------------

# <

writeMetadataTest(
    identifier="metadata-well-formed-001",
    specLink="#conform-metaOrigLength",
    valid=False,
)

# &

writeMetadataTest(
    identifier="metadata-well-formed-002",
    specLink="#conform-metaOrigLength",
    valid=False,
)

# mismatched elements

writeMetadataTest(
    identifier="metadata-well-formed-003",
    specLink="#conform-metaOrigLength",
    valid=False,
)

# unclosed element

writeMetadataTest(
    identifier="metadata-well-formed-004",
    specLink="#conform-metaOrigLength",
    valid=False,
)

# case mismatch

writeMetadataTest(
    identifier="metadata-well-formed-005",
    specLink="#conform-metaOrigLength",
    valid=False,
)

# more than one root

writeMetadataTest(
    identifier="metadata-well-formed-006",
    specLink="#conform-metaOrigLength",
    valid=False,
)

# unknown encoding

writeMetadataTest(
    identifier="metadata-well-formed-007",
    specLink="#conform-metaOrigLength",
    valid=False,
)

# --------------------------
# Metadata Display: Encoding
# --------------------------

# UTF-8

writeMetadataTest(
    identifier="metadata-encoding-001",
    valid=True,
)

# Invalid

writeMetadataTest(
    identifier="metadata-encoding-002",
    valid=False,
)

writeMetadataTest(
    identifier="metadata-encoding-003",
    specLink="#conform-metaOrigLength",
    valid=False,
)

# -------------------------------------------
# Metadata Display: Schema Validity: metadata
# -------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-metadata-001",
    valid=True,
)

# top element not metadata

writeMetadataTest(
    identifier="metadata-schema-metadata-002",
    valid=False,
)

# missing version

writeMetadataTest(
    identifier="metadata-schema-metadata-003",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# invalid version

writeMetadataTest(
    identifier="metadata-schema-metadata-004",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-metadata-005",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown element

writeMetadataTest(
    identifier="metadata-schema-metadata-006",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-uniqueid-001",
    valid=True,
)

# does not exist

writeMetadataTest(
    identifier="metadata-schema-uniqueid-002",
    valid=True,
)

# duplicate

writeMetadataTest(
    identifier="metadata-schema-uniqueid-003",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# missing id attribute

writeMetadataTest(
    identifier="metadata-schema-uniqueid-004",
    specLink="#conform-metadata-id-required",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-uniqueid-005",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown child

writeMetadataTest(
    identifier="metadata-schema-uniqueid-006",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-uniqueid-007",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# -----------------------------------------
# Metadata Display: Schema Validity: vendor
# -----------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-vendor-001",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-vendor-002",
    valid=True,
)

# does not exist

writeMetadataTest(
    identifier="metadata-schema-vendor-003",
    valid=True,
)

# duplicate

writeMetadataTest(
    identifier="metadata-schema-vendor-004",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# missing name attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-005",
    specLink="#conform-metadata-vendor-required",
    valid=False,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-006",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-vendor-007",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-vendor-008",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-009",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-010",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown child

writeMetadataTest(
    identifier="metadata-schema-vendor-011",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-vendor-012",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# ------------------------------------------
# Metadata Display: Schema Validity: credits
# ------------------------------------------

# valid - single credit element

writeMetadataTest(
    identifier="metadata-schema-credits-001",
    valid=True,
)

# valid - multiple credit elements

writeMetadataTest(
    identifier="metadata-schema-credits-002",
    valid=True,
)

# missing credit element

writeMetadataTest(
    identifier="metadata-schema-credits-003",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-credits-004",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown element

writeMetadataTest(
    identifier="metadata-schema-credits-005",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-credits-006",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# multiple credits

writeMetadataTest(
    identifier="metadata-schema-credits-007",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# -----------------------------------------
# Metadata Display: Schema Validity: credit
# -----------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-credit-001",
    valid=True,
)

# valid no url

writeMetadataTest(
    identifier="metadata-schema-credit-002",
    valid=True,
)

# valid no role

writeMetadataTest(
    identifier="metadata-schema-credit-003",
    valid=True,
)

# no name

writeMetadataTest(
    identifier="metadata-schema-credit-004",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-credit-005",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-credit-006",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-credit-007",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-credit-008",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-credit-009",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-credit-010",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-credit-011",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# ----------------------------------------------
# Metadata Display: Schema Validity: description
# ----------------------------------------------

# valid with url

writeMetadataTest(
    identifier="metadata-schema-description-001",
    valid=True,
)

# valid without url

writeMetadataTest(
    identifier="metadata-schema-description-002",
    valid=True,
)

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-description-003",
    valid=True,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-description-004",
    valid=True,
)

# valid one text element with language using lang

writeMetadataTest(
    identifier="metadata-schema-description-005",
    valid=True,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-description-006",
    valid=True,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-description-007",
    valid=True,
)

# more than one description

writeMetadataTest(
    identifier="metadata-schema-description-008",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-description-009",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-description-010",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-description-011",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-description-012",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-description-013",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-014",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-015",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-description-016",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-description-017",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-description-018",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# one div

writeMetadataTest(
    identifier="metadata-schema-description-019",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# two div

writeMetadataTest(
    identifier="metadata-schema-description-020",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# nested div

writeMetadataTest(
    identifier="metadata-schema-description-021",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# div with dir

writeMetadataTest(
    identifier="metadata-schema-description-022",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-023",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-024",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# div with class

writeMetadataTest(
    identifier="metadata-schema-description-025",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# one span

writeMetadataTest(
    identifier="metadata-schema-description-026",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# two span

writeMetadataTest(
    identifier="metadata-schema-description-027",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# nested span

writeMetadataTest(
    identifier="metadata-schema-description-028",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# span with dir

writeMetadataTest(
    identifier="metadata-schema-description-029",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-030",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-031",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# span with class

writeMetadataTest(
    identifier="metadata-schema-description-032",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# ------------------------------------------
# Metadata Display: Schema Validity: license
# ------------------------------------------

# valid with url and license

writeMetadataTest(
    identifier="metadata-schema-license-001",
    valid=True,
)

# valid no url

writeMetadataTest(
    identifier="metadata-schema-license-002",
    valid=True,
)

# valid no id

writeMetadataTest(
    identifier="metadata-schema-license-003",
    valid=True,
)

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-license-004",
    valid=True,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-license-005",
    valid=True,
)

# valid one text element with language using lang

writeMetadataTest(
    identifier="metadata-schema-license-006",
    valid=True,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-license-007",
    valid=True,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-license-008",
    valid=True,
)

# more than one license

writeMetadataTest(
    identifier="metadata-schema-license-009",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-license-010",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-license-011",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-license-012",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-license-013",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element dir attribute

writeMetadataTest(
    identifier="metadata-schema-license-014",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-015",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-016",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element class attribute

writeMetadataTest(
    identifier="metadata-schema-license-017",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-license-018",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-license-019",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# one div

writeMetadataTest(
    identifier="metadata-schema-license-020",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# two div

writeMetadataTest(
    identifier="metadata-schema-license-021",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# nested div

writeMetadataTest(
    identifier="metadata-schema-license-022",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# div with dir

writeMetadataTest(
    identifier="metadata-schema-license-023",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-024",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-025",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# div with class

writeMetadataTest(
    identifier="metadata-schema-license-026",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# one span

writeMetadataTest(
    identifier="metadata-schema-license-027",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# two span

writeMetadataTest(
    identifier="metadata-schema-license-028",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# nested span

writeMetadataTest(
    identifier="metadata-schema-license-029",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# span with dir

writeMetadataTest(
    identifier="metadata-schema-license-030",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-031",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-032",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# span with class

writeMetadataTest(
    identifier="metadata-schema-license-033",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# --------------------------------------------
# Metadata Display: Schema Validity: copyright
# --------------------------------------------

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-copyright-001",
    valid=True,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-copyright-002",
    valid=True,
)

# valid one text element with language using lang

writeMetadataTest(
    identifier="metadata-schema-copyright-003",
    valid=True,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-copyright-004",
    valid=True,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-copyright-005",
    valid=True,
)

# more than one copyright

writeMetadataTest(
    identifier="metadata-schema-copyright-006",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-copyright-007",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-008",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-copyright-009",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-copyright-010",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element with dir attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-011",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-012",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-013",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element with class attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-014",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-015",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-copyright-016",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# one div

writeMetadataTest(
    identifier="metadata-schema-copyright-017",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# two div

writeMetadataTest(
    identifier="metadata-schema-copyright-018",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# nested div

writeMetadataTest(
    identifier="metadata-schema-copyright-019",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# div with dir

writeMetadataTest(
    identifier="metadata-schema-copyright-020",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-021",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-022",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# div with class

writeMetadataTest(
    identifier="metadata-schema-copyright-023",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# one span

writeMetadataTest(
    identifier="metadata-schema-copyright-024",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# two span

writeMetadataTest(
    identifier="metadata-schema-copyright-025",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# nested span

writeMetadataTest(
    identifier="metadata-schema-copyright-026",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# span with dir

writeMetadataTest(
    identifier="metadata-schema-copyright-027",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-028",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-029",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# span with class

writeMetadataTest(
    identifier="metadata-schema-copyright-030",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# --------------------------------------------
# Metadata Display: Schema Validity: trademark
# --------------------------------------------

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-trademark-001",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-trademark-002",
    valid=True,
)

# valid one text element with language using lang

writeMetadataTest(
    identifier="metadata-schema-trademark-003",
    valid=True,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-trademark-004",
    valid=True,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-trademark-005",
    valid=True,
)

# more than one trademark

writeMetadataTest(
    identifier="metadata-schema-trademark-006",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-trademark-007",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-008",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-trademark-009",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-trademark-010",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element with dir attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-011",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-012",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-013",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element with class attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-014",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-015",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-trademark-016",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# one div

writeMetadataTest(
    identifier="metadata-schema-trademark-017",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# two div

writeMetadataTest(
    identifier="metadata-schema-trademark-018",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# nested div

writeMetadataTest(
    identifier="metadata-schema-trademark-019",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# div with dir

writeMetadataTest(
    identifier="metadata-schema-trademark-020",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-021",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-022",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# div with class

writeMetadataTest(
    identifier="metadata-schema-trademark-023",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# one span

writeMetadataTest(
    identifier="metadata-schema-trademark-024",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# two span

writeMetadataTest(
    identifier="metadata-schema-trademark-025",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# nested span

writeMetadataTest(
    identifier="metadata-schema-trademark-026",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# span with dir

writeMetadataTest(
    identifier="metadata-schema-trademark-027",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-028",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-029",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# span with class

writeMetadataTest(
    identifier="metadata-schema-trademark-030",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-licensee-001",
    valid=True,
)

# duplicate

writeMetadataTest(
    identifier="metadata-schema-licensee-002",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# missing name

writeMetadataTest(
    identifier="metadata-schema-licensee-003",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-licensee-004",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-licensee-005",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-licensee-006",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-licensee-007",
    specLink="#conform-metadata-schemavalid",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-licensee-008",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-licensee-009",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-licensee-010",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# --------------------------------------------
# Metadata Display: Schema Validity: extension
# --------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-extension-001",
    valid=True,
)

# valid two extensions

writeMetadataTest(
    identifier="metadata-schema-extension-002",
    valid=True,
)

# valid no id

writeMetadataTest(
    identifier="metadata-schema-extension-003",
    valid=True,
)

# valid no name

writeMetadataTest(
    identifier="metadata-schema-extension-004",
    valid=True,
)

# valid one untagged name one tagged name

writeMetadataTest(
    identifier="metadata-schema-extension-005",
    valid=True,
)

# valid two tagged names

writeMetadataTest(
    identifier="metadata-schema-extension-006",
    valid=True,
)

# valid more than one item

writeMetadataTest(
    identifier="metadata-schema-extension-007",
    valid=True,
)

# no item

writeMetadataTest(
    identifier="metadata-schema-extension-008",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-009",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown child

writeMetadataTest(
    identifier="metadata-schema-extension-010",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-extension-011",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - name
# ---------------------------------------------------

# valid no lang

writeMetadataTest(
    identifier="metadata-schema-extension-012",
    valid=True,
)

# valid xml:lang

writeMetadataTest(
    identifier="metadata-schema-extension-013",
    valid=True,
)

# valid lang

writeMetadataTest(
    identifier="metadata-schema-extension-014",
    valid=True,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-extension-015",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-016",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-017",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-extension-018",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-019",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-extension-020",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - item
# ---------------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-extension-021",
    valid=True,
)

# valid multiple languages

writeMetadataTest(
    identifier="metadata-schema-extension-022",
    valid=True,
)

# valid no id

writeMetadataTest(
    identifier="metadata-schema-extension-023",
    valid=True,
)

# valid name no tag and tagged

writeMetadataTest(
    identifier="metadata-schema-extension-024",
    valid=True,
)

# valid name two tagged

writeMetadataTest(
    identifier="metadata-schema-extension-025",
    valid=True,
)

# valid value no tag and tagged

writeMetadataTest(
    identifier="metadata-schema-extension-026",
    valid=True,
)

# valid value two tagged

writeMetadataTest(
    identifier="metadata-schema-extension-027",
    valid=True,
)

# no name

writeMetadataTest(
    identifier="metadata-schema-extension-028",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# no value

writeMetadataTest(
    identifier="metadata-schema-extension-029",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-030",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-extension-031",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-extension-032",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# ----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - name
# ----------------------------------------------------------

# valid no lang

writeMetadataTest(
    identifier="metadata-schema-extension-033",
    valid=True,
)

# valid xml:lang

writeMetadataTest(
    identifier="metadata-schema-extension-034",
    valid=True,
)

# valid lang

writeMetadataTest(
    identifier="metadata-schema-extension-035",
    valid=True,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-extension-036",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-037",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-038",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-extension-039",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-040",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-extension-041",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# -----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - value
# -----------------------------------------------------------

# valid no lang

writeMetadataTest(
    identifier="metadata-schema-extension-042",
    valid=True,
)

# valid xml:lang

writeMetadataTest(
    identifier="metadata-schema-extension-043",
    valid=True,
)

# valid lang

writeMetadataTest(
    identifier="metadata-schema-extension-044",
    valid=True,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-extension-045",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-046",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-047",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-extension-048",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-049",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-extension-050",
    specLink="#conform-metadata-schemavalid",
    valid=False,
)

# ------------------------------------
# File Structure: Private Data: 4-Byte
# ------------------------------------

# private data not on 4-byte boundary

def makePrivateData4Byte1():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    paddingLength = calcPaddingLength(header["metaLength"])
    assert paddingLength > 0
    header["length"] -= paddingLength
    header["privOffset"] -= paddingLength
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata)
    data += packTestPrivateData(privateData)
    return data

writeTest(
    identifier="privatedata-4-byte-001",
    title="Private Data Does Not Begin of 4-Byte Boundary",
    description="The private data does not begin on a four byte boundary because the metadata is not padded. This will fail for another reason: the calculated length (header length + directory length + entry lengths + metadata length + private data length) will not match the stored length in the header.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-private-padalign",
    data=makePrivateData4Byte1()
)

# metadata not padded with null bytes

def makePrivateData4Byte2():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    paddingLength = calcPaddingLength(header["metaLength"])
    assert paddingLength > 0
    metadata, compMetadata = metadata
    compMetadata = compMetadata[:-paddingLength] + ("\x01" * paddingLength)
    metadata = (metadata, compMetadata)
    data = packTestHeader(header) + packTestDirectory(directory) + packTestTableData(directory, tableData) + packTestMetadata(metadata) + packTestPrivateData(privateData)
    return data

writeTest(
    identifier="privatedata-4-byte-002",
    title="Padding Between Metadata and Private Data is Non-Null",
    description="Metadata is padded with \\01 instead of \\00.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-private-padalign",
    data=makePrivateData4Byte2()
)

# ------------------
# Generate the Index
# ------------------

print "Compiling index..."

testGroups = []

for tag, title, url in groupDefinitions:
    group = dict(title=title, url=url, testCases=testRegistry[tag])
    testGroups.append(group)

generateFormatIndexHTML(directory=formatTestDirectory, testCases=testGroups)

# -----------------------
# Check for Unknown Files
# -----------------------

woffPattern = os.path.join(formatTestDirectory, "*.woff")
filesOnDisk = glob.glob(woffPattern)

for path in filesOnDisk:
    identifier = os.path.basename(path)
    identifier = identifier.split(".")[0]
    if identifier not in registeredIdentifiers:
        print "Unknown file:", path