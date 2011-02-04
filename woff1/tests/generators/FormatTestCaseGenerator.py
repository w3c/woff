import os
import shutil
import glob
from xml.etree.ElementTree import ElementTree, Element, SubElement
import sstruct
from testCaseGeneratorLib.woff import packTestHeader, packTestDirectory, packTestTableData, packTestMetadata, packTestPrivateData
from testCaseGeneratorLib.defaultData import defaultTestData, testDataWOFFMetadata, testDataWOFFPrivateData
from testCaseGeneratorLib.paths import resourcesDirectory, formatDirectory
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

# ----------------------
# Start Index Generation
# ----------------------

# start the main element
indexRoot = Element("testcases")

# This function was taken from: http://effbot.org/zone/element-lib.htm
# License information found here: http://effbot.org/zone/copyright.htm
# "Unless otherwise noted, source code can be be used freely.
# Examples, test scripts and other short code fragments can be
# considered as being in the public domain."
def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# -----------------
# Test Case Writing
# -----------------

registeredIdentifiers = set()

def writeTest(identifier, title, description, data, specLink=None, credits=[], valid=False, failPoint=None):
    print "Compiling %s..." % identifier
    assert identifier not in registeredIdentifiers, "Duplicate identifier! %s" % identifier
    registeredIdentifiers.add(identifier)

    # generate the WOFF
    woffPath = os.path.join(formatDirectory, identifier) + ".woff"
    f = open(woffPath, "wb")
    f.write(data)
    f.close()

    # make the test case element
    caseElement = SubElement(indexRoot, "testcase")
    # title
    titleElement = SubElement(caseElement, "title")
    titleElement.text = title
    # description
    descriptionElement = SubElement(caseElement, "description")
    descriptionElement.text = description
    # link
    if specLink is None:
        specLink = specificationURL
    else:
        specLink = specificationURL + specLink
    SubElement(caseElement, "specification", href=specLink)
    # credits
    for credit in credits:
        SubElement(caseElement, "credit", **credit)
    # validity
    if valid:
        valid = "true"
    else:
        valid = "false"
    SubElement(caseElement, "valid", value=valid)
    # failure point
    if failPoint:
        for location in failPoint.split(" "):
            SubElement(caseElement, "failpoint", location=location)

def writeMetadataTest(identifier, title=None, description=None, credits=[], specLink=None, valid=False, metadata=None):
    """
    This is a convenience functon that eliminates the need to make a complete
    WOFF when only the metadata is being tested.
    """
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
    specLink="#conform-nonmagicnumber-reject",
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
    specLink="#conform-totalsize-longword-reject",
    data=makeHeaderInvalidTotalSfntSize1()
)

writeTest(
    identifier="header-totalSfntSize-002",
    title=makeHeaderInvalidTotalSfntSize2Title,
    description=makeHeaderInvalidTotalSfntSize2Description,
    credits=makeHeaderInvalidTotalSfntSize2Credits,
    valid=False,
    specLink="#conform-totalsize-longword-reject",
    data=makeHeaderInvalidTotalSfntSize2()
)

writeTest(
    identifier="header-totalSfntSize-003",
    title=makeHeaderInvalidTotalSfntSize3Title,
    description=makeHeaderInvalidTotalSfntSize3Description,
    credits=makeHeaderInvalidTotalSfntSize3Credits,
    valid=False,
    specLink="#conform-totalsize-longword-reject",
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
    specLink="#conform-reserved-reject",
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
    specLink="#conform-extraneous-reject",
    data=makeExtraneousData1()
)

# between tables

writeTest(
    identifier="blocks-extraneous-data-002",
    title=makeExtraneousData2Title,
    description=makeExtraneousData2Description,
    credits=makeExtraneousData2Credits,
    valid=False,
    specLink="#conform-extraneous-reject",
    data=makeExtraneousData2()
)

# after table data with no metadata or private data

writeTest(
    identifier="blocks-extraneous-data-003",
    title=makeExtraneousData3Title,
    description=makeExtraneousData3Description,
    credits=makeExtraneousData3Credits,
    valid=False,
    specLink="#conform-extraneous-reject",
    data=makeExtraneousData3()
)

# between tabledata and metadata

writeTest(
    identifier="blocks-extraneous-data-004",
    title=makeExtraneousData4Title,
    description=makeExtraneousData4Description,
    credits=makeExtraneousData4Credits,
    valid=False,
    specLink="#conform-extraneous-reject",
    data=makeExtraneousData4()
)

# between tabledata and private data

writeTest(
    identifier="blocks-extraneous-data-005",
    title=makeExtraneousData5Title,
    description=makeExtraneousData5Description,
    credits=makeExtraneousData5Credits,
    valid=False,
    specLink="#conform-extraneous-reject",
    data=makeExtraneousData5()
)

# between metadata and private data

writeTest(
    identifier="blocks-extraneous-data-006",
    title=makeExtraneousData6Title,
    description=makeExtraneousData6Description,
    credits=makeExtraneousData6Credits,
    valid=False,
    specLink="#conform-extraneous-reject",
    data=makeExtraneousData6()
)

# after metadata with no private data

writeTest(
    identifier="blocks-extraneous-data-007",
    title=makeExtraneousData7Title,
    description=makeExtraneousData7Description,
    credits=makeExtraneousData7Credits,
    valid=False,
    specLink="#conform-extraneous-reject",
    data=makeExtraneousData7()
)

# after private data

