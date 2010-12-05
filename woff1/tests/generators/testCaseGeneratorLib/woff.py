"""
WOFF data packers.
"""

import sstruct
from utilities import padData

# ------------------
# struct Description
# ------------------

woffHeaderFormat = """
    > # big endian
    signature:      4s
    flavor:         4s
    length:         L
    numTables:      H
    reserved:       H
    totalSfntSize:  L
    majorVersion:   H
    minorVersion:   H
    metaOffset:     L
    metaLength:     L
    metaOrigLength: L
    privOffset:     L
    privLength:     L
"""
woffHeaderSize = sstruct.calcsize(woffHeaderFormat)

woffDirectoryEntryFormat = """
    > # big endian
    tag:            4s
    offset:         L
    compLength:     L
    origLength:     L
    origChecksum:   L
"""
woffDirectoryEntrySize = sstruct.calcsize(woffDirectoryEntryFormat)

# ------------
# Data Packing
# ------------

def packTestHeader(header):
    return sstruct.pack(woffHeaderFormat, header)

def packTestDirectory(directory):
    data = ""
    directory = [(entry["tag"], entry) for entry in directory]
    for tag, table in sorted(directory):
        data += sstruct.pack(woffDirectoryEntryFormat, table)
    return data

def packTestTableData(directory, tableData):
    orderedData = []
    for entry in directory:
        tag = entry["tag"]
        origData, compData = tableData[tag]
        compData = padData(compData)
        orderedData.append(compData)
    return "".join(orderedData)

def packTestMetadata((origMetadata, compMetadata), havePrivateData=False):
    if havePrivateData:
        compMetadata = padData(compMetadata)
    return compMetadata

def packTestPrivateData(privateData):
    return privateData
