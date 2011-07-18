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
from testCaseGeneratorLib.woff import packTestHeader, packTestDirectory, packTestTableData, packTestMetadata, packTestPrivateData
from testCaseGeneratorLib.defaultData import defaultTestData, testDataWOFFMetadata, testDataWOFFPrivateData
from testCaseGeneratorLib.html import generateSFNTDisplayTestHTML, generateSFNTDisplayRefHTML, generateSFNTDisplayIndexHTML
from testCaseGeneratorLib.paths import resourcesDirectory, userAgentDirectory, userAgentTestDirectory, userAgentTestResourcesDirectory, userAgentFontsToInstallDirectory
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
destPath = os.path.join(userAgentTestResourcesDirectory, "index.css")
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
registeredTitles = set()
registeredAssertions = set()

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
    assert title not in registeredTitles, "Duplicate title! %s" % title
    assert assertion not in registeredAssertions, "Duplicate assertion! %s" % assertion
    registeredIdentifiers.add(identifier)
    registeredTitles.add(title)
    registeredAssertions.add(assertion)

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
    # dynamically get some data from the shared cases as needed
    if title is None:
        assert assertion is None
        assert metadata is None
        parts = identifier.split("-")
        assert parts[0] == "metadatadisplay"
        number = int(parts[-1])
        group = parts[1:-1]
        group = [i.title() for i in group]
        group = "".join(group)
        importBase = "metadata" + group + str(number)
        title = getattr(sharedCases, importBase + "Title")
        assertion = getattr(sharedCases, importBase + "Description")
        credits = getattr(sharedCases, importBase + "Credits")
        metadata = getattr(sharedCases, importBase + "Metadata")
    assert metadata is not None
    assert metadataIsValid is not None
    # compile the WOFF
    data, metadata = makeMetadataTest(metadata)
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
        kwargs["metadataToDisplay"] = metadata
    writeFileStructureTest(
        identifier,
        **kwargs
    )

# -----------
# Valid Files
# -----------

# CFF

writeFileStructureTest(
    identifier="valid-001",
    title=makeValidWOFF1Title,
    assertion=makeValidWOFF1Description,
    credits=makeValidWOFF1Credits,
    shouldDisplaySFNT=True,
    data=makeValidWOFF1()
)