writeTest(
    identifier="blocks-extraneous-data-008",
    title=makeExtraneousData8Title,
    description=makeExtraneousData8Description,
    credits=makeExtraneousData8Credits,
    valid=False,
    specLink="#conform-extraneous-reject",
    data=makeExtraneousData8()
)

# -------------------------------------
# File Structure: Data Blocks: Overlaps
# -------------------------------------

# two tables overlap

writeTest(
    identifier="blocks-overlap-001",
    title=makeOverlappingData1Title,
    description=makeOverlappingData1Description,
    credits=makeOverlappingData1Credits,
    valid=False,
    specLink="#conform-overlap-reject",
    data=makeOverlappingData1()
)

# metadata overlaps the table data

writeTest(
    identifier="blocks-overlap-002",
    title=makeOverlappingData2Title,
    description=makeOverlappingData2Description,
    credits=makeOverlappingData2Credits,
    valid=False,
    specLink="#conform-overlap-reject",
    data=makeOverlappingData2()
)

# private data overlaps the table data

writeTest(
    identifier="blocks-overlap-003",
    title=makeOverlappingData3Title,
    description=makeOverlappingData3Description,
    credits=makeOverlappingData3Credits,
    valid=False,
    specLink="#conform-overlap-reject",
    data=makeOverlappingData3()
)

# private data overlaps the metadata

writeTest(
    identifier="blocks-overlap-004",
    title=makeOverlappingData4Title,
    description=makeOverlappingData4Description,
    credits=makeOverlappingData4Credits,
    valid=False,
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
    title=metadataWellFormed1Title,
    description=metadataWellFormed1Description,
    credits=metadataWellFormed1Credits,
    specLink="#conform-invalid-mustignore",
    valid=False,
    metadata=metadataWellFormed1Metadata,
)

# &

writeMetadataTest(
    identifier="metadata-well-formed-002",
    title=metadataWellFormed2Title,
    description=metadataWellFormed2Description,
    credits=metadataWellFormed2Credits,
    specLink="#conform-invalid-mustignore",
    valid=False,
    metadata=metadataWellFormed2Metadata,
)

# mismatched elements

writeMetadataTest(
    identifier="metadata-well-formed-003",
    title=metadataWellFormed3Title,
    description=metadataWellFormed3Description,
    credits=metadataWellFormed3Credits,
    specLink="#conform-invalid-mustignore",
    valid=False,
    metadata=metadataWellFormed3Metadata,
)

# unclosed element

writeMetadataTest(
    identifier="metadata-well-formed-004",
    title=metadataWellFormed4Title,
    description=metadataWellFormed4Description,
    credits=metadataWellFormed4Credits,
    specLink="#conform-invalid-mustignore",
    valid=False,
    metadata=metadataWellFormed4Metadata,
)

# case mismatch

writeMetadataTest(
    identifier="metadata-well-formed-005",
    title=metadataWellFormed5Title,
    description=metadataWellFormed5Description,
    credits=metadataWellFormed5Credits,
    specLink="#conform-invalid-mustignore",
    valid=False,
    metadata=metadataWellFormed5Metadata,
)

# more than one root

writeMetadataTest(
    identifier="metadata-well-formed-006",
    title=metadataWellFormed6Title,
    description=metadataWellFormed6Description,
    credits=metadataWellFormed6Credits,
    specLink="#conform-invalid-mustignore",
    valid=False,
    metadata=metadataWellFormed6Metadata,
)

# unknown encoding

writeMetadataTest(
    identifier="metadata-well-formed-007",
    title=metadataWellFormed7Title,
    description=metadataWellFormed7Description,
    credits=metadataWellFormed7Credits,
    specLink="#conform-invalid-mustignore",
    valid=False,
    metadata=metadataWellFormed7Metadata,
)

# --------------------------
# Metadata Display: Encoding
# --------------------------

# UTF-8

writeMetadataTest(
    identifier="metadata-encoding-001",
    title=metadataEncoding1Title,
    description=metadataEncoding1Description,
    credits=metadataEncoding1Credits,
    valid=True,
    metadata=metadataEncoding1Metadata,
)

# UTF-16

writeMetadataTest(
    identifier="metadata-encoding-002",
    title=metadataEncoding2Title,
    description=metadataEncoding2Description,
    credits=metadataEncoding2Credits,
    valid=True,
    metadata=metadataEncoding2Metadata,
)

# Invalid

writeMetadataTest(
    identifier="metadata-encoding-003",
    title=metadataEncoding3Title,
    description=metadataEncoding3Description,
    credits=metadataEncoding3Credits,
    specLink="#conform-invalid-mustignore",
    valid=False,
    metadata=metadataEncoding3Metadata,
)

# -------------------------------------------
# Metadata Display: Schema Validity: metadata
# -------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-metadata-001",
    title=metadataSchemaMetadata1Title,
    description=metadataSchemaMetadata1Description,
    credits=metadataSchemaMetadata1Credits,
    valid=True,
    metadata=metadataSchemaMetadata1Metadata,
)

# missing version

writeMetadataTest(
    identifier="metadata-schema-metadata-002",
    title=metadataSchemaMetadata2Title,
    description=metadataSchemaMetadata2Description,
    credits=metadataSchemaMetadata2Credits,
    valid=False,
    metadata=metadataSchemaMetadata2Metadata,
)

# invalid version

