`tree-reader.py` is a plugin for [bareos.org]. It accepts the plugin options `file` and `read`.
`file` needs to point at the output of `qumulo-tree-walk` with columns `path,type,id,size,blocks,owner,change_time` (in that order).

`anon.py` anonymises the output of qumolo-tree-walk like this:
* replaces all filename / directories by randomly generated words
* replaces the owner id by a random number
* replaces the id by a random number

`split-up.py` splits the output list into four files (`test.pid`, `test.full`, `test.diff`, `test.incr`). This is needed for `make-bareos-tables.sql`.
The idea is that `test.pid` contains the path table that bareos needs (a simple map id -> path).  `test.full` contains the file data in a
slightly modified way (for example it only stores filename + path id instead of the whole path).  If a file is listed multiple times inside the output
then only the first occurence is saved inside `test.full`.  The second occurance is stored inside `test.diff` and the third occurance is stored inside
of `test.incr`.

`make-bareos-tables.sql` takes the four files created with `split-up.py` and creates the postgresql tables & indices that bareos uses internally to
enable the building of restore trees.  Be careful: this script will first delete all tables it intends to fill if they exist.  Do not try to use
this with a real bareos database!
It will use the jobids 1, 2, 3 for the full, diff, incremental backup.
