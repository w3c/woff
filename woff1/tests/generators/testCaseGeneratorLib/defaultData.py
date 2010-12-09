"""
Default data for the test cases.
"""

import zlib
from copy import deepcopy
from fontTools.ttLib.sfnt import sfntDirectoryFormat, sfntDirectorySize, sfntDirectoryEntryFormat, sfntDirectoryEntrySize
from sfnt import getSFNTData
from woff import woffHeaderSize, woffDirectoryEntrySize
from paths import sfntCFFSourcePath, sfntTTFSourcePath
from utilities import calcPaddingLength, calcTableChecksum

# ---------
# SFNT Data
# ---------

originalSFNTChecksums = {}

sfntTTFTableData, sfntTTFTableOrder, sfntTTFTableChecksums = getSFNTData(sfntTTFSourcePath)
for tag, checksum in sfntTTFTableChecksums.items():
    data = sfntTTFTableData[tag]
    if data in originalSFNTChecksums:
        assert originalSFNTChecksums[data] == checksum
    originalSFNTChecksums[data] = checksum

sfntCFFTableData, sfntCFFTableOrder, sfntCFFTableChecksums = getSFNTData(sfntCFFSourcePath)
for tag, checksum in sfntCFFTableChecksums.items():
    data = sfntCFFTableData[tag]
    if data in originalSFNTChecksums:
        assert originalSFNTChecksums[data] == checksum
    originalSFNTChecksums[data] = checksum

# --------
# Metadata
# --------

testDataWOFFMetadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
	<uniqueid id="org.w3.webfonts.wofftest" />
	<vendor name="Test Vendor" url="http://w3c.org/Fonts" />
	<credits>
		<credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
		<credit name="Credit 2" role="Role 2" url="http://w3c.org/Fonts" />
	</credits>
	<description url="http://w3c.org/Fonts">
		<text>
			Description without language.
		</text>
		<text lang="en">
			Description with "en" language.
		</text>
		<text lang="fr">
			Description with "fr" language.
		</text>
	</description>
	<license url="http://w3c.org/Fonts" id="License ID">
		<text>
			License without language.
		</text>
		<text lang="en">
			License with "en" language.
		</text>
		<text lang="fr">
			License with "fr" language.
		</text>
	</license>
	<copyright>
		<text>
			Copyright without language.
		</text>
		<text lang="en">
			Copyright with "en" language.
		</text>
		<text lang="fr">
			Copyright with "fr" language.
		</text>
	</copyright>
	<trademark>
		<text>
			Trademark without language.
		</text>
		<text lang="en">
			Trademark with "en" language.
		</text>
		<text lang="fr">
			Trademark with "fr" language.
		</text>
	</trademark>
	<licensee name="Licensee Name" />
	<extension id="Extension 1">
		<name>Name Without Language</name>
		<name lang="en">Name With "en" Language</name>
		<name lang="fr">Name With "fr" Language</name>
		<item id="Extension 1 - Item 1 ID">
			<name>Name Without Language</name>
			<name lang="en">Name With "en" Language</name>
			<name lang="fr">Name With "fr" Language</name>
			<value>Value Without Language</value>
			<value lang="en">Value With "en" Language</value>
			<value lang="fr">Value With "fr" Language</value>
		</item>
		<item id="Extension 1 - Item 2 ID">
			<name>Name Without Language</name>
			<name lang="en">Name With "en" Language</name>
			<name lang="fr">Name With "fr" Language</name>
			<value>Value Without Language</value>
			<value lang="en">Value With "en" Language</value>
			<value lang="fr">Value With "fr" Language</value>
		</item>
	</extension>
	<extension id="Extension 2">
		<name>Name Without Language</name>
		<name lang="en">Name With "en" Language</name>
		<name lang="fr">Name With "fr" Language</name>
		<item id="Extension 2 - Item 1 ID">
			<name>Name Without Language</name>
			<name lang="en">Name With "en" Language</name>
			<name lang="fr">Name With "fr" Language</name>
			<value>Value Without Language</value>
			<value lang="en">Value With "en" Language</value>
			<value lang="fr">Value With "fr" Language</value>
		</item>
		<item id="Extension 2 - Item 2 ID">
			<name>Name Without Language</name>
			<name lang="en">Name With "en" Language</name>
			<name lang="fr">Name With "fr" Language</name>
			<value>Value Without Language</value>
			<value lang="en">Value With "en" Language</value>
			<value lang="fr">Value With "fr" Language</value>
		</item>
	</extension>