writeMetadataTest(
    identifier="metadata-schema-metadata-003",
    title=metadataSchemaMetadata3Title,
    description=metadataSchemaMetadata3Description,
    credits=metadataSchemaMetadata3Credits,
    valid=False,
    metadata=metadataSchemaMetadata3Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-metadata-004",
    title=metadataSchemaMetadata4Title,
    description=metadataSchemaMetadata4Description,
    credits=metadataSchemaMetadata4Credits,
    valid=False,
    metadata=metadataSchemaMetadata4Metadata,
)

# unknown element

writeMetadataTest(
    identifier="metadata-schema-metadata-005",
    title=metadataSchemaMetadata5Title,
    description=metadataSchemaMetadata5Description,
    credits=metadataSchemaMetadata5Credits,
    valid=False,
    metadata=metadataSchemaMetadata5Metadata,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-uniqueid-001",
    title=metadataSchemaUniqueid1Title,
    description=metadataSchemaUniqueid1Description,
    credits=metadataSchemaUniqueid1Credits,
    valid=True,
    metadata=metadataSchemaUniqueid1Metadata,
)

# does not exist

writeMetadataTest(
    identifier="metadata-schema-uniqueid-002",
    title=metadataSchemaUniqueid2Title,
    description=metadataSchemaUniqueid2Description,
    credits=metadataSchemaUniqueid2Credits,
    valid=True,
    metadata=metadataSchemaUniqueid2Metadata,
)

# duplicate

writeMetadataTest(
    identifier="metadata-schema-uniqueid-003",
    title=metadataSchemaUniqueid3Title,
    description=metadataSchemaUniqueid3Description,
    credits=metadataSchemaUniqueid3Credits,
    valid=False,
    metadata=metadataSchemaUniqueid3Metadata,
)

# missing id attribute

writeMetadataTest(
    identifier="metadata-schema-uniqueid-004",
    title=metadataSchemaUniqueid4Title,
    description=metadataSchemaUniqueid4Description,
    credits=metadataSchemaUniqueid4Credits,
    specLink="#conform-metadata-id-required",
    valid=False,
    metadata=metadataSchemaUniqueid4Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-uniqueid-005",
    title=metadataSchemaUniqueid5Title,
    description=metadataSchemaUniqueid5Description,
    credits=metadataSchemaUniqueid5Credits,
    valid=False,
    metadata=metadataSchemaUniqueid5Metadata,
)

# unknown child

writeMetadataTest(
    identifier="metadata-schema-uniqueid-006",
    title=metadataSchemaUniqueid6Title,
    description=metadataSchemaUniqueid6Description,
    credits=metadataSchemaUniqueid6Credits,
    valid=False,
    metadata=metadataSchemaUniqueid6Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-uniqueid-007",
    title=metadataSchemaUniqueid7Title,
    description=metadataSchemaUniqueid7Description,
    credits=metadataSchemaUniqueid7Credits,
    valid=False,
    metadata=metadataSchemaUniqueid7Metadata,
)

# -----------------------------------------
# Metadata Display: Schema Validity: vendor
# -----------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-vendor-001",
    title=metadataSchemaVendor1Title,
    description=metadataSchemaVendor1Description,
    credits=metadataSchemaVendor1Credits,
    valid=True,
    metadata=metadataSchemaVendor1Metadata,
)

writeMetadataTest(
    identifier="metadata-schema-vendor-002",
    title=metadataSchemaVendor2Title,
    description=metadataSchemaVendor2Description,
    credits=metadataSchemaVendor2Credits,
    valid=True,
    metadata=metadataSchemaVendor2Metadata,
)

# does not exist

writeMetadataTest(
    identifier="metadata-schema-vendor-003",
    title=metadataSchemaVendor3Title,
    description=metadataSchemaVendor3Description,
    credits=metadataSchemaVendor3Credits,
    valid=True,
    metadata=metadataSchemaVendor3Metadata,
)

# duplicate

writeMetadataTest(
    identifier="metadata-schema-vendor-004",
    title=metadataSchemaVendor4Title,
    description=metadataSchemaVendor4Description,
    credits=metadataSchemaVendor4Credits,
    valid=False,
    metadata=metadataSchemaVendor4Metadata,
)

# missing name attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-005",
    title=metadataSchemaVendor5Title,
    description=metadataSchemaVendor5Description,
    credits=metadataSchemaVendor5Credits,
    specLink="#conform-metadata-vendor-required",
    valid=False,
    metadata=metadataSchemaVendor5Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-006",
    title=metadataSchemaVendor6Title,
    description=metadataSchemaVendor6Description,
    credits=metadataSchemaVendor6Credits,
    valid=False,
    metadata=metadataSchemaVendor6Metadata,
)

# unknown child

writeMetadataTest(
    identifier="metadata-schema-vendor-007",
    title=metadataSchemaVendor7Title,
    description=metadataSchemaVendor7Description,
    credits=metadataSchemaVendor7Credits,
    valid=False,
    metadata=metadataSchemaVendor7Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-vendor-008",
    title=metadataSchemaVendor8Title,
    description=metadataSchemaVendor8Description,
    credits=metadataSchemaVendor8Credits,
    valid=False,
    metadata=metadataSchemaVendor8Metadata,
)

# ------------------------------------------
# Metadata Display: Schema Validity: credits
# ------------------------------------------

# valid - no lang, single credit element

writeMetadataTest(
    identifier="metadata-schema-credits-001",
    title=metadataSchemaCredits1Title,
    description=metadataSchemaCredits1Description,
    credits=metadataSchemaCredits1Credits,
    valid=True,
    metadata=metadataSchemaCredits1Metadata,
)

# valid - lang, single credit element

