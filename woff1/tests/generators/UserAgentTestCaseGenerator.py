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
    title=metadataWellFormed1Title,
    assertion=metadataWellFormed1Description,
    credits=metadataWellFormed1Credits,
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=metadataWellFormed1Metadata,
)

# &

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-002",
    title=metadataWellFormed2Title,
    assertion=metadataWellFormed2Description,
    credits=metadataWellFormed2Credits,
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=metadataWellFormed2Metadata,
)

# mismatched elements

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-003",
    title=metadataWellFormed3Title,
    assertion=metadataWellFormed3Description,
    credits=metadataWellFormed3Credits,
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=metadataWellFormed3Metadata,
)

# unclosed element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-004",
    title=metadataWellFormed4Title,
    assertion=metadataWellFormed4Description,
    credits=metadataWellFormed4Credits,
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=metadataWellFormed4Metadata,
)

# case mismatch

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-005",
    title=metadataWellFormed5Title,
    assertion=metadataWellFormed5Description,
    credits=metadataWellFormed5Credits,
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=metadataWellFormed5Metadata,
)

# more than one root

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-006",
    title=metadataWellFormed6Title,
    assertion=metadataWellFormed6Description,
    credits=metadataWellFormed6Credits,
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=metadataWellFormed6Metadata,
)

# unknown encoding

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-007",
    title=metadataWellFormed7Title,
    assertion=metadataWellFormed7Description,
    credits=metadataWellFormed7Credits,
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=metadataWellFormed7Metadata,
)

# --------------------------
# Metadata Display: Encoding
# --------------------------

# UTF-8

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-001",
    title=metadataEncoding1Title,
    assertion=metadataEncoding1Description,
    credits=metadataEncoding1Credits,
    metadataIsValid=True,
    metadata=metadataEncoding1Metadata,
)

# UTF-16

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-002",
    title=metadataEncoding2Title,
    assertion=metadataEncoding2Description,
    credits=metadataEncoding2Credits,
    metadataIsValid=True,
    metadata=metadataEncoding2Metadata,
)

# Invalid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-003",
    title=metadataEncoding3Title,
    assertion=metadataEncoding3Description,
    credits=metadataEncoding3Credits,
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
    metadata=metadataEncoding3Metadata,
)

# -------------------------------------------
# Metadata Display: Schema Validity: metadata
# -------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-001",
    title=metadataSchemaMetadata1Title,
    assertion=metadataSchemaMetadata1Description,
    credits=metadataSchemaMetadata1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaMetadata1Metadata,
)

# missing version

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-002",
    title=metadataSchemaMetadata2Title,
    assertion=metadataSchemaMetadata2Description,
    credits=metadataSchemaMetadata2Credits,
    metadataIsValid=False,
    metadata=metadataSchemaMetadata2Metadata,
)

# invalid version

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-003",
    title=metadataSchemaMetadata3Title,
    assertion=metadataSchemaMetadata3Description,
    credits=metadataSchemaMetadata3Credits,
    metadataIsValid=False,
    metadata=metadataSchemaMetadata3Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-004",
    title=metadataSchemaMetadata4Title,
    assertion=metadataSchemaMetadata4Description,
    credits=metadataSchemaMetadata4Credits,
    metadataIsValid=False,
    metadata=metadataSchemaMetadata4Metadata,
)

# unknown element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-005",
    title=metadataSchemaMetadata5Title,
    assertion=metadataSchemaMetadata5Description,
    credits=metadataSchemaMetadata5Credits,
    metadataIsValid=False,
    metadata=metadataSchemaMetadata5Metadata,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-001",
    title=metadataSchemaUniqueid1Title,
    assertion=metadataSchemaUniqueid1Description,
    credits=metadataSchemaUniqueid1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaUniqueid1Metadata,
)

# does not exist

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-002",
    title=metadataSchemaUniqueid2Title,
    assertion=metadataSchemaUniqueid2Description,
    credits=metadataSchemaUniqueid2Credits,
    metadataIsValid=True,
    metadata=metadataSchemaUniqueid2Metadata,
)

# duplicate

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-003",
    title=metadataSchemaUniqueid3Title,
    assertion=metadataSchemaUniqueid3Description,
    credits=metadataSchemaUniqueid3Credits,
    metadataIsValid=False,
    metadata=metadataSchemaUniqueid3Metadata,
)

# missing id attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-004",
    title=metadataSchemaUniqueid4Title,
    assertion=metadataSchemaUniqueid4Description,
    credits=metadataSchemaUniqueid4Credits,
    metadataDisplaySpecLink="#conform-metadata-id-required",
    metadataIsValid=False,
    metadata=metadataSchemaUniqueid4Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-005",
    title=metadataSchemaUniqueid5Title,
    assertion=metadataSchemaUniqueid5Description,
    credits=metadataSchemaUniqueid5Credits,
    metadataIsValid=False,
    metadata=metadataSchemaUniqueid5Metadata,
)