writeFileStructureTest(
    identifier="valid-002",
    title=makeValidWOFF2Title,
    assertion=makeValidWOFF2Description,
    credits=makeValidWOFF2Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    data=makeValidWOFF2(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

writeFileStructureTest(
    identifier="valid-003",
    title=makeValidWOFF3Title,
    assertion=makeValidWOFF3Description,
    credits=makeValidWOFF3Credits,
    shouldDisplaySFNT=True,
    data=makeValidWOFF3()
)

writeFileStructureTest(
    identifier="valid-004",
    title=makeValidWOFF4Title,
    assertion=makeValidWOFF4Description,
    credits=makeValidWOFF4Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    data=makeValidWOFF4(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

# TTF

writeFileStructureTest(
    identifier="valid-005",
    flavor="TTF",
    title=makeValidWOFF5Title,
    assertion=makeValidWOFF5Description,
    credits=makeValidWOFF5Credits,
    shouldDisplaySFNT=True,
    data=makeValidWOFF5()
)

writeFileStructureTest(
    identifier="valid-006",
    flavor="TTF",
    title=makeValidWOFF6Title,
    assertion=makeValidWOFF6Description,
    credits=makeValidWOFF6Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    data=makeValidWOFF6(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

writeFileStructureTest(
    identifier="valid-007",
    flavor="TTF",
    title=makeValidWOFF7Title,
    assertion=makeValidWOFF7Description,
    credits=makeValidWOFF7Credits,
    shouldDisplaySFNT=True,
    data=makeValidWOFF7()
)

writeFileStructureTest(
    identifier="valid-008",
    flavor="TTF",
    title=makeValidWOFF8Title,
    assertion=makeValidWOFF8Description,
    credits=makeValidWOFF8Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    data=makeValidWOFF8(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

# ---------------------------------
# File Structure: Header: signature
# ---------------------------------

writeFileStructureTest(
    identifier="header-signature-001",
    title=makeHeaderInvalidSignature1Title,
    assertion=makeHeaderInvalidSignature1Description,
    credits=makeHeaderInvalidSignature1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-nomagicnumber-reject",
    data=makeHeaderInvalidSignature1()
)

# ------------------------------
# File Structure: Header: length
# ------------------------------

writeFileStructureTest(
    identifier="header-length-001",
    title=makeHeaderInvalidLength1Title,
    assertion=makeHeaderInvalidLength1Description,
    credits=makeHeaderInvalidLength1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#WOFFHeader",
    data=makeHeaderInvalidLength1()
)

writeFileStructureTest(
    identifier="header-length-002",
    title=makeHeaderInvalidLength2Title,
    assertion=makeHeaderInvalidLength2Description,
    credits=makeHeaderInvalidLength2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#WOFFHeader",
    data=makeHeaderInvalidLength2()
)

# ---------------------------------
# File Structure: Header: numTables
# ---------------------------------

writeFileStructureTest(
    identifier="header-numTables-001",
    title=makeHeaderInvalidNumTables1Title,
    assertion=makeHeaderInvalidNumTables1Description,
    credits=makeHeaderInvalidNumTables1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#WOFFHeader",
    data=makeHeaderInvalidNumTables1()
)

# -------------------------------------
# File Structure: Header: totalSfntSize
# -------------------------------------

writeFileStructureTest(
    identifier="header-totalSfntSize-001",
    title=makeHeaderInvalidTotalSfntSize1Title,
    assertion=makeHeaderInvalidTotalSfntSize1Description,
    credits=makeHeaderInvalidTotalSfntSize1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-totalsize-longword-reject",
    data=makeHeaderInvalidTotalSfntSize1()
)

writeFileStructureTest(
    identifier="header-totalSfntSize-002",
    title=makeHeaderInvalidTotalSfntSize2Title,
    assertion=makeHeaderInvalidTotalSfntSize2Description,
    credits=makeHeaderInvalidTotalSfntSize2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-totalsize-longword-reject",
    data=makeHeaderInvalidTotalSfntSize2()
)

writeFileStructureTest(
    identifier="header-totalSfntSize-003",
    title=makeHeaderInvalidTotalSfntSize3Title,
    assertion=makeHeaderInvalidTotalSfntSize3Description,
    credits=makeHeaderInvalidTotalSfntSize3Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-totalsize-longword-reject",
    data=makeHeaderInvalidTotalSfntSize3()
)

# --------------------------------
# File Structure: Header: reserved
# --------------------------------

writeFileStructureTest(
    identifier="header-reserved-001",
    title=makeHeaderInvalidReserved1Title,
    assertion=makeHeaderInvalidReserved1Description,
    credits=makeHeaderInvalidReserved1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-reserved-reject",
    data=makeHeaderInvalidReserved1()
)

# --------------------------------------------
# File Structure: Data Blocks: Extraneous Data
# --------------------------------------------

# between table directory and table data

writeFileStructureTest(
    identifier="blocks-extraneous-data-001",
    title=makeExtraneousData1Title,
    assertion=makeExtraneousData1Description,
    credits=makeExtraneousData1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData1()
)

# between tables

writeFileStructureTest(
    identifier="blocks-extraneous-data-002",
    title=makeExtraneousData2Title,
    assertion=makeExtraneousData2Description,
    credits=makeExtraneousData2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData2()
)

# after table data with no metadata or private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-003",
    title=makeExtraneousData3Title,
    assertion=makeExtraneousData3Description,
    credits=makeExtraneousData3Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData3()
)

# between tabledata and metadata

writeFileStructureTest(
    identifier="blocks-extraneous-data-004",
    title=makeExtraneousData4Title,
    assertion=makeExtraneousData4Description,
    credits=makeExtraneousData4Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData4()
)

# between tabledata and private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-005",
    title=makeExtraneousData5Title,
    assertion=makeExtraneousData5Description,
    credits=makeExtraneousData5Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData5()
)

# between metadata and private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-006",
    title=makeExtraneousData6Title,
    assertion=makeExtraneousData6Description,
    credits=makeExtraneousData6Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData6()
)

# after metadata with no private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-007",
    title=makeExtraneousData7Title,
    assertion=makeExtraneousData7Description,
    credits=makeExtraneousData7Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData7()
)

# after private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-008",
    title=makeExtraneousData8Title,
    assertion=makeExtraneousData8Description,
    credits=makeExtraneousData8Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData8()
)

# -------------------------------------
# File Structure: Data Blocks: Overlaps
# -------------------------------------

# two tables overlap

writeFileStructureTest(
    identifier="blocks-overlap-001",
    title=makeOverlappingData1Title,
    assertion=makeOverlappingData1Description,
    credits=makeOverlappingData1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData1()
)

# metadata overlaps the table data

writeFileStructureTest(
    identifier="blocks-overlap-002",
    title=makeOverlappingData2Title,
    assertion=makeOverlappingData2Description,
    credits=makeOverlappingData2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData2()
)

# private data overlaps the table data

writeFileStructureTest(
    identifier="blocks-overlap-003",
    title=makeOverlappingData3Title,
    assertion=makeOverlappingData3Description,
    credits=makeOverlappingData3Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData3()
)

# private data overlaps the metadata

writeFileStructureTest(
    identifier="blocks-overlap-004",
    title=makeOverlappingData4Title,
    assertion=makeOverlappingData4Description,
    credits=makeOverlappingData4Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData4()
)

# ------------------------------------------------
# File Structure: Table Directory: 4-Byte Boundary
# ------------------------------------------------

writeFileStructureTest(
    identifier="directory-4-byte-001",
    title=makeTableData4Byte1Title,
    assertion=makeTableData4Byte1Description,
    credits=makeTableData4Byte1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-tablesize-longword",
    data=makeTableData4Byte1()
)

# final table is not padded

writeFileStructureTest(
    identifier="directory-4-byte-002",
    title=makeTableData4Byte2Title,
    assertion=makeTableData4Byte2Description,
    credits=makeTableData4Byte2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-tablesize-longword",
    data=makeTableData4Byte2()
)

# -----------------------------------------
# File Structure: Table Directory: Overlaps
# -----------------------------------------

# offset after end of file

writeFileStructureTest(
    identifier="directory-overlaps-001",
    title=makeTableDataByteRange1Title,
    assertion=makeTableDataByteRange1Description,
    credits=makeTableDataByteRange1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange1()
)

# offset + length goes past the end of the file

writeFileStructureTest(
    identifier="directory-overlaps-002",
    title=makeTableDataByteRange2Title,
    assertion=makeTableDataByteRange2Description,
    credits=makeTableDataByteRange2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange2()
)

# overlaps metadata

writeFileStructureTest(
    identifier="directory-overlaps-003",
    title=makeTableDataByteRange3Title,
    assertion=makeTableDataByteRange3Description,
    credits=makeTableDataByteRange3Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange3()
)

# overlaps private data

writeFileStructureTest(
    identifier="directory-overlaps-004",
    title=makeTableDataByteRange4Title,
    assertion=makeTableDataByteRange4Description,
    credits=makeTableDataByteRange4Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange4()
)

# two tables overlap

writeFileStructureTest(
    identifier="directory-overlaps-005",
    title=makeTableDataByteRange5Title,
    assertion=makeTableDataByteRange5Description,
    credits=makeTableDataByteRange5Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-diroverlap-reject",
    data=makeTableDataByteRange5()
)

# -------------------------------------------
# File Structure: Table Directory: compLength
# -------------------------------------------

# some tables have a compressed length that is longer than the original length

writeFileStructureTest(
    identifier="directory-compLength-001",
    title=makeTableDataCompressionLength1Title,
    assertion=makeTableDataCompressionLength1Description,
    credits=makeTableDataCompressionLength1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-compressedlarger",
    data=makeTableDataCompressionLength1()
)

# -------------------------------------------
# File Structure: Table Directory: origLength
# -------------------------------------------

# one table has an origLength that is less than the decompressed length

writeFileStructureTest(
    identifier="directory-origLength-001",
    title=makeTableDataOriginalLength1Title,
    assertion=makeTableDataOriginalLength1Description,
    credits=makeTableDataOriginalLength1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-origLength",
    data=makeTableDataOriginalLength1()
)

# one table has an origLength that is greater than the decompressed length

writeFileStructureTest(
    identifier="directory-origLength-002",
    title=makeTableDataOriginalLength2Title,
    assertion=makeTableDataOriginalLength2Description,
    credits=makeTableDataOriginalLength2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-origLength",
    data=makeTableDataOriginalLength2()
)

# ---------------------------------------
# File Structure: Table Data: Compression
# ---------------------------------------

# no tables compressed

writeFileStructureTest(
    identifier="tabledata-compression-001",
    title=makeTableCompressionTest1Title,
    assertion=makeTableCompressionTest1Description,
    credits=makeTableCompressionTest1Credits,
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-mustuncompress",
    data=makeTableCompressionTest1()
)

# all possible tables are compressed

writeFileStructureTest(
    identifier="tabledata-compression-002",
    title=makeTableCompressionTest2Title,
    assertion=makeTableCompressionTest2Description,
    credits=makeTableCompressionTest2Credits,
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-mustuncompress",
    data=makeTableCompressionTest2()
)

# not all possible tables are compressed

writeFileStructureTest(
    identifier="tabledata-compression-003",
    title=makeTableCompressionTest3Title,
    assertion=makeTableCompressionTest3Description,
    credits=makeTableCompressionTest3Credits,
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-mustuncompress",
    data=makeTableCompressionTest3()
)

# varying compression levels

writeFileStructureTest(
    identifier="tabledata-compression-004",
    title=makeTableCompressionTest4Title,
    assertion=makeTableCompressionTest4Description,
    credits=makeTableCompressionTest4Credits,
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-mustuncompress",
    data=makeTableCompressionTest4()
)

# ----------------------------------------------
# File Structure: Table Data: Compression Format
# ----------------------------------------------

# compression incompatible with zlib

writeFileStructureTest(
    identifier="tabledata-zlib-001",
    title=makeTableZlibCompressionTest1Title,
    assertion=makeTableZlibCompressionTest1Description,
    credits=makeTableZlibCompressionTest1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-decompressfailure",
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

writeFileStructureTest(
    identifier="metadatadisplay-compression-001",
    title=makeMetadataCompression1Title,
    assertion=makeMetadataCompression1Description,
    credits=makeMetadataCompression1Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=False,
    metadataDisplaySpecLink="#conform-metadata-alwayscompress",
    data=makeMetadataCompression1(),
)

# --------------------------------
# Metadata Display: metaOrigLength
# --------------------------------

# <

writeFileStructureTest(
    identifier="metadatadisplay-metaOrigLength-001",
    title=makeMetaOrigLengthTest1Title,
    assertion=makeMetaOrigLengthTest1Description,
    credits=makeMetaOrigLengthTest1Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=False,
    sfntDisplaySpecLink="#conform-metaOrigLength",
    data=makeMetaOrigLengthTest1()
)

# >

writeFileStructureTest(
    identifier="metadatadisplay-metaOrigLength-002",
    title=makeMetaOrigLengthTest2Title,
    assertion=makeMetaOrigLengthTest2Description,
    credits=makeMetaOrigLengthTest2Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=False,
    sfntDisplaySpecLink="#conform-metaOrigLength",
    data=makeMetaOrigLengthTest2()
)

# -----------------------------
# Metadata Display: Well-Formed
# -----------------------------

# <

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-001",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# &

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-002",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# mismatched elements

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-003",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# unclosed element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-004",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# case mismatch

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-005",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# more than one root

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-006",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# unknown encoding

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-007",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# --------------------------
# Metadata Display: Encoding
# --------------------------

# UTF-8

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-001",
    metadataIsValid=True,
)

# Invalid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-002",
    metadataIsValid=False,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-003",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# -------------------------------------------
# Metadata Display: Schema Validity: metadata
# -------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-001",
    metadataIsValid=True,
)

# missing version

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-002",
    metadataIsValid=False,
)

# invalid version

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-003",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-004",
    metadataIsValid=False,
)

