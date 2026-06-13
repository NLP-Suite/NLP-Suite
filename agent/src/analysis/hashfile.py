"""Checksum-keyed cache of tokenized files, used by
statistics_txt_util.compute_character_word_ngrams to skip re-tokenizing
unchanged documents across runs. Ported June 2026 from the upstream desktop
repo (marker file moved out of the cwd, eval replaced with ast.literal_eval).

The cache lives in a sibling directory of the output directory named
<outputDir>_cache; tokens are stored one file per line as
<sha256>@@@@----@@@@<token list repr>.
"""

import ast
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

CACHE_FILENAME = "stanza.temp.cache"
_SEPARATOR = "@@@@----@@@@"


def calculate_checksum(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def checkOut(outputDir):
    """Return True when a cache file exists for this output directory."""
    cache_directory = outputDir + "_cache"
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)
    return CACHE_FILENAME in os.listdir(cache_directory)


def getcache(outputDir):
    cache_file = outputDir + "_cache" + os.sep + CACHE_FILENAME
    hashmap = {}
    with open(cache_file, encoding="utf-8") as f:
        for line in f:
            if _SEPARATOR in line:
                try:
                    checksum, tokens = line.split(_SEPARATOR)
                    hashmap[checksum] = ast.literal_eval(tokens)
                except (ValueError, SyntaxError):
                    logger.info("Skipping malformed n-grams cache line")
    return hashmap


def storehash(hashmap, checksum, tokens):
    if checksum not in hashmap:
        hashmap[checksum] = tokens


def writehash(hashmap, outputDir):
    cache_directory = outputDir + "_cache"
    cache_outputFileName = cache_directory + os.sep + CACHE_FILENAME
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)
    lines = "".join(str(key) + _SEPARATOR + str(value) + "\n" for key, value in hashmap.items())
    try:
        with open(cache_outputFileName, "w", encoding="utf-8") as f:
            f.write(lines)
    except OSError:
        logger.warning("Failed to create the n-grams cache output file %s", cache_outputFileName)