# unknown child

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-006",
    title=metadataSchemaUniqueid6Title,
    assertion=metadataSchemaUniqueid6Description,
    credits=metadataSchemaUniqueid6Credits,
    metadataIsValid=False,
    metadata=metadataSchemaUniqueid6Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-007",
    title=metadataSchemaUniqueid7Title,
    assertion=metadataSchemaUniqueid7Description,
    credits=metadataSchemaUniqueid7Credits,
    metadataIsValid=False,
    metadata=metadataSchemaUniqueid7Metadata,
)

# -----------------------------------------
# Metadata Display: Schema Validity: vendor
# -----------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-001",
    title=metadataSchemaVendor1Title,
    assertion=metadataSchemaVendor1Description,
    credits=metadataSchemaVendor1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaVendor1Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-002",
    title=metadataSchemaVendor2Title,
    assertion=metadataSchemaVendor2Description,
    credits=metadataSchemaVendor2Credits,
    metadataIsValid=True,
    metadata=metadataSchemaVendor2Metadata,
)

# does not exist

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-003",
    title=metadataSchemaVendor3Title,
    assertion=metadataSchemaVendor3Description,
    credits=metadataSchemaVendor3Credits,
    metadataIsValid=True,
    metadata=metadataSchemaVendor3Metadata,
)

# duplicate

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-004",
    title=metadataSchemaVendor4Title,
    assertion=metadataSchemaVendor4Description,
    credits=metadataSchemaVendor4Credits,
    metadataIsValid=False,
    metadata=metadataSchemaVendor4Metadata,
)

# missing name attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-005",
    title=metadataSchemaVendor5Title,
    assertion=metadataSchemaVendor5Description,
    credits=metadataSchemaVendor5Credits,
    metadataDisplaySpecLink="#conform-metadata-vendor-required",
    metadataIsValid=False,
    metadata=metadataSchemaVendor5Metadata,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-006",
    title=metadataSchemaVendor6Title,
    assertion=metadataSchemaVendor6Description,
    credits=metadataSchemaVendor6Credits,
    metadataIsValid=True,
    metadata=metadataSchemaVendor6Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-007",
    title=metadataSchemaVendor7Title,
    assertion=metadataSchemaVendor7Description,
    credits=metadataSchemaVendor7Credits,
    metadataIsValid=True,
    metadata=metadataSchemaVendor7Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-008",
    title=metadataSchemaVendor8Title,
    assertion=metadataSchemaVendor8Description,
    credits=metadataSchemaVendor8Credits,
    metadataIsValid=False,
    metadata=metadataSchemaVendor8Metadata,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-009",
    title=metadataSchemaVendor9Title,
    assertion=metadataSchemaVendor9Description,
    credits=metadataSchemaVendor9Credits,
    metadataIsValid=True,
    metadata=metadataSchemaVendor9Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-010",
    title=metadataSchemaVendor10Title,
    assertion=metadataSchemaVendor10Description,
    credits=metadataSchemaVendor10Credits,
    metadataIsValid=False,
    metadata=metadataSchemaVendor10Metadata,
)

# unknown child

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-011",
    title=metadataSchemaVendor11Title,
    assertion=metadataSchemaVendor11Description,
    credits=metadataSchemaVendor11Credits,
    metadataIsValid=False,
    metadata=metadataSchemaVendor11Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-012",
    title=metadataSchemaVendor12Title,
    assertion=metadataSchemaVendor12Description,
    credits=metadataSchemaVendor12Credits,
    metadataIsValid=False,
    metadata=metadataSchemaVendor12Metadata,
)

# ------------------------------------------
# Metadata Display: Schema Validity: credits
# ------------------------------------------

# valid - single credit element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-001",
    title=metadataSchemaCredits1Title,
    assertion=metadataSchemaCredits1Description,
    credits=metadataSchemaCredits1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCredits1Metadata,
)

# valid - multiple credit elements

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-002",
    title=metadataSchemaCredits2Title,
    assertion=metadataSchemaCredits2Description,
    credits=metadataSchemaCredits2Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCredits2Metadata,
)

# missing credit element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-003",
    title=metadataSchemaCredits3Title,
    assertion=metadataSchemaCredits3Description,
    credits=metadataSchemaCredits3Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredits3Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-004",
    title=metadataSchemaCredits4Title,
    assertion=metadataSchemaCredits4Description,
    credits=metadataSchemaCredits4Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredits4Metadata,
)

# unknown element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-005",
    title=metadataSchemaCredits5Title,
    assertion=metadataSchemaCredits5Description,
    credits=metadataSchemaCredits5Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredits5Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-006",
    title=metadataSchemaCredits6Title,
    assertion=metadataSchemaCredits6Description,
    credits=metadataSchemaCredits6Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredits6Metadata,
)