# unknown element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-005",
    metadataIsValid=False,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-001",
    metadataIsValid=True,
)

# does not exist

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-002",
    metadataIsValid=True,
)

# duplicate

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-003",
    metadataIsValid=False,
)

# missing id attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-004",
    metadataDisplaySpecLink="#conform-metadata-id-required",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-005",
    metadataIsValid=False,
)

# unknown child

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-006",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-007",
    metadataIsValid=False,
)

# -----------------------------------------
# Metadata Display: Schema Validity: vendor
# -----------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-001",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-002",
    metadataIsValid=True,
)

# does not exist

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-003",
    metadataIsValid=True,
)

# duplicate

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-004",
    metadataIsValid=False,
)

# missing name attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-005",
    metadataDisplaySpecLink="#conform-metadata-vendor-required",
    metadataIsValid=False,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-006",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-007",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-008",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-009",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-010",
    metadataIsValid=False,
)

# unknown child

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-011",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-012",
    metadataIsValid=False,
)

# ------------------------------------------
# Metadata Display: Schema Validity: credits
# ------------------------------------------

# valid - single credit element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-001",
    metadataIsValid=True,
)

# valid - multiple credit elements

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-002",
    metadataIsValid=True,
)

# missing credit element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-003",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-004",
    metadataIsValid=False,
)