writeMetadataTest(
    identifier="metadata-schema-credits-002",
    title=metadataSchemaCredits2Title,
    description=metadataSchemaCredits2Description,
    credits=metadataSchemaCredits2Credits,
    valid=True,
    metadata=metadataSchemaCredits2Metadata,
)

# valid - multiple credit elements

writeMetadataTest(
    identifier="metadata-schema-credits-003",
    title=metadataSchemaCredits3Title,
    description=metadataSchemaCredits3Description,
    credits=metadataSchemaCredits3Credits,
    valid=True,
    metadata=metadataSchemaCredits3Metadata,
)

# more than one credits

writeMetadataTest(
    identifier="metadata-schema-credits-004",
    title=metadataSchemaCredits4Title,
    description=metadataSchemaCredits4Description,
    credits=metadataSchemaCredits4Credits,
    valid=True,
    metadata=metadataSchemaCredits4Metadata,
)

# missing credit element

writeMetadataTest(
    identifier="metadata-schema-credits-005",
    title=metadataSchemaCredits5Title,
    description=metadataSchemaCredits5Description,
    credits=metadataSchemaCredits5Credits,
    valid=False,
    metadata=metadataSchemaCredits5Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-credits-006",
    title=metadataSchemaCredits6Title,
    description=metadataSchemaCredits6Description,
    credits=metadataSchemaCredits6Credits,
    valid=False,
    metadata=metadataSchemaCredits6Metadata,
)

# unknown element

writeMetadataTest(
    identifier="metadata-schema-credits-007",
    title=metadataSchemaCredits7Title,
    description=metadataSchemaCredits7Description,
    credits=metadataSchemaCredits7Credits,
    valid=False,
    metadata=metadataSchemaCredits7Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-credits-008",
    title=metadataSchemaCredits8Title,
    description=metadataSchemaCredits8Description,
    credits=metadataSchemaCredits8Credits,
    valid=False,
    metadata=metadataSchemaCredits8Metadata,
)

# -----------------------------------------
# Metadata Display: Schema Validity: credit
# -----------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-credit-001",
    title=metadataSchemaCredit1Title,
    description=metadataSchemaCredit1Description,
    credits=metadataSchemaCredit1Credits,
    valid=True,
    metadata=metadataSchemaCredit1Metadata,
)

# valid no url

writeMetadataTest(
    identifier="metadata-schema-credit-002",
    title=metadataSchemaCredit2Title,
    description=metadataSchemaCredit2Description,
    credits=metadataSchemaCredit2Credits,
    valid=True,
    metadata=metadataSchemaCredit2Metadata,
)

# valid no role

writeMetadataTest(
    identifier="metadata-schema-credit-003",
    title=metadataSchemaCredit3Title,
    description=metadataSchemaCredit3Description,
    credits=metadataSchemaCredit3Credits,
    valid=True,
    metadata=metadataSchemaCredit3Metadata,
)

# no name

writeMetadataTest(
    identifier="metadata-schema-credit-004",
    title=metadataSchemaCredit4Title,
    description=metadataSchemaCredit4Description,
    credits=metadataSchemaCredit4Credits,
    valid=False,
    metadata=metadataSchemaCredit4Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-credit-005",
    title=metadataSchemaCredit5Title,
    description=metadataSchemaCredit5Description,
    credits=metadataSchemaCredit5Credits,
    valid=False,
    metadata=metadataSchemaCredit5Metadata,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-credit-006",
    title=metadataSchemaCredit6Title,
    description=metadataSchemaCredit6Description,
    credits=metadataSchemaCredit6Credits,
    valid=False,
    metadata=metadataSchemaCredit6Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-credit-007",
    title=metadataSchemaCredit7Title,
    description=metadataSchemaCredit7Description,
    credits=metadataSchemaCredit7Credits,
    valid=False,
    metadata=metadataSchemaCredit7Metadata,
)

# ----------------------------------------------
# Metadata Display: Schema Validity: description
# ----------------------------------------------

# valid with url

writeMetadataTest(
    identifier="metadata-schema-description-001",
    title=metadataSchemaDescription1Title,
    description=metadataSchemaDescription1Description,
    credits=metadataSchemaDescription1Credits,
    valid=True,
    metadata=metadataSchemaDescription1Metadata,
)

# valid without url

writeMetadataTest(
    identifier="metadata-schema-description-002",
    title=metadataSchemaDescription2Title,
    description=metadataSchemaDescription2Description,
    credits=metadataSchemaDescription2Credits,
    valid=True,
    metadata=metadataSchemaDescription2Metadata,
)

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-description-003",
    title=metadataSchemaDescription3Title,
    description=metadataSchemaDescription3Description,
    credits=metadataSchemaDescription3Credits,
    valid=True,
    metadata=metadataSchemaDescription3Metadata,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-description-004",
    title=metadataSchemaDescription4Title,
    description=metadataSchemaDescription4Description,
    credits=metadataSchemaDescription4Credits,
    valid=True,
    metadata=metadataSchemaDescription4Metadata,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-description-005",
    title=metadataSchemaDescription5Title,
    description=metadataSchemaDescription5Description,
    credits=metadataSchemaDescription5Credits,
    valid=True,
    metadata=metadataSchemaDescription5Metadata,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-description-006",
    title=metadataSchemaDescription6Title,
    description=metadataSchemaDescription6Description,
    credits=metadataSchemaDescription6Credits,
    valid=True,
    metadata=metadataSchemaDescription6Metadata,
)

# more than one description

