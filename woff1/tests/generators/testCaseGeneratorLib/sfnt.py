"""
SFNT data extractor.
"""

import zlib
import sstruct
from fontTools.ttLib import TTFont
from fontTools.ttLib.sfnt import calcChecksum, getSearchRange,\
    SFNTDirectoryEntry, sfntDirectoryFormat, sfntDirectorySize, sfntDirectoryEntryFormat, sfntDirectoryEntrySize
from utilities import padData, calcHeadCheckSumAdjustmentSFNT

# ---------
# Unpacking
# ---------

def getSFNTData(pathOrFile):
    font = TTFont(pathOrFile)
    # checksums
    tableChecksums = {}
    for tag, entry in font.reader.tables.items():
        tableChecksums[tag] = entry.checkSum
    # data
    tableData = {}
    for tag in font.keys():
        if len(tag) != 4:
            continue
        origData = font.getTableData(tag)
        compData = zlib.compress(origData)
        if len(compData) >= len(origData) or tag == "head":
            compData = origData
        tableData[tag] = (origData, compData)
    # order
    tableOrder = [i for i in font.keys() if len(i) == 4]
    font.close()
    del font
    return tableData, tableOrder, tableChecksums

# -------
# Packing
# -------

def packSFNT(header, directory, tableData, flavor="cff", calcCheckSum=True):
    # update the checkSum
    if calcCheckSum:
        calcHeadCheckSumAdjustmentSFNT(directory, tableData, flavor=flavor)
    # update the header
    searchRange, entrySelector, rangeShift = getSearchRange(len(directory))
    header["searchRange"] = searchRange
    header["entrySelector"] = entrySelector
    header["rangeShift"] = rangeShift
    # version and num tables should already be set
    sfntData = sstruct.pack(sfntDirectoryFormat, header)
    # compile the directory
    directory = [(entry["offset"], entry) for entry in directory]
    sfntDirectoryEntries = {}
    for o, entry in sorted(directory):
        sfntEntry = SFNTDirectoryEntry()
        sfntEntry.tag = entry["tag"]
        sfntEntry.checkSum = entry["checksum"]
        sfntEntry.offset = entry["offset"]
        sfntEntry.length = entry["length"]
        sfntDirectoryEntries[entry["tag"]] = sfntEntry
    for tag, entry in sorted(sfntDirectoryEntries.items()):
        sfntData += entry.toString()
    # compile the data
    for o, entry in sorted(directory):
        data = tableData[entry["tag"]]
        data = padData(data)
        sfntData += data
    # done
    return sfntData
