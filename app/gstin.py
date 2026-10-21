import re

# 2 digit state code + 10 char PAN + entity number + Z + check character
GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")

CHARACTERS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def has_valid_format(gstin):
    return bool(GSTIN_PATTERN.match(gstin))


def checksum_character(first_fourteen):
    """Work out what the 15th character of a GSTIN should be."""
    total = 0
    for position, character in enumerate(first_fourteen):
        value = CHARACTERS.index(character)
        if position % 2 == 1:
            value *= 2
        # add the two "digits" of the value in base 36
        total += value // 36 + value % 36
    return CHARACTERS[(36 - total % 36) % 36]


def has_valid_checksum(gstin):
    return checksum_character(gstin[:14]) == gstin[14]