writeMetadataTest(
    identifier="metadata-schema-description-007",
    title=metadataSchemaDescription7Title,
    description=metadataSchemaDescription7Description,
    credits=metadataSchemaDescription7Credits,
    valid=False,
    metadata=metadataSchemaDescription7Metadata,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-description-008",
    title=metadataSchemaDescription8Title,
    description=metadataSchemaDescription8Description,
    credits=metadataSchemaDescription8Credits,
    valid=False,
    metadata=metadataSchemaDescription8Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-description-009",
    title=metadataSchemaDescription9Title,
    description=metadataSchemaDescription9Description,
    credits=metadataSchemaDescription9Credits,
    valid=False,
    metadata=metadataSchemaDescription9Metadata,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-description-010",
    title=metadataSchemaDescription10Title,
    description=metadataSchemaDescription10Description,
    credits=metadataSchemaDescription10Credits,
    valid=False,
    metadata=metadataSchemaDescription10Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-description-011",
    title=metadataSchemaDescription11Title,
    description=metadataSchemaDescription11Description,
    credits=metadataSchemaDescription11Credits,
    valid=False,
    metadata=metadataSchemaDescription11Metadata,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-description-012",
    title=metadataSchemaDescription12Title,
    description=metadataSchemaDescription12Description,
    credits=metadataSchemaDescription12Credits,
    valid=False,
    metadata=metadataSchemaDescription12Metadata,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-description-013",
    title=metadataSchemaDescription13Title,
    description=metadataSchemaDescription13Description,
    credits=metadataSchemaDescription13Credits,
    valid=False,
    metadata=metadataSchemaDescription13Metadata,
)

# ------------------------------------------
# Metadata Display: Schema Validity: license
# ------------------------------------------

# valid with url and license

writeMetadataTest(
    identifier="metadata-schema-license-001",
    title=metadataSchemaLicense1Title,
    description=metadataSchemaLicense1Description,
    credits=metadataSchemaLicense1Credits,
    valid=True,
    metadata=metadataSchemaLicense1Metadata,
)

# valid no url

writeMetadataTest(
    identifier="metadata-schema-license-002",
    title=metadataSchemaLicense2Title,
    description=metadataSchemaLicense2Description,
    credits=metadataSchemaLicense2Credits,
    valid=True,
    metadata=metadataSchemaLicense2Metadata,
)

# valid no id

writeMetadataTest(
    identifier="metadata-schema-license-003",
    title=metadataSchemaLicense3Title,
    description=metadataSchemaLicense3Description,
    credits=metadataSchemaLicense3Credits,
    valid=True,
    metadata=metadataSchemaLicense3Metadata,
)

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-license-004",
    title=metadataSchemaLicense4Title,
    description=metadataSchemaLicense4Description,
    credits=metadataSchemaLicense4Credits,
    valid=True,
    metadata=metadataSchemaLicense4Metadata,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-license-005",
    title=metadataSchemaLicense5Title,
    description=metadataSchemaLicense5Description,
    credits=metadataSchemaLicense5Credits,
    valid=True,
    metadata=metadataSchemaLicense5Metadata,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-license-006",
    title=metadataSchemaLicense6Title,
    description=metadataSchemaLicense6Description,
    credits=metadataSchemaLicense6Credits,
    valid=True,
    metadata=metadataSchemaLicense6Metadata,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-license-007",
    title=metadataSchemaLicense7Title,
    description=metadataSchemaLicense7Description,
    credits=metadataSchemaLicense7Credits,
    valid=True,
    metadata=metadataSchemaLicense7Metadata,
)

# more than one license

writeMetadataTest(
    identifier="metadata-schema-license-008",
    title=metadataSchemaLicense8Title,
    description=metadataSchemaLicense8Description,
    credits=metadataSchemaLicense8Credits,
    valid=False,
    metadata=metadataSchemaLicense8Metadata,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-license-009",
    title=metadataSchemaLicense9Title,
    description=metadataSchemaLicense9Description,
    credits=metadataSchemaLicense9Credits,
    valid=False,
    metadata=metadataSchemaLicense9Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-license-010",
    title=metadataSchemaLicense10Title,
    description=metadataSchemaLicense10Description,
    credits=metadataSchemaLicense10Credits,
    valid=False,
    metadata=metadataSchemaLicense10Metadata,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-license-011",
    title=metadataSchemaLicense11Title,
    description=metadataSchemaLicense11Description,
    credits=metadataSchemaLicense11Credits,
    valid=False,
    metadata=metadataSchemaLicense11Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-license-012",
    title=metadataSchemaLicense12Title,
    description=metadataSchemaLicense12Description,
    credits=metadataSchemaLicense12Credits,
    valid=False,
    metadata=metadataSchemaLicense12Metadata,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-license-013",
    title=metadataSchemaLicense13Title,
    description=metadataSchemaLicense13Description,
    credits=metadataSchemaLicense13Credits,
    valid=False,
    metadata=metadataSchemaLicense13Metadata,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-license-014",
    title=metadataSchemaLicense14Title,
    description=metadataSchemaLicense14Description,
    credits=metadataSchemaLicense14Credits,
    valid=False,
    metadata=metadataSchemaLicense14Metadata,
)

