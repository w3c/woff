"""
SFNT data extractor.
"""

import zlib
import sstruct
from fontTools.ttLib import TTFont
from fontTools.ttLib.sfnt import getSearchRange,\
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

def packSFNT(header, directory, tableData, flavor="cff",
    calcCheckSum=True, applyPadding=True, sortDirectory=True,
    searchRange=None, entrySelector=None, rangeShift=None):
    # update the checkSum
    if calcCheckSum:
        if flavor == "cff":
            f = "OTTO"
        else:
            f = "\000\001\000\000"
        calcHeadCheckSumAdjustmentSFNT(directory, tableData, flavor=f)
    # update the header
    cSearchRange, cEntrySelector, cRangeShift = getSearchRange(len(directory))
    if searchRange is None:
        searchRange = cSearchRange
    if entrySelector is None:
        entrySelector = cEntrySelector
    if rangeShift is None:
        rangeShift = cRangeShift
    header["searchRange"] = searchRange
    header["entrySelector"] = entrySelector
    header["rangeShift"] = rangeShift
    # version and num tables should already be set
    sfntData = sstruct.pack(sfntDirectoryFormat, header)
    # compile the directory
    sfntDirectoryEntries = {}
    entryOrder = []
    for entry in directory:
        sfntEntry = SFNTDirectoryEntry()
        sfntEntry.tag = entry["tag"]
        sfntEntry.checkSum = entry["checksum"]
        sfntEntry.offset = entry["offset"]
        sfntEntry.length = entry["length"]
        sfntDirectoryEntries[entry["tag"]] = sfntEntry
        entryOrder.append(entry["tag"])
    if sortDirectory:
        entryOrder = sorted(entryOrder)
    for tag in entryOrder:
        entry = sfntDirectoryEntries[tag]
        sfntData += entry.toString()
    # compile the data
    directory = [(entry["offset"], entry["tag"]) for entry in directory]
    for o, tag in sorted(directory):
        data = tableData[tag]
        if applyPadding:
            data = padData(data)
        sfntData += data
    # done
    return sfntData