# multiple credits

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-007",
    title=metadataSchemaCredits7Title,
    assertion=metadataSchemaCredits7Description,
    credits=metadataSchemaCredits7Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredits7Metadata,
)

# -----------------------------------------
# Metadata Display: Schema Validity: credit
# -----------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-001",
    title=metadataSchemaCredit1Title,
    assertion=metadataSchemaCredit1Description,
    credits=metadataSchemaCredit1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCredit1Metadata,
)

# valid no url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-002",
    title=metadataSchemaCredit2Title,
    assertion=metadataSchemaCredit2Description,
    credits=metadataSchemaCredit2Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCredit2Metadata,
)

# valid no role

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-003",
    title=metadataSchemaCredit3Title,
    assertion=metadataSchemaCredit3Description,
    credits=metadataSchemaCredit3Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCredit3Metadata,
)

# no name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-004",
    title=metadataSchemaCredit4Title,
    assertion=metadataSchemaCredit4Description,
    credits=metadataSchemaCredit4Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredit4Metadata,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-005",
    title=metadataSchemaCredit5Title,
    assertion=metadataSchemaCredit5Description,
    credits=metadataSchemaCredit5Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCredit5Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-006",
    title=metadataSchemaCredit6Title,
    assertion=metadataSchemaCredit6Description,
    credits=metadataSchemaCredit6Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCredit6Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-007",
    title=metadataSchemaCredit7Title,
    assertion=metadataSchemaCredit7Description,
    credits=metadataSchemaCredit7Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredit7Metadata,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-008",
    title=metadataSchemaCredit8Title,
    assertion=metadataSchemaCredit8Description,
    credits=metadataSchemaCredit8Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCredit8Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-009",
    title=metadataSchemaCredit9Title,
    assertion=metadataSchemaCredit9Description,
    credits=metadataSchemaCredit9Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredit9Metadata,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-010",
    title=metadataSchemaCredit10Title,
    assertion=metadataSchemaCredit10Description,
    credits=metadataSchemaCredit10Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredit10Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-011",
    title=metadataSchemaCredit11Title,
    assertion=metadataSchemaCredit11Description,
    credits=metadataSchemaCredit11Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCredit11Metadata,
)

# ----------------------------------------------
# Metadata Display: Schema Validity: description
# ----------------------------------------------

# valid with url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-001",
    title=metadataSchemaDescription1Title,
    assertion=metadataSchemaDescription1Description,
    credits=metadataSchemaDescription1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription1Metadata,
)

# valid without url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-002",
    title=metadataSchemaDescription2Title,
    assertion=metadataSchemaDescription2Description,
    credits=metadataSchemaDescription2Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription2Metadata,
)

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-003",
    title=metadataSchemaDescription3Title,
    assertion=metadataSchemaDescription3Description,
    credits=metadataSchemaDescription3Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription3Metadata,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-004",
    title=metadataSchemaDescription4Title,
    assertion=metadataSchemaDescription4Description,
    credits=metadataSchemaDescription4Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription4Metadata,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-005",
    title=metadataSchemaDescription5Title,
    assertion=metadataSchemaDescription5Description,
    credits=metadataSchemaDescription5Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription5Metadata,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-006",
    title=metadataSchemaDescription6Title,
    assertion=metadataSchemaDescription6Description,
    credits=metadataSchemaDescription6Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription6Metadata,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-007",
    title=metadataSchemaDescription7Title,
    assertion=metadataSchemaDescription7Description,
    credits=metadataSchemaDescription7Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription7Metadata,
)