# unknown element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-005",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-006",
    metadataIsValid=False,
)

# multiple credits

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-007",
    metadataIsValid=False,
)

# -----------------------------------------
# Metadata Display: Schema Validity: credit
# -----------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-001",
    metadataIsValid=True,
)

# valid no url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-002",
    metadataIsValid=True,
)

# valid no role

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-003",
    metadataIsValid=True,
)

# no name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-004",
    metadataIsValid=False,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-005",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-006",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-007",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-008",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-009",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-010",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-011",
    metadataIsValid=False,
)

# ----------------------------------------------
# Metadata Display: Schema Validity: description
# ----------------------------------------------

# valid with url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-001",
    metadataIsValid=True,
)

# valid without url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-002",
    metadataIsValid=True,
)

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-003",
    metadataIsValid=True,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-004",
    metadataIsValid=True,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-005",
    metadataIsValid=True,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-006",
    metadataIsValid=True,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-007",
    metadataIsValid=True,
)

# more than one description

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-008",
    metadataIsValid=False,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-009",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-010",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-011",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-012",
    metadataIsValid=False,
)

# dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-013",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-014",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-015",
    metadataIsValid=False,
)

# class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-016",
    metadataIsValid=True,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-017",
    metadataIsValid=False,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-018",
    metadataIsValid=False,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-019",
    metadataIsValid=True,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-020",
    metadataIsValid=True,
)

