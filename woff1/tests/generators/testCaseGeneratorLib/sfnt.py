"""
SFNT data extractor.
"""

import zlib
from fontTools.ttLib import TTFont

def getSFNTData(path):
    font = TTFont(path)
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
        if len(compData) >= len(origData):
            compData = origData
        tableData[tag] = (origData, compData)
    # order
    tableOrder = [i for i in font.keys() if len(i) == 4]
    font.close()
    del font
    return tableData, tableOrder, tableChecksums