# more than one description

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-008",
    title=metadataSchemaDescription8Title,
    assertion=metadataSchemaDescription8Description,
    credits=metadataSchemaDescription8Credits,
    metadataIsValid=False,
    metadata=metadataSchemaDescription8Metadata,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-009",
    title=metadataSchemaDescription9Title,
    assertion=metadataSchemaDescription9Description,
    credits=metadataSchemaDescription9Credits,
    metadataIsValid=False,
    metadata=metadataSchemaDescription9Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-010",
    title=metadataSchemaDescription10Title,
    assertion=metadataSchemaDescription10Description,
    credits=metadataSchemaDescription10Credits,
    metadataIsValid=False,
    metadata=metadataSchemaDescription10Metadata,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-011",
    title=metadataSchemaDescription11Title,
    assertion=metadataSchemaDescription11Description,
    credits=metadataSchemaDescription11Credits,
    metadataIsValid=False,
    metadata=metadataSchemaDescription11Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-012",
    title=metadataSchemaDescription12Title,
    assertion=metadataSchemaDescription12Description,
    credits=metadataSchemaDescription12Credits,
    metadataIsValid=False,
    metadata=metadataSchemaDescription12Metadata,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-013",
    title=metadataSchemaDescription13Title,
    assertion=metadataSchemaDescription13Description,
    credits=metadataSchemaDescription13Credits,
    metadataIsValid=False,
    metadata=metadataSchemaDescription13Metadata,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-014",
    title=metadataSchemaDescription14Title,
    assertion=metadataSchemaDescription14Description,
    credits=metadataSchemaDescription14Credits,
    metadataIsValid=False,
    metadata=metadataSchemaDescription14Metadata,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-015",
    title=metadataSchemaDescription15Title,
    assertion=metadataSchemaDescription15Description,
    credits=metadataSchemaDescription15Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription15Metadata,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-016",
    title=metadataSchemaDescription16Title,
    assertion=metadataSchemaDescription16Description,
    credits=metadataSchemaDescription16Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription16Metadata,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-017",
    title=metadataSchemaDescription17Title,
    assertion=metadataSchemaDescription17Description,
    credits=metadataSchemaDescription17Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription17Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-018",
    title=metadataSchemaDescription18Title,
    assertion=metadataSchemaDescription18Description,
    credits=metadataSchemaDescription18Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription18Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-019",
    title=metadataSchemaDescription19Title,
    assertion=metadataSchemaDescription19Description,
    credits=metadataSchemaDescription19Credits,
    metadataIsValid=False,
    metadata=metadataSchemaDescription19Metadata,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-020",
    title=metadataSchemaDescription20Title,
    assertion=metadataSchemaDescription20Description,
    credits=metadataSchemaDescription20Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription20Metadata,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-021",
    title=metadataSchemaDescription21Title,
    assertion=metadataSchemaDescription21Description,
    credits=metadataSchemaDescription21Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription21Metadata,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-022",
    title=metadataSchemaDescription22Title,
    assertion=metadataSchemaDescription22Description,
    credits=metadataSchemaDescription22Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription22Metadata,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-023",
    title=metadataSchemaDescription23Title,
    assertion=metadataSchemaDescription23Description,
    credits=metadataSchemaDescription23Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription23Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-024",
    title=metadataSchemaDescription24Title,
    assertion=metadataSchemaDescription24Description,
    credits=metadataSchemaDescription24Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription24Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-025",
    title=metadataSchemaDescription25Title,
    assertion=metadataSchemaDescription25Description,
    credits=metadataSchemaDescription25Credits,
    metadataIsValid=False,
    metadata=metadataSchemaDescription25Metadata,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-026",
    title=metadataSchemaDescription26Title,
    assertion=metadataSchemaDescription26Description,
    credits=metadataSchemaDescription26Credits,
    metadataIsValid=True,
    metadata=metadataSchemaDescription26Metadata,
)

# ------------------------------------------
# Metadata Display: Schema Validity: license
# ------------------------------------------

# valid with url and license

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-001",
    title=metadataSchemaLicense1Title,
    assertion=metadataSchemaLicense1Description,
    credits=metadataSchemaLicense1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense1Metadata,
)

# valid no url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-002",
    title=metadataSchemaLicense2Title,
    assertion=metadataSchemaLicense2Description,
    credits=metadataSchemaLicense2Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense2Metadata,
)

# valid no id

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-003",
    title=metadataSchemaLicense3Title,
    assertion=metadataSchemaLicense3Description,
    credits=metadataSchemaLicense3Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense3Metadata,
)

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-004",
    title=metadataSchemaLicense4Title,
    assertion=metadataSchemaLicense4Description,
    credits=metadataSchemaLicense4Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense4Metadata,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-005",
    title=metadataSchemaLicense5Title,
    assertion=metadataSchemaLicense5Description,
    credits=metadataSchemaLicense5Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense5Metadata,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-006",
    title=metadataSchemaLicense6Title,
    assertion=metadataSchemaLicense6Description,
    credits=metadataSchemaLicense6Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense6Metadata,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-007",
    title=metadataSchemaLicense7Title,
    assertion=metadataSchemaLicense7Description,
    credits=metadataSchemaLicense7Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense7Metadata,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-008",
    title=metadataSchemaLicense8Title,
    assertion=metadataSchemaLicense8Description,
    credits=metadataSchemaLicense8Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense8Metadata,
)

