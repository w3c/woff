"""
Miscellaneous utilities.
"""

from fontTools.ttLib.sfnt import calcChecksum

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

def calcTableChecksum(tag, data):
    """
    Calculate the checksum for the given table.
    """
    if tag == "head":
        checksum = calcChecksum(data[:8] + '\0\0\0\0' + data[12:])
    else:
        checksum = calcChecksum(data)
    return checksum

# --------
# Metadata
# --------

def stripMetadata(metadata):
    """
    Strip leading and trailing whitespace from each line in the metadata.
    This is needed because of the indenting in the test case generation functions.
    """
    return "\n".join([line.strip() for line in metadata.splitlines()])