# nested div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-021",
    metadataIsValid=True,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-022",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-023",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-024",
    metadataIsValid=False,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-025",
    metadataIsValid=True,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-026",
    metadataIsValid=True,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-027",
    metadataIsValid=True,
)

# nested span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-028",
    metadataIsValid=True,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-029",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-030",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-031",
    metadataIsValid=False,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-032",
    metadataIsValid=True,
)

# ------------------------------------------
# Metadata Display: Schema Validity: license
# ------------------------------------------

# valid with url and license

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-001",
    metadataIsValid=True,
)

# valid no url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-002",
    metadataIsValid=True,
)

# valid no id

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-003",
    metadataIsValid=True,
)

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-004",
    metadataIsValid=True,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-005",
    metadataIsValid=True,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-006",
    metadataIsValid=True,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-007",
    metadataIsValid=True,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-008",
    metadataIsValid=True,
)

# more than one license

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-009",
    metadataIsValid=False,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-010",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-011",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-012",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-013",
    metadataIsValid=False,
)

# text element dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-014",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-015",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-016",
    metadataIsValid=False,
)

# text element class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-017",
    metadataIsValid=True,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-018",
    metadataIsValid=False,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-019",
    metadataIsValid=False,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-020",
    metadataIsValid=True,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-021",
    metadataIsValid=True,
)

# nested div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-022",
    metadataIsValid=True,
)


# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-023",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-024",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-025",
    metadataIsValid=False,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-026",
    metadataIsValid=True,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-027",
    metadataIsValid=True,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-028",
    metadataIsValid=True,
)

# nested span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-029",
    metadataIsValid=True,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-030",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-031",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-032",
    metadataIsValid=False,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-033",
    metadataIsValid=True,
)

# --------------------------------------------
# Metadata Display: Schema Validity: copyright
# --------------------------------------------

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-001",
    metadataIsValid=True,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-002",
    metadataIsValid=True,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-003",
    metadataIsValid=True,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-004",
    metadataIsValid=True,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-005",
    metadataIsValid=True,
)

# more than one copyright

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-006",
    metadataIsValid=False,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-007",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-008",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-009",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-010",
    metadataIsValid=False,
)