# more than one license

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-009",
    title=metadataSchemaLicense9Title,
    assertion=metadataSchemaLicense9Description,
    credits=metadataSchemaLicense9Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicense9Metadata,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-010",
    title=metadataSchemaLicense10Title,
    assertion=metadataSchemaLicense10Description,
    credits=metadataSchemaLicense10Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicense10Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-011",
    title=metadataSchemaLicense11Title,
    assertion=metadataSchemaLicense11Description,
    credits=metadataSchemaLicense11Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicense11Metadata,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-012",
    title=metadataSchemaLicense12Title,
    assertion=metadataSchemaLicense12Description,
    credits=metadataSchemaLicense12Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicense12Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-013",
    title=metadataSchemaLicense13Title,
    assertion=metadataSchemaLicense13Description,
    credits=metadataSchemaLicense13Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicense13Metadata,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-014",
    title=metadataSchemaLicense14Title,
    assertion=metadataSchemaLicense14Description,
    credits=metadataSchemaLicense14Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicense14Metadata,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-015",
    title=metadataSchemaLicense15Title,
    assertion=metadataSchemaLicense15Description,
    credits=metadataSchemaLicense15Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicense15Metadata,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-016",
    title=metadataSchemaLicense16Title,
    assertion=metadataSchemaLicense16Description,
    credits=metadataSchemaLicense16Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense16Metadata,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-017",
    title=metadataSchemaLicense17Title,
    assertion=metadataSchemaLicense17Description,
    credits=metadataSchemaLicense17Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense17Metadata,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-018",
    title=metadataSchemaLicense18Title,
    assertion=metadataSchemaLicense18Description,
    credits=metadataSchemaLicense18Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense18Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-019",
    title=metadataSchemaLicense19Title,
    assertion=metadataSchemaLicense19Description,
    credits=metadataSchemaLicense19Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense19Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-020",
    title=metadataSchemaLicense20Title,
    assertion=metadataSchemaLicense20Description,
    credits=metadataSchemaLicense20Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicense20Metadata,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-021",
    title=metadataSchemaLicense21Title,
    assertion=metadataSchemaLicense21Description,
    credits=metadataSchemaLicense21Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense21Metadata,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-022",
    title=metadataSchemaLicense22Title,
    assertion=metadataSchemaLicense22Description,
    credits=metadataSchemaLicense22Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense22Metadata,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-023",
    title=metadataSchemaLicense23Title,
    assertion=metadataSchemaLicense23Description,
    credits=metadataSchemaLicense23Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense23Metadata,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-024",
    title=metadataSchemaLicense24Title,
    assertion=metadataSchemaLicense24Description,
    credits=metadataSchemaLicense24Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense24Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-025",
    title=metadataSchemaLicense25Title,
    assertion=metadataSchemaLicense25Description,
    credits=metadataSchemaLicense25Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense25Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-026",
    title=metadataSchemaLicense26Title,
    assertion=metadataSchemaLicense26Description,
    credits=metadataSchemaLicense26Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicense26Metadata,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-027",
    title=metadataSchemaLicense27Title,
    assertion=metadataSchemaLicense27Description,
    credits=metadataSchemaLicense27Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicense27Metadata,
)

# --------------------------------------------
# Metadata Display: Schema Validity: copyright
# --------------------------------------------

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-001",
    title=metadataSchemaCopyright1Title,
    assertion=metadataSchemaCopyright1Description,
    credits=metadataSchemaCopyright1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright1Metadata,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-002",
    title=metadataSchemaCopyright2Title,
    assertion=metadataSchemaCopyright2Description,
    credits=metadataSchemaCopyright2Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright2Metadata,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-003",
    title=metadataSchemaCopyright3Title,
    assertion=metadataSchemaCopyright3Description,
    credits=metadataSchemaCopyright3Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright3Metadata,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-004",
    title=metadataSchemaCopyright4Title,
    assertion=metadataSchemaCopyright4Description,
    credits=metadataSchemaCopyright4Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright4Metadata,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-005",
    title=metadataSchemaCopyright5Title,
    assertion=metadataSchemaCopyright5Description,
    credits=metadataSchemaCopyright5Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright5Metadata,
)

