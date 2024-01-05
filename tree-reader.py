#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BAREOS - Backup Archiving REcovery Open Sourced
#
# Copyright (C) 2023-2023 Bareos GmbH & Co. KG
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of version three of the GNU Affero General Public
# License as published by the Free Software Foundation, which is
# listed in the file LICENSE.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

# this test module will emit a job message in every single callback there is
# to make sure emitting a message won't break anything

# import all the wrapper functions in our module scope
from BareosFdWrapper import *

from bareosfd import (
    bRC_OK, bRC_More, bRC_Stop,
    JobMessage,
    DebugMessage,
    M_INFO,
    M_WARNING,
    bFileType,
    StatPacket,
    FT_REG, FT_DIREND, FT_LNK,
)

from datetime import datetime
import time

from BareosFdPluginBaseclass import BareosFdPluginBaseclass

import sys
from stat import S_IFREG, S_IFDIR, S_IRWXU


@BareosPlugin
class TreePlugin(BareosFdPluginBaseclass):
    def __init__(self, plugindef):
        JobMessage(M_INFO, "__init__('{}')\n".format(plugindef))
        self.desc = None
        return super().__init__(plugindef)

    def parse_plugin_definition(self, plugindef):
        ret = super().parse_plugin_definition(plugindef)

        self.desc = self.options["file"]
        if (self.options.get("read")):
            self.read = True
        else:
            self.read = False

        JobMessage(M_INFO, "parse_plugin_definition('{}','{}')\n".format(self.desc, self.read))

        return ret

    def handle_plugin_event(self, event):
        JobMessage(M_INFO, "handle_plugin_event({})\n".format(event))
        return super().handle_plugin_event(event)

    def parse_tp(self, tp):
        # skip nano seconds
        import time
        start = tp[:26]
        end = tp[29:]
        both = start + end

        return 0
        return time.mktime(time.strptime(both, '%Y-%m-%dT%H:%M:%S.%f%z'))


    def parse_ft(self, ft):
        if ft == 'FS_FILE_TYPE_FILE':
            return FT_REG
        elif ft == 'FS_FILE_TYPE_DIRECTORY':
            return FT_DIREND
        elif ft == 'FS_FILE_TYPE_SYMLINK':
            return FT_LNK
        else:
            raise ValueError('bad ft: %s' % ft)


    def start_backup_job(self):
        if self.desc is None:
            return bRC_Error

        self.fp = open(self.desc)

        self.line = self.fp.readline()[:-1] # remove newline

        return bRC_OK


    def start_backup_file(self, savepkt):
        if self.line:
            [name,ft,id,sz,blks,owner,tp] = self.line.split("|")
            statp = StatPacket()
            self.size = statp.st_size = int(sz)
            statp.st_mode = S_IRWXU | S_IFREG
            statp.st_blocks = int(blks)
            statp.st_blksize = 4096
            statp.st_ctime = self.parse_tp(tp)
            statp.st_atime = self.parse_tp(tp)
            statp.st_mtime = self.parse_tp(tp)
            statp.st_uid = int(owner)
            savepkt.statp = statp
            savepkt.type = self.parse_ft(ft)
            savepkt.no_read = (not self.read) or (savepkt.type != FT_REG)
            savepkt.fname = name
            savepkt.link = "i dont know"

            return bRC_OK

        return bRC_Stop

    def end_backup_file(self):
        if self.line:
            self.line = self.fp.readline()[:-1] # remove newline
            return bRC_More
        else:
            return bRC_OK

    def plugin_io_open(self, IOP):
        return bRC_OK

    def plugin_io_read(self, IOP):
        if self.size > 0:
            numbytes = min(IOP.count, self.size)
            IOP.buf = bytearray(numbytes)
            IOP.io_errno = 0
            IOP.status = numbytes
            self.size -= numbytes
        else:
            IOP.status = 0
        return bRC_OK

    def plugin_io_close(self, IOP):
        self.size = 0
        return bRC_OK

    def get_acl(self, acl):
        acl.content = bytearray(b"acl_content")
        return super().get_acl(acl)

    def set_acl(self, acl):
        return bRC_OK

    def get_xattr(self, xattr):
        xattr.name = bytearray(b"xattr_name")
        xattr.value = bytearray(b"xattr_value")

        return super().get_xattr(xattr)

    def set_xattr(self, xattr):
        return bRC_OK