# --------------------------------------------
# Metadata Display: Schema Validity: copyright
# --------------------------------------------

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-copyright-001",
    title=metadataSchemaCopyright1Title,
    description=metadataSchemaCopyright1Description,
    credits=metadataSchemaCopyright1Credits,
    valid=True,
    metadata=metadataSchemaCopyright1Metadata,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-copyright-002",
    title=metadataSchemaCopyright2Title,
    description=metadataSchemaCopyright2Description,
    credits=metadataSchemaCopyright2Credits,
    valid=True,
    metadata=metadataSchemaCopyright2Metadata,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-copyright-003",
    title=metadataSchemaCopyright3Title,
    description=metadataSchemaCopyright3Description,
    credits=metadataSchemaCopyright3Credits,
    valid=True,
    metadata=metadataSchemaCopyright3Metadata,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-copyright-004",
    title=metadataSchemaCopyright4Title,
    description=metadataSchemaCopyright4Description,
    credits=metadataSchemaCopyright4Credits,
    valid=True,
    metadata=metadataSchemaCopyright4Metadata,
)

# more than one copyright

writeMetadataTest(
    identifier="metadata-schema-copyright-005",
    title=metadataSchemaCopyright5Title,
    description=metadataSchemaCopyright5Description,
    credits=metadataSchemaCopyright5Credits,
    valid=False,
    metadata=metadataSchemaCopyright5Metadata,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-copyright-006",
    title=metadataSchemaCopyright6Title,
    description=metadataSchemaCopyright6Description,
    credits=metadataSchemaCopyright6Credits,
    valid=False,
    metadata=metadataSchemaCopyright6Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-007",
    title=metadataSchemaCopyright7Title,
    description=metadataSchemaCopyright7Description,
    credits=metadataSchemaCopyright7Credits,
    valid=False,
    metadata=metadataSchemaCopyright7Metadata,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-copyright-008",
    title=metadataSchemaCopyright8Title,
    description=metadataSchemaCopyright8Description,
    credits=metadataSchemaCopyright8Credits,
    valid=False,
    metadata=metadataSchemaCopyright8Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-copyright-009",
    title=metadataSchemaCopyright9Title,
    description=metadataSchemaCopyright9Description,
    credits=metadataSchemaCopyright9Credits,
    valid=False,
    metadata=metadataSchemaCopyright9Metadata,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-010",
    title=metadataSchemaCopyright10Title,
    description=metadataSchemaCopyright10Description,
    credits=metadataSchemaCopyright10Credits,
    valid=False,
    metadata=metadataSchemaCopyright10Metadata,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-copyright-011",
    title=metadataSchemaCopyright11Title,
    description=metadataSchemaCopyright11Description,
    credits=metadataSchemaCopyright11Credits,
    valid=False,
    metadata=metadataSchemaCopyright11Metadata,
)

# --------------------------------------------
# Metadata Display: Schema Validity: trademark
# --------------------------------------------

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-trademark-001",
    title=metadataSchemaTrademark1Title,
    description=metadataSchemaTrademark1Description,
    credits=metadataSchemaTrademark1Credits,
    valid=True,
    metadata=metadataSchemaTrademark1Metadata,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-trademark-002",
    title=metadataSchemaTrademark2Title,
    description=metadataSchemaTrademark2Description,
    credits=metadataSchemaTrademark2Credits,
    valid=True,
    metadata=metadataSchemaTrademark2Metadata,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-trademark-003",
    title=metadataSchemaTrademark3Title,
    description=metadataSchemaTrademark3Description,
    credits=metadataSchemaTrademark3Credits,
    valid=True,
    metadata=metadataSchemaTrademark3Metadata,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-trademark-004",
    title=metadataSchemaTrademark4Title,
    description=metadataSchemaTrademark4Description,
    credits=metadataSchemaTrademark4Credits,
    valid=True,
    metadata=metadataSchemaTrademark4Metadata,
)

# more than one trademark

writeMetadataTest(
    identifier="metadata-schema-trademark-005",
    title=metadataSchemaTrademark5Title,
    description=metadataSchemaTrademark5Description,
    credits=metadataSchemaTrademark5Credits,
    valid=False,
    metadata=metadataSchemaTrademark5Metadata,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-trademark-006",
    title=metadataSchemaTrademark6Title,
    description=metadataSchemaTrademark6Description,
    credits=metadataSchemaTrademark6Credits,
    valid=False,
    metadata=metadataSchemaTrademark6Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-007",
    title=metadataSchemaTrademark7Title,
    description=metadataSchemaTrademark7Description,
    credits=metadataSchemaTrademark7Credits,
    valid=False,
    metadata=metadataSchemaTrademark7Metadata,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-trademark-008",
    title=metadataSchemaTrademark8Title,
    description=metadataSchemaTrademark8Description,
    credits=metadataSchemaTrademark8Credits,
    valid=False,
    metadata=metadataSchemaTrademark8Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-trademark-009",
    title=metadataSchemaTrademark9Title,
    description=metadataSchemaTrademark9Description,
    credits=metadataSchemaTrademark9Credits,
    valid=False,
    metadata=metadataSchemaTrademark9Metadata,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-010",
    title=metadataSchemaTrademark10Title,
    description=metadataSchemaTrademark10Description,
    credits=metadataSchemaTrademark10Credits,
    valid=False,
    metadata=metadataSchemaTrademark10Metadata,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-trademark-011",
    title=metadataSchemaTrademark11Title,
    description=metadataSchemaTrademark11Description,
    credits=metadataSchemaTrademark11Credits,
    valid=False,
    metadata=metadataSchemaTrademark11Metadata,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-licensee-001",
    title=metadataSchemaLicensee1Title,
    description=metadataSchemaLicensee1Description,
    credits=metadataSchemaLicensee1Credits,
    valid=True,
    metadata=metadataSchemaLicensee1Metadata,
)