# text element with dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-011",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-012",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-013",
    metadataIsValid=False,
)

# text elemet with class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-014",
    metadataIsValid=True,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-015",
    metadataIsValid=False,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-016",
    metadataIsValid=False,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-017",
    metadataIsValid=True,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-018",
    metadataIsValid=True,
)

# nested div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-019",
    metadataIsValid=True,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-020",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-021",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-022",
    metadataIsValid=False,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-023",
    metadataIsValid=True,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-024",
    metadataIsValid=True,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-025",
    metadataIsValid=True,
)

# nested span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-026",
    metadataIsValid=True,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-027",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-028",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-029",
    metadataIsValid=False,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-030",
    metadataIsValid=True,
)

# --------------------------------------------
# Metadata Display: Schema Validity: trademark
# --------------------------------------------

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-001",
    metadataIsValid=True,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-002",
    metadataIsValid=True,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-003",
    metadataIsValid=True,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-004",
    metadataIsValid=True,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-005",
    metadataIsValid=True,
)

# more than one trademark

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-006",
    metadataIsValid=False,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-007",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-008",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-009",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-010",
    metadataIsValid=False,
)

# text element dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-011",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-012",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-013",
    metadataIsValid=False,
)

# text element with class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-014",
    metadataIsValid=True,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-015",
    metadataIsValid=False,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-016",
    metadataIsValid=False,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-017",
    metadataIsValid=True,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-018",
    metadataIsValid=True,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-019",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-020",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-021",
    metadataIsValid=False,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-022",
    metadataIsValid=True,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-023",
    metadataIsValid=True,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-024",
    metadataIsValid=True,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-025",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-026",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-027",
    metadataIsValid=False,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-028",
    metadataIsValid=True,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-001",
    metadataIsValid=True,
)

# duplicate

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-002",
    metadataIsValid=False,
)

# missing name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-003",
    metadataIsValid=False,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-004",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-005",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-006",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-007",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-008",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-009",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-010",
    metadataIsValid=False,
)

# --------------------------------------------
# Metadata Display: Schema Validity: extension
# --------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-001",
    metadataIsValid=True,
)

# valid two extensions

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-002",
    metadataIsValid=True,
)

# valid no id

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-003",
    metadataIsValid=True,
)

# valid no name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-004",
    metadataIsValid=True,
)

# valid one untagged name one tagged name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-005",
    metadataIsValid=True,
)

# valid two tagged names

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-006",
    metadataIsValid=True,
)

# valid more than one item

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-007",
    metadataIsValid=True,
)

# no item

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-008",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-009",
    metadataIsValid=False,
)

# unknown child

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-010",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-011",
    metadataIsValid=False,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - name
# ---------------------------------------------------

# valid no lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-012",
    metadataIsValid=True,
)

# valid xml:lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-013",
    metadataIsValid=True,
)

# valid lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-014",
    metadataIsValid=True,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-015",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-016",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-017",
    metadataIsValid=False,
)

# class atribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-018",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-019",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-020",
    metadataIsValid=False,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - item
# ---------------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-021",
    metadataIsValid=True,
)

# valid multiple languages

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-022",
    metadataIsValid=True,
)

# valid no id

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-023",
    metadataIsValid=True,
)

# valid name no tag and tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-024",
    metadataIsValid=True,
)

# valid name two tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-025",
    metadataIsValid=True,
)

# valid value no tag and tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-026",
    metadataIsValid=True,
)

# valid value two tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-027",
    metadataIsValid=True,
)

# no name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-028",
    metadataIsValid=False,
)

# no value

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-029",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-030",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-031",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-032",
    metadataIsValid=False,
)

# ----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - name
# ----------------------------------------------------------

# valid no lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-033",
    metadataIsValid=True,
)

# valid xml:lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-034",
    metadataIsValid=True,
)

# valid lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-035",
    metadataIsValid=True,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-036",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-037",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-038",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-039",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-040",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-041",
    metadataIsValid=False,
)

# -----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - value
# -----------------------------------------------------------

# valid no lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-042",
    metadataIsValid=True,
)

# valid xml:lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-043",
    metadataIsValid=True,
)

# valid lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-044",
    metadataIsValid=True,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-045",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-046",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-047",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-048",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-049",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-050",
    metadataIsValid=False,
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