# more than one copyright

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-006",
    title=metadataSchemaCopyright6Title,
    assertion=metadataSchemaCopyright6Description,
    credits=metadataSchemaCopyright6Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCopyright6Metadata,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-007",
    title=metadataSchemaCopyright7Title,
    assertion=metadataSchemaCopyright7Description,
    credits=metadataSchemaCopyright7Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCopyright7Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-008",
    title=metadataSchemaCopyright8Title,
    assertion=metadataSchemaCopyright8Description,
    credits=metadataSchemaCopyright8Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCopyright8Metadata,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-009",
    title=metadataSchemaCopyright9Title,
    assertion=metadataSchemaCopyright9Description,
    credits=metadataSchemaCopyright9Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCopyright9Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-010",
    title=metadataSchemaCopyright10Title,
    assertion=metadataSchemaCopyright10Description,
    credits=metadataSchemaCopyright10Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCopyright10Metadata,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-011",
    title=metadataSchemaCopyright11Title,
    assertion=metadataSchemaCopyright11Description,
    credits=metadataSchemaCopyright11Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCopyright11Metadata,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-012",
    title=metadataSchemaCopyright12Title,
    assertion=metadataSchemaCopyright12Description,
    credits=metadataSchemaCopyright12Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCopyright12Metadata,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-013",
    title=metadataSchemaCopyright13Title,
    assertion=metadataSchemaCopyright13Description,
    credits=metadataSchemaCopyright13Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright13Metadata,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-014",
    title=metadataSchemaCopyright14Title,
    assertion=metadataSchemaCopyright14Description,
    credits=metadataSchemaCopyright14Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright14Metadata,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-015",
    title=metadataSchemaCopyright15Title,
    assertion=metadataSchemaCopyright15Description,
    credits=metadataSchemaCopyright15Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright15Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-016",
    title=metadataSchemaCopyright16Title,
    assertion=metadataSchemaCopyright16Description,
    credits=metadataSchemaCopyright16Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright16Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-017",
    title=metadataSchemaCopyright17Title,
    assertion=metadataSchemaCopyright17Description,
    credits=metadataSchemaCopyright17Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCopyright17Metadata,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-018",
    title=metadataSchemaCopyright18Title,
    assertion=metadataSchemaCopyright18Description,
    credits=metadataSchemaCopyright18Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright18Metadata,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-019",
    title=metadataSchemaCopyright19Title,
    assertion=metadataSchemaCopyright19Description,
    credits=metadataSchemaCopyright19Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright19Metadata,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-020",
    title=metadataSchemaCopyright20Title,
    assertion=metadataSchemaCopyright20Description,
    credits=metadataSchemaCopyright20Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright20Metadata,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-021",
    title=metadataSchemaCopyright21Title,
    assertion=metadataSchemaCopyright21Description,
    credits=metadataSchemaCopyright21Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright21Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-022",
    title=metadataSchemaCopyright22Title,
    assertion=metadataSchemaCopyright22Description,
    credits=metadataSchemaCopyright22Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright22Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-023",
    title=metadataSchemaCopyright23Title,
    assertion=metadataSchemaCopyright23Description,
    credits=metadataSchemaCopyright23Credits,
    metadataIsValid=False,
    metadata=metadataSchemaCopyright23Metadata,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-024",
    title=metadataSchemaCopyright24Title,
    assertion=metadataSchemaCopyright24Description,
    credits=metadataSchemaCopyright24Credits,
    metadataIsValid=True,
    metadata=metadataSchemaCopyright24Metadata,
)

# --------------------------------------------
# Metadata Display: Schema Validity: trademark
# --------------------------------------------

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-001",
    title=metadataSchemaTrademark1Title,
    assertion=metadataSchemaTrademark1Description,
    credits=metadataSchemaTrademark1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark1Metadata,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-002",
    title=metadataSchemaTrademark2Title,
    assertion=metadataSchemaTrademark2Description,
    credits=metadataSchemaTrademark2Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark2Metadata,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-003",
    title=metadataSchemaTrademark3Title,
    assertion=metadataSchemaTrademark3Description,
    credits=metadataSchemaTrademark3Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark3Metadata,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-004",
    title=metadataSchemaTrademark4Title,
    assertion=metadataSchemaTrademark4Description,
    credits=metadataSchemaTrademark4Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark4Metadata,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-005",
    title=metadataSchemaTrademark5Title,
    assertion=metadataSchemaTrademark5Description,
    credits=metadataSchemaTrademark5Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark5Metadata,
)

