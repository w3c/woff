"""
Miscellaneous utilities.
"""

import struct
import sstruct
from fontTools.ttLib.sfnt import calcChecksum, getSearchRange,\
    SFNTDirectoryEntry, sfntDirectoryFormat, sfntDirectorySize, sfntDirectoryEntryFormat, sfntDirectoryEntrySize

# -------
# Padding
# -------

def calcPaddingLength(length):
    """
    Calculate how much padding is needed for 4-byte alignment.
    """
    if not length % 4:
        return 0
    return 4 - (length % 4)

def padData(data):
    """
    Pad with null bytes.
    """
    data += "\0" * calcPaddingLength(len(data))
    return data

# ---------
# Checksums
# ---------

def sumDataULongs(data):
    longs = struct.unpack(">%dL" % (len(data) / 4), data)
    value = sum(longs) % (2 ** 32)
    return value

def calcChecksum(data):
    data = padData(data)
    return sumDataULongs(data)

def calcTableChecksum(tag, data):
    """
    Calculate the checksum for the given table.
    """
    if tag == "head":
        checksum = calcChecksum(data[:8] + '\0\0\0\0' + data[12:])
    else:
        checksum = calcChecksum(data)
    return checksum & 0xffffffff

def calcHeadCheckSumAdjustment(directory, tableData, flavor=None):
    """
    Set the checkSumAdjustment in the head table data.
    This works with the WOFF table data structure used throughout the suites.
    """
    # first make sure that the head table is not compressed
    for entry in directory:
        if entry["tag"] != "head":
            continue
        origLength = entry["origLength"]
        compLength = entry["compLength"]
        assert origLength == compLength
        break
    # repack the data for the SFNT calculator
    sfntDirectory = []
    offset = sfntDirectorySize + (sfntDirectoryEntrySize * len(directory))
    for entry in directory:
        d = dict(
            tag=entry["tag"],
            offset=offset, # this should only be used for calculating the table order
            length=entry["origLength"],
            checksum=entry["origChecksum"]
        )
        sfntDirectory.append(d)
        offset += entry["origLength"] + calcPaddingLength(entry["origLength"])
    sfntTableData = {}
    for tag, (origData, compData) in tableData.items():
        sfntTableData[tag] = origData
    calcHeadCheckSumAdjustmentSFNT(sfntDirectory, sfntTableData, flavor=flavor)
    newHeadTableData = sfntTableData["head"]
    tableData["head"] = (newHeadTableData, newHeadTableData)

def calcHeadCheckSumAdjustmentSFNT(directory, tableData, flavor=None):
    """
    Set the checkSumAdjustment in the head table data.
    Grumble.
    """
    # if the flavor is None, guess.
    if flavor is None:
        flavor = "\000\001\000\000"
        for entry in directory:
            if entry["tag"] == "CFF ":
                flavor = "OTTO"
                break
    assert flavor in ("OTTO", "\000\001\000\000")
    # make the sfnt header
    searchRange, entrySelector, rangeShift = getSearchRange(len(directory))
    sfntHeaderData = dict(
        sfntVersion=flavor,
        numTables=len(directory),
        searchRange=searchRange,
        entrySelector=entrySelector,
        rangeShift=rangeShift
    )
    sfntData = sstruct.pack(sfntDirectoryFormat, sfntHeaderData)
    # make a SFNT table directory
    directory = [(entry["tag"], entry) for entry in directory]
    for tag, entry in sorted(directory):
        sfntEntry = SFNTDirectoryEntry()
        sfntEntry.tag = entry["tag"]
        sfntEntry.checkSum = entry["checksum"]
        sfntEntry.offset = entry["offset"]
        sfntEntry.length = entry["length"]
        sfntData += sfntEntry.toString()
    # calculate the checksum
    sfntDataChecksum = calcChecksum(sfntData)
    # gather all of the checksums
    checksums = [entry["checksum"] for o, entry in directory]
    checksums.append(sfntDataChecksum)
    # calculate the checksum
    checkSumAdjustment = sum(checksums)
    checkSumAdjustment = (0xB1B0AFBA - checkSumAdjustment) & 0xffffffff
    # set the value in the head table
    headTableData = tableData["head"]
    newHeadTableData = headTableData[:8]
    newHeadTableData += struct.pack(">L", checkSumAdjustment)
    newHeadTableData += headTableData[12:]
    tableData["head"] = newHeadTableData

# --------
# Metadata
# --------

def stripMetadata(metadata):
    """
    Strip leading and trailing whitespace from each line in the metadata.
    This is needed because of the indenting in the test case generation functions.
    """
    metadata = metadata.strip()
    metadata = metadata.replace("    ", "\t")
    return "\n".join([line.strip() for line in metadata.splitlines()])