</metadata>
""".strip()

# ------------
# Private Data
# ------------

testDataWOFFPrivateData = "\0" * 100

# -----------------------
# Default Data Structures
# -----------------------

testDataWOFFHeader = dict(
    signature="wOFF",
    flavor="OTTO",
    length=0,
    reserved=0,
    numTables=0,
    totalSfntSize=0,
    majorVersion=0,
    minorVersion=0,
    metaOffset=0,
    metaLength=0,
    metaOrigLength=0,
    privOffset=0,
    privLength=0
)

testTTFDataWOFFDirectory = []
for tag in sfntTTFTableOrder:
    d = dict(
        tag=tag,
        offset=0,
        compLength=0,
        origLength=0,
        origChecksum=0
    )
    testTTFDataWOFFDirectory.append(d)

testCFFDataWOFFDirectory = []
for tag in sfntCFFTableOrder:
    d = dict(
        tag=tag,
        offset=0,
        compLength=0,
        origLength=0,
        origChecksum=0
    )
    testCFFDataWOFFDirectory.append(d)

# --------------------
# Default Data Creator
# --------------------

def defaultTestData(header=None, directory=None, tableData=None, metadata=None, privateData=None, flavor="cff"):
    parts = []
    # setup the header
    if header is None:
        header = deepcopy(testDataWOFFHeader)
    parts.append(header)
    # setup the directory
    if directory is None:
        if flavor == "cff":
            directory = deepcopy(testCFFDataWOFFDirectory)
        else:
            directory = deepcopy(testTTFDataWOFFDirectory)
    parts.append(directory)
    # setup the table data
    if tableData is None:
        if flavor == "cff":
            tableData = deepcopy(sfntCFFTableData)
        else:
            tableData = deepcopy(sfntTTFTableData)
    parts.append(tableData)
    # sanity checks
    assert len(directory) == len(tableData)
    assert set(tableData.keys()) == set([entry["tag"] for entry in directory])
    # apply the directory data to the header
    header["numTables"] = len(directory)
    header["length"] = woffHeaderSize + (woffDirectoryEntrySize * len(directory))
    if "CFF " in tableData:
        header["flavor"] = "OTTO"
    else:
        header["flavor"] = "\000\001\000\000"
    # apply the table data to the directory and the header
    header["totalSfntSize"] = sfntDirectorySize + (len(directory) * sfntDirectoryEntrySize)
    offset = header["length"]
    for entry in directory:
        tag = entry["tag"]
        origData, compData = tableData[tag]
        # measure
        compLength = len(compData)
        compPaddedLength = compLength + calcPaddingLength(compLength)
        origLength = len(origData)
        origPaddedLength = origLength + calcPaddingLength(origLength)
        # store
        entry["offset"] = offset
        entry["compLength"] = compLength
        entry["origLength"] = origLength
        if origData in originalSFNTChecksums:
            checksum = originalSFNTChecksums[origData]
        else:
            checksum = calcTableChecksum(tag, origData)
        entry["origChecksum"] = checksum
        header["length"] += compPaddedLength
        header["totalSfntSize"] += origPaddedLength
        # next
        offset += compPaddedLength
    # setup the metadata
    if metadata is not None:
        if isinstance(metadata, tuple):
            metadata, compMetadata = metadata
        else:
            compMetadata = None
        if compMetadata is None:
            compMetadata = zlib.compress(metadata)
        header["metaOffset"] = header["length"]
        header["metaLength"] = len(compMetadata)
        header["metaOrigLength"] = len(metadata)
        header["length"] += len(compMetadata)
        if privateData is not None:
            header["length"] += calcPaddingLength(len(compMetadata))
        parts.append((metadata, compMetadata))
    # setup the private data
    if privateData is not None:
        header["privOffset"] = header["length"]
        header["privLength"] = len(privateData)
        header["length"] += len(privateData)
        parts.append(privateData)
    # return the parts
    return parts