# more than one trademark

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-006",
    title=metadataSchemaTrademark6Title,
    assertion=metadataSchemaTrademark6Description,
    credits=metadataSchemaTrademark6Credits,
    metadataIsValid=False,
    metadata=metadataSchemaTrademark6Metadata,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-007",
    title=metadataSchemaTrademark7Title,
    assertion=metadataSchemaTrademark7Description,
    credits=metadataSchemaTrademark7Credits,
    metadataIsValid=False,
    metadata=metadataSchemaTrademark7Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-008",
    title=metadataSchemaTrademark8Title,
    assertion=metadataSchemaTrademark8Description,
    credits=metadataSchemaTrademark8Credits,
    metadataIsValid=False,
    metadata=metadataSchemaTrademark8Metadata,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-009",
    title=metadataSchemaTrademark9Title,
    assertion=metadataSchemaTrademark9Description,
    credits=metadataSchemaTrademark9Credits,
    metadataIsValid=False,
    metadata=metadataSchemaTrademark9Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-010",
    title=metadataSchemaTrademark10Title,
    assertion=metadataSchemaTrademark10Description,
    credits=metadataSchemaTrademark10Credits,
    metadataIsValid=False,
    metadata=metadataSchemaTrademark10Metadata,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-011",
    title=metadataSchemaTrademark11Title,
    assertion=metadataSchemaTrademark11Description,
    credits=metadataSchemaTrademark11Credits,
    metadataIsValid=False,
    metadata=metadataSchemaTrademark11Metadata,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-012",
    title=metadataSchemaTrademark12Title,
    assertion=metadataSchemaTrademark12Description,
    credits=metadataSchemaTrademark12Credits,
    metadataIsValid=False,
    metadata=metadataSchemaTrademark12Metadata,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-013",
    title=metadataSchemaTrademark13Title,
    assertion=metadataSchemaTrademark13Description,
    credits=metadataSchemaTrademark13Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark13Metadata,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-014",
    title=metadataSchemaTrademark14Title,
    assertion=metadataSchemaTrademark14Description,
    credits=metadataSchemaTrademark14Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark14Metadata,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-015",
    title=metadataSchemaTrademark15Title,
    assertion=metadataSchemaTrademark15Description,
    credits=metadataSchemaTrademark15Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark15Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-016",
    title=metadataSchemaTrademark16Title,
    assertion=metadataSchemaTrademark16Description,
    credits=metadataSchemaTrademark16Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark16Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-017",
    title=metadataSchemaTrademark17Title,
    assertion=metadataSchemaTrademark17Description,
    credits=metadataSchemaTrademark17Credits,
    metadataIsValid=False,
    metadata=metadataSchemaTrademark17Metadata,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-018",
    title=metadataSchemaTrademark18Title,
    assertion=metadataSchemaTrademark18Description,
    credits=metadataSchemaTrademark18Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark18Metadata,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-019",
    title=metadataSchemaTrademark19Title,
    assertion=metadataSchemaTrademark19Description,
    credits=metadataSchemaTrademark19Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark19Metadata,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-020",
    title=metadataSchemaTrademark20Title,
    assertion=metadataSchemaTrademark20Description,
    credits=metadataSchemaTrademark20Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark20Metadata,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-021",
    title=metadataSchemaTrademark21Title,
    assertion=metadataSchemaTrademark21Description,
    credits=metadataSchemaTrademark21Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark21Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-022",
    title=metadataSchemaTrademark22Title,
    assertion=metadataSchemaTrademark22Description,
    credits=metadataSchemaTrademark22Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark22Metadata,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-023",
    title=metadataSchemaTrademark23Title,
    assertion=metadataSchemaTrademark23Description,
    credits=metadataSchemaTrademark23Credits,
    metadataIsValid=False,
    metadata=metadataSchemaTrademark23Metadata,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-024",
    title=metadataSchemaTrademark24Title,
    assertion=metadataSchemaTrademark24Description,
    credits=metadataSchemaTrademark24Credits,
    metadataIsValid=True,
    metadata=metadataSchemaTrademark24Metadata,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-001",
    title=metadataSchemaLicensee1Title,
    assertion=metadataSchemaLicensee1Description,
    credits=metadataSchemaLicensee1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaLicensee1Metadata,
)

# duplicate

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-002",
    title=metadataSchemaLicensee2Title,
    assertion=metadataSchemaLicensee2Description,
    credits=metadataSchemaLicensee2Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicensee2Metadata,
)

# missing name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-003",
    title=metadataSchemaLicensee3Title,
    assertion=metadataSchemaLicensee3Description,
    credits=metadataSchemaLicensee3Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicensee3Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-004",
    title=metadataSchemaLicensee4Title,
    assertion=metadataSchemaLicensee4Description,
    credits=metadataSchemaLicensee4Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicensee4Metadata,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-005",
    title=metadataSchemaLicensee5Title,
    assertion=metadataSchemaLicensee5Description,
    credits=metadataSchemaLicensee5Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicensee5Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-006",
    title=metadataSchemaLicensee6Title,
    assertion=metadataSchemaLicensee6Description,
    credits=metadataSchemaLicensee6Credits,
    metadataIsValid=False,
    metadata=metadataSchemaLicensee6Metadata,
)

# --------------------------------------------
# Metadata Display: Schema Validity: extension
# --------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-001",
    title=metadataSchemaExtension1Title,
    assertion=metadataSchemaExtension1Description,
    credits=metadataSchemaExtension1Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension1Metadata,
)

# valid two extensions

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-002",
    title=metadataSchemaExtension2Title,
    assertion=metadataSchemaExtension2Description,
    credits=metadataSchemaExtension2Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension2Metadata,
)

# valid no id

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-003",
    title=metadataSchemaExtension3Title,
    assertion=metadataSchemaExtension3Description,
    credits=metadataSchemaExtension3Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension3Metadata,
)

# valid no name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-004",
    title=metadataSchemaExtension4Title,
    assertion=metadataSchemaExtension4Description,
    credits=metadataSchemaExtension4Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension4Metadata,
)

# valid tagged name using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-005",
    title=metadataSchemaExtension5Title,
    assertion=metadataSchemaExtension5Description,
    credits=metadataSchemaExtension5Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension5Metadata,
)

# valid one untagged name one tagged name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-006",
    title=metadataSchemaExtension6Title,
    assertion=metadataSchemaExtension6Description,
    credits=metadataSchemaExtension6Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension6Metadata,
)

# valid two tagged names

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-007",
    title=metadataSchemaExtension7Title,
    assertion=metadataSchemaExtension7Description,
    credits=metadataSchemaExtension7Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension7Metadata,
)

# valid more than one item

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-008",
    title=metadataSchemaExtension8Title,
    assertion=metadataSchemaExtension8Description,
    credits=metadataSchemaExtension8Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension8Metadata,
)

