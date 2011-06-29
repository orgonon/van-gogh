#!/usr/bin/env python

import hashlib
import cPickle
import os
def append(filehash):
    hashlog = hashes()
    if filehash[0] in hashlog: 
        return hashlog[filehash[0]]
    else: 
        hashlog[filehash[0]] = filehash[1]
        cPickle.dump(hashlog, open('hashes', 'w'))
        return False

def hasher(fileName, otherName=None, block_size=2**20):
    f = open(fileName)
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    if otherName: return(md5.digest(), otherName)
    return (md5.digest(), fileName)

def create():
    ahash = hasher('hasher.py')
    hashlog = {} 
    hashlog[ahash[0]] = ahash[1]
    cPickle.dump(hashlog, open('hashes','w'))

def hashes():
    try: 
        hashlog = cPickle.load(open('hashes', 'r'))
        return hashlog
    except:
        create()
        hashlog = cPickle.load(open('hashes', 'r'))
        return hashlog
