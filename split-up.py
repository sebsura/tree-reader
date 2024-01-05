#!/bin/python

import fileinput

full_id = 1
diff_id = 2
incr_id = 3

pids = dict()
current_pid = 0
current_fi = 0

file_pid = open("test.pid", "w")
file_full = open("test.full", "w")
file_diff = open("test.diff", "w")
file_incr = open("test.incr", "w")

full = set()
diff = set()
incr = set()


def make_path_id(path):
    global current_pid, pids
    res = pids.get(path)
    if res != None:
        return res

    current_pid += 1
    pids[path] = current_pid
    return current_pid

def add_pid(pid, path):
    file_pid.write(f"{pid}|{path}\n")

def add_file(fi, pid, stat, name):
    global full, diff, incr
    global file_full, file_diff, file_incr
    global full_id, diff_id, incr_id

    pair = (pid, name)
    if pair not in full:
        full.add(pair)
        file_full.write(f"{fi}|{full_id}|{pid}|'{stat}'|'{name}'\n")
    elif pair not in diff:
        diff.add(pair)
        file_diff.write(f"{fi}|{diff_id}|{pid}|'{stat}'|'{name}'\n")
    elif pair not in incr:
        incr.add(pair)
        file_incr.write(f"{fi}|{incr_id}|{pid}|'{stat}'|'{name}'\n")
    else:
        print(f"{pair} exists too often in file; ignored.")

def make_stat(id, sz, blks, owner, tp):
    return "P0C BM82 IGk B Po Po A CGy BAA Y BlgDfI BZQ7WQ BlgDfI A A C"

def next_fi():
    global current_fi
    current_fi += 1
    return current_fi

def split(name):
    [p, _, f] = name.rpartition('/')
    return p, f

def is_dir(ft):
    return ft == "FS_FILE_TYPE_DIRECTORY"

def handle(parts):
    [name,ft,id,sz,blks,owner,tp] = parts
    if is_dir(ft):
        path, file = name, ""
    else:
        [path, file] = split(name)

    pid = make_path_id(path)
    fi = next_fi()
    stat = make_stat(id, sz, blks, owner, tp)

    add_file(fi, pid, stat, file)

def handle_line(line):
    handle(line.split("|"))

def handle_pids():
    global pids
    rev = dict()
    for k in pids.keys():
        rev[pids[k]] = k
    for pid in sorted(rev.keys()):
        path = rev[pid]
        add_pid(pid, path)


for line in fileinput.input():
    if line[-1] == '\n':
        line = line[:-1]
    handle_line(line)

handle_pids()

file_pid.close()
file_full.close()
file_diff.close()
file_incr.close()

print(f"full = {len(full)}, diff = {len(diff)}, incr = {len(incr)}")