# duplicate

writeMetadataTest(
    identifier="metadata-schema-licensee-002",
    title=metadataSchemaLicensee2Title,
    description=metadataSchemaLicensee2Description,
    credits=metadataSchemaLicensee2Credits,
    valid=False,
    metadata=metadataSchemaLicensee2Metadata,
)

# missing name

writeMetadataTest(
    identifier="metadata-schema-licensee-003",
    title=metadataSchemaLicensee3Title,
    description=metadataSchemaLicensee3Description,
    credits=metadataSchemaLicensee3Credits,
    valid=False,
    metadata=metadataSchemaLicensee3Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-licensee-004",
    title=metadataSchemaLicensee4Title,
    description=metadataSchemaLicensee4Description,
    credits=metadataSchemaLicensee4Credits,
    valid=False,
    metadata=metadataSchemaLicensee4Metadata,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-licensee-005",
    title=metadataSchemaLicensee5Title,
    description=metadataSchemaLicensee5Description,
    credits=metadataSchemaLicensee5Credits,
    valid=False,
    metadata=metadataSchemaLicensee5Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-licensee-006",
    title=metadataSchemaLicensee6Title,
    description=metadataSchemaLicensee6Description,
    credits=metadataSchemaLicensee6Credits,
    valid=False,
    metadata=metadataSchemaLicensee6Metadata,
)

# --------------------------------------------
# Metadata Display: Schema Validity: extension
# --------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-extension-001",
    title=metadataSchemaExtension1Title,
    description=metadataSchemaExtension1Description,
    credits=metadataSchemaExtension1Credits,
    valid=True,
    metadata=metadataSchemaExtension1Metadata,
)

# valid two extensions

writeMetadataTest(
    identifier="metadata-schema-extension-002",
    title=metadataSchemaExtension2Title,
    description=metadataSchemaExtension2Description,
    credits=metadataSchemaExtension2Credits,
    valid=True,
    metadata=metadataSchemaExtension2Metadata,
)

# valid no id

writeMetadataTest(
    identifier="metadata-schema-extension-003",
    title=metadataSchemaExtension3Title,
    description=metadataSchemaExtension3Description,
    credits=metadataSchemaExtension3Credits,
    valid=True,
    metadata=metadataSchemaExtension3Metadata,
)

# valid no name

writeMetadataTest(
    identifier="metadata-schema-extension-004",
    title=metadataSchemaExtension4Title,
    description=metadataSchemaExtension4Description,
    credits=metadataSchemaExtension4Credits,
    valid=True,
    metadata=metadataSchemaExtension4Metadata,
)

# valid one untagged name one tagged name

writeMetadataTest(
    identifier="metadata-schema-extension-005",
    title=metadataSchemaExtension5Title,
    description=metadataSchemaExtension5Description,
    credits=metadataSchemaExtension5Credits,
    valid=True,
    metadata=metadataSchemaExtension5Metadata,
)

# valid two tagged names

writeMetadataTest(
    identifier="metadata-schema-extension-006",
    title=metadataSchemaExtension6Title,
    description=metadataSchemaExtension6Description,
    credits=metadataSchemaExtension6Credits,
    valid=True,
    metadata=metadataSchemaExtension6Metadata,
)

# valid more than one item

writeMetadataTest(
    identifier="metadata-schema-extension-007",
    title=metadataSchemaExtension7Title,
    description=metadataSchemaExtension7Description,
    credits=metadataSchemaExtension7Credits,
    valid=True,
    metadata=metadataSchemaExtension7Metadata,
)

# no item

writeMetadataTest(
    identifier="metadata-schema-extension-008",
    title=metadataSchemaExtension8Title,
    description=metadataSchemaExtension8Description,
    credits=metadataSchemaExtension8Credits,
    valid=False,
    metadata=metadataSchemaExtension8Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-009",
    title=metadataSchemaExtension9Title,
    description=metadataSchemaExtension9Description,
    credits=metadataSchemaExtension9Credits,
    valid=False,
    metadata=metadataSchemaExtension9Metadata,
)

# unknown child

writeMetadataTest(
    identifier="metadata-schema-extension-010",
    title=metadataSchemaExtension10Title,
    description=metadataSchemaExtension10Description,
    credits=metadataSchemaExtension10Credits,
    valid=False,
    metadata=metadataSchemaExtension10Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-extension-011",
    title=metadataSchemaExtension11Title,
    description=metadataSchemaExtension11Description,
    credits=metadataSchemaExtension11Credits,
    valid=False,
    metadata=metadataSchemaExtension11Metadata,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - item
# ---------------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-extension-012",
    title=metadataSchemaExtension12Title,
    description=metadataSchemaExtension12Description,
    credits=metadataSchemaExtension12Credits,
    valid=True,
    metadata=metadataSchemaExtension12Metadata,
)

# valid multiple languages

writeMetadataTest(
    identifier="metadata-schema-extension-013",
    title=metadataSchemaExtension13Title,
    description=metadataSchemaExtension13Description,
    credits=metadataSchemaExtension13Credits,
    valid=True,
    metadata=metadataSchemaExtension13Metadata,
)

# valid no id

writeMetadataTest(
    identifier="metadata-schema-extension-014",
    title=metadataSchemaExtension14Title,
    description=metadataSchemaExtension14Description,
    credits=metadataSchemaExtension14Credits,
    valid=True,
    metadata=metadataSchemaExtension14Metadata,
)

# valid name no tag and tagged

