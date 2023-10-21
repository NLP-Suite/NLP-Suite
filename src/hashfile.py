import hashlib
def calculate_checksum(filename): # This very fast option could ensure we don't
    # do useless work if we already process once
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
import os
def checkOut(outputDir):
    outputDir +='Cache'
    # Check if the directory exists
    if not os.path.exists(outputDir):
        # If not, create the directory
        os.makedirs(outputDir)
    a = os.listdir(outputDir)
    if 'stanza.temp.cache' in a:
        return True
    else:
        with open('stanza.temp.cache','w',encoding='utf-8') as f:
            f.write("")
        return False
def getcache(outputDir):
    outputDir = outputDir + "Cache"
    with open(outputDir+os.sep+'stanza.temp.cache', encoding='utf-8') as f:
        caches = f.readlines()
    hashmap = {}
    for cache in caches:
        if '@@@@----@@@@' in cache:
            try:
                ab_id, tokens = cache.split('@@@@----@@@@')
                hashmap[ab_id] = eval(tokens)
            except:
                print("That's all for fetching caches...")
    return hashmap
def storehash(hashmap, hash, tokens):
    if hash in hashmap:
        print('tokens is auto fetched from temporary storage. No need to repeat.')
    else:
        hashmap[hash]= tokens
    # since complex objects are passed by reference, no need to return to waste space
def writehash(hashmap,outputDir):
    outputDir = outputDir + "Cache"
    s = ''
    for key in hashmap.keys():
        s+= str(key) + '@@@@----@@@@' + str(hashmap[key]) + '\n'
    with open(outputDir+os.sep+'stanza.temp.cache', 'w', encoding='utf-8') as f:
        f.write(s)

