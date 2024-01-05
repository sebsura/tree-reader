#!/bin/python

from functools import cache
import fileinput
import random

def random_string(size):
    bytes = [random.randint(65, 90) + random.randint(0, 1) * 32 for i in range(size)]
    return bytearray(bytes).decode("utf-8")

@cache
def randomize_string(s):
    return random_string(len(s))

def randomize_path(path):
    parts = path.split("/")
    rands = [randomize_string(p) for p in parts]
    return "/".join(rands)

@cache
def randomize_owner(owner):
    return random.getrandbits(32)

@cache
def randomize_id(id):
    return random.getrandbits(32)

def anonymise(parts):
    [name,ft,id,sz,blks,owner,tp] = parts
    return [randomize_path(name),ft,str(randomize_id(id)),sz,blks,str(randomize_owner(owner)),
            tp]

def handle_line(line):
    return "|".join(anonymise(line.split("|")))


for line in fileinput.input():
    if line[-1] == '\n':
        line = line[:-1]
    print(handle_line(line))