writeMetadataTest(
    identifier="metadata-schema-extension-015",
    title=metadataSchemaExtension15Title,
    description=metadataSchemaExtension15Description,
    credits=metadataSchemaExtension15Credits,
    valid=True,
    metadata=metadataSchemaExtension15Metadata,
)

# valid name two tagged

writeMetadataTest(
    identifier="metadata-schema-extension-016",
    title=metadataSchemaExtension16Title,
    description=metadataSchemaExtension16Description,
    credits=metadataSchemaExtension16Credits,
    valid=True,
    metadata=metadataSchemaExtension16Metadata,
)

# valid value no tag and tagged

writeMetadataTest(
    identifier="metadata-schema-extension-017",
    title=metadataSchemaExtension17Title,
    description=metadataSchemaExtension17Description,
    credits=metadataSchemaExtension17Credits,
    valid=True,
    metadata=metadataSchemaExtension17Metadata,
)

# valid value two tagged

writeMetadataTest(
    identifier="metadata-schema-extension-018",
    title=metadataSchemaExtension18Title,
    description=metadataSchemaExtension18Description,
    credits=metadataSchemaExtension18Credits,
    valid=True,
    metadata=metadataSchemaExtension18Metadata,
)

# no name

writeMetadataTest(
    identifier="metadata-schema-extension-019",
    title=metadataSchemaExtension19Title,
    description=metadataSchemaExtension19Description,
    credits=metadataSchemaExtension19Credits,
    valid=False,
    metadata=metadataSchemaExtension19Metadata,
)

# no value

writeMetadataTest(
    identifier="metadata-schema-extension-020",
    title=metadataSchemaExtension20Title,
    description=metadataSchemaExtension20Description,
    credits=metadataSchemaExtension20Credits,
    valid=False,
    metadata=metadataSchemaExtension20Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-021",
    title=metadataSchemaExtension21Title,
    description=metadataSchemaExtension21Description,
    credits=metadataSchemaExtension21Credits,
    valid=False,
    metadata=metadataSchemaExtension21Metadata,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-extension-022",
    title=metadataSchemaExtension22Title,
    description=metadataSchemaExtension22Description,
    credits=metadataSchemaExtension22Credits,
    valid=False,
    metadata=metadataSchemaExtension22Metadata,
)

# content

writeMetadataTest(
    identifier="metadata-schema-extension-023",
    title=metadataSchemaExtension23Title,
    description=metadataSchemaExtension23Description,
    credits=metadataSchemaExtension23Credits,
    valid=False,
    metadata=metadataSchemaExtension23Metadata,
)

# ----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - name
# ----------------------------------------------------------

# valid no lang

writeMetadataTest(
    identifier="metadata-schema-extension-024",
    title=metadataSchemaExtension24Title,
    description=metadataSchemaExtension24Description,
    credits=metadataSchemaExtension24Credits,
    valid=True,
    metadata=metadataSchemaExtension24Metadata,
)

# valid lang

writeMetadataTest(
    identifier="metadata-schema-extension-025",
    title=metadataSchemaExtension25Title,
    description=metadataSchemaExtension25Description,
    credits=metadataSchemaExtension25Credits,
    valid=True,
    metadata=metadataSchemaExtension25Metadata,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-026",
    title=metadataSchemaExtension26Title,
    description=metadataSchemaExtension26Description,
    credits=metadataSchemaExtension26Credits,
    valid=False,
    metadata=metadataSchemaExtension26Metadata,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-extension-027",
    title=metadataSchemaExtension27Title,
    description=metadataSchemaExtension27Description,
    credits=metadataSchemaExtension27Credits,
    valid=False,
    metadata=metadataSchemaExtension27Metadata,
)

# -----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - value
# -----------------------------------------------------------

# valid no lang

writeMetadataTest(
    identifier="metadata-schema-extension-028",
    title=metadataSchemaExtension28Title,
    description=metadataSchemaExtension28Description,
    credits=metadataSchemaExtension28Credits,
    valid=True,
    metadata=metadataSchemaExtension28Metadata,
)

# valid lang

writeMetadataTest(
    identifier="metadata-schema-extension-029",
    title=metadataSchemaExtension29Title,
    description=metadataSchemaExtension29Description,
    credits=metadataSchemaExtension29Credits,
    valid=True,
    metadata=metadataSchemaExtension29Metadata,
)


# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-030",
    title=metadataSchemaExtension30Title,
    description=metadataSchemaExtension30Description,
    credits=metadataSchemaExtension30Credits,
    valid=False,
    metadata=metadataSchemaExtension30Metadata,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-extension-031",
    title=metadataSchemaExtension31Title,
    description=metadataSchemaExtension31Description,
    credits=metadataSchemaExtension31Credits,
    valid=False,
    metadata=metadataSchemaExtension31Metadata,
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
    valid=True,
    specLink="#conform-private-padalign",
    data=makePrivateData4Byte1()
)

# -----------------------
# Finish Index Generation
# -----------------------

# make it pretty
indent(indexRoot)
# write it
tree = ElementTree(indexRoot)
path = os.path.join(formatDirectory, "testcases.xml")
if os.path.exists(path):
    os.remove(path)
tree.write(path, encoding="utf8")

# -----------------------
# Check for Unknown Files
# -----------------------

woffPattern = os.path.join(formatDirectory, "*.woff")
filesOnDisk = glob.glob(woffPattern)

for path in filesOnDisk:
    identifier = os.path.basename(path)
    identifier = identifier.split(".")[0]
    if identifier not in registeredIdentifiers:
        print "Unknown file:", path