# no item

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-009",
    title=metadataSchemaExtension9Title,
    assertion=metadataSchemaExtension9Description,
    credits=metadataSchemaExtension9Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension9Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-010",
    title=metadataSchemaExtension10Title,
    assertion=metadataSchemaExtension10Description,
    credits=metadataSchemaExtension10Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension10Metadata,
)

# unknown child

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-011",
    title=metadataSchemaExtension11Title,
    assertion=metadataSchemaExtension11Description,
    credits=metadataSchemaExtension11Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension11Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-012",
    title=metadataSchemaExtension12Title,
    assertion=metadataSchemaExtension12Description,
    credits=metadataSchemaExtension12Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension12Metadata,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - item
# ---------------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-013",
    title=metadataSchemaExtension13Title,
    assertion=metadataSchemaExtension13Description,
    credits=metadataSchemaExtension13Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension13Metadata,
)

# valid multiple languages

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-014",
    title=metadataSchemaExtension14Title,
    assertion=metadataSchemaExtension14Description,
    credits=metadataSchemaExtension14Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension14Metadata,
)

# valid no id

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-015",
    title=metadataSchemaExtension15Title,
    assertion=metadataSchemaExtension15Description,
    credits=metadataSchemaExtension15Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension15Metadata,
)

# valid name no tag and tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-016",
    title=metadataSchemaExtension16Title,
    assertion=metadataSchemaExtension16Description,
    credits=metadataSchemaExtension16Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension16Metadata,
)

# valid name two tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-017",
    title=metadataSchemaExtension17Title,
    assertion=metadataSchemaExtension17Description,
    credits=metadataSchemaExtension17Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension17Metadata,
)

# valid value no tag and tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-018",
    title=metadataSchemaExtension18Title,
    assertion=metadataSchemaExtension18Description,
    credits=metadataSchemaExtension18Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension18Metadata,
)

# valid value two tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-019",
    title=metadataSchemaExtension19Title,
    assertion=metadataSchemaExtension19Description,
    credits=metadataSchemaExtension19Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension19Metadata,
)

# no name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-020",
    title=metadataSchemaExtension20Title,
    assertion=metadataSchemaExtension20Description,
    credits=metadataSchemaExtension20Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension20Metadata,
)

# no value

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-021",
    title=metadataSchemaExtension21Title,
    assertion=metadataSchemaExtension21Description,
    credits=metadataSchemaExtension21Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension21Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-022",
    title=metadataSchemaExtension22Title,
    assertion=metadataSchemaExtension22Description,
    credits=metadataSchemaExtension22Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension22Metadata,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-023",
    title=metadataSchemaExtension23Title,
    assertion=metadataSchemaExtension23Description,
    credits=metadataSchemaExtension23Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension23Metadata,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-024",
    title=metadataSchemaExtension24Title,
    assertion=metadataSchemaExtension24Description,
    credits=metadataSchemaExtension24Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension24Metadata,
)

# ----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - name
# ----------------------------------------------------------

# valid no lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-025",
    title=metadataSchemaExtension25Title,
    assertion=metadataSchemaExtension25Description,
    credits=metadataSchemaExtension25Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension25Metadata,
)

# valid xml:lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-026",
    title=metadataSchemaExtension26Title,
    assertion=metadataSchemaExtension26Description,
    credits=metadataSchemaExtension26Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension26Metadata,
)

# valid lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-027",
    title=metadataSchemaExtension27Title,
    assertion=metadataSchemaExtension27Description,
    credits=metadataSchemaExtension27Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension27Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-028",
    title=metadataSchemaExtension28Title,
    assertion=metadataSchemaExtension28Description,
    credits=metadataSchemaExtension28Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension28Metadata,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-029",
    title=metadataSchemaExtension29Title,
    assertion=metadataSchemaExtension29Description,
    credits=metadataSchemaExtension29Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension29Metadata,
)

# -----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - value
# -----------------------------------------------------------

# valid no lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-030",
    title=metadataSchemaExtension30Title,
    assertion=metadataSchemaExtension30Description,
    credits=metadataSchemaExtension30Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension30Metadata,
)

# valid xml:lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-031",
    title=metadataSchemaExtension31Title,
    assertion=metadataSchemaExtension31Description,
    credits=metadataSchemaExtension31Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension31Metadata,
)

# valid lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-032",
    title=metadataSchemaExtension32Title,
    assertion=metadataSchemaExtension32Description,
    credits=metadataSchemaExtension32Credits,
    metadataIsValid=True,
    metadata=metadataSchemaExtension32Metadata,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-033",
    title=metadataSchemaExtension33Title,
    assertion=metadataSchemaExtension33Description,
    credits=metadataSchemaExtension33Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension33Metadata,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-034",
    title=metadataSchemaExtension34Title,
    assertion=metadataSchemaExtension34Description,
    credits=metadataSchemaExtension34Credits,
    metadataIsValid=False,
    metadata=metadataSchemaExtension34Metadata,
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