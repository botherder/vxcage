#!/usr/bin/env python
# Copyright (c) 2012, Claudio "nex" Guarnieri
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# -*- coding: utf-8 -*-

import os
import sys
import getpass
import argparse

try:
    import requests
    from progressbar import *
    from prettytable import PrettyTable
except ImportError as e:
    sys.exit("ERROR: Missing dependency: %s" % e)

def color(text, color_code):
    return '\x1b[%dm%s\x1b[0m' % (color_code, text)

def cyan(text):
    return color(text, 36)

def bold(text):
    return color(text, 1)

def logo():
    print("")
    print(cyan("  `o   O o   O .oOo  .oOoO' .oOoO .oOo. "))
    print(cyan("   O   o  OoO  O     O   o  o   O OooO' "))
    print(cyan("   o  O   o o  o     o   O  O   o O     "))
    print(cyan("   `o'   O   O `OoO' `OoO'o `OoOo `OoO' "))
    print(cyan("                                O       "))
    print(cyan("                             OoO' ") + " by nex")
    print("")

class VxCage(object):
    def __init__(self, host, port, ssl=False, auth=False):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.auth = auth
        self.username = None
        self.password = None

    def authenticate(self):
        if self.auth:
            self.username = raw_input("Username: ")
            self.password = getpass.getpass("Password: ")

    def build_url(self, route):
        if self.ssl:
            url = "https://"
            self.port = 443
        else:
            url = "http://"
        
        url += "%s:%s%s" % (self.host, self.port, route)

        return url

    def tags_list(self):
        req = requests.get(self.build_url("/tags/list"),
                           auth=(self.username, self.password),
                           verify=False)
        res = req.json

        table = PrettyTable(["tag"])
        table.align = "l"
        table.padding_width = 1

        for tag in res:
            table.add_row([tag])

        print(table)
        print("Total: %s" % len(res))

    def find_malware(self, term, value):
        term = term.lower()

        if not term in ("md5", "sha256", "ssdeep", "tag"):
            print("ERROR: Invalid search term [md5, sha256, ssdeep, tag]")
            return

        payload = {term : value}
        req = requests.post(self.build_url("/malware/find"),
                            data=payload,
                            auth=(self.username, self.password),
                            verify=False)
        res = req.json

        if isinstance(res, dict):
            for key, value in res.items():
                if key == "tags":
                    print("%s: %s" % (bold(key), ",".join(value)))
                else:
                    print("%s: %s" % (bold(key), value))
        else:
            table = PrettyTable(["md5",
                                 "sha256",
                                 "file_name",
                                 "file_type",
                                 "file_size"])
            table.align = "l"
            table.padding_width = 1

            for entry in res:
                table.add_row([entry["md5"],
                               entry["sha256"],
                               entry["file_name"],
                               entry["file_type"],
                               entry["file_size"]])

            print(table)
            print("Total: %d" % len(res))

    def get_malware(self, sha256, path):
        if not os.path.exists(path):
            print("ERROR: Folder does not exist at path %s" % path)
            return

        req = requests.get(self.build_url("/malware/get/%s" % sha256),
                           auth=(self.username, self.password),
                           verify=False)

        size = int(req.headers["Content-Length"].strip())
        bytes = 0

        widgets = [
            "Download: ",
            Percentage(),
            " ",
            Bar(marker=":"),
            " ",
            ETA(),
            " ",
            FileTransferSpeed()
        ]
        progress = ProgressBar(widgets=widgets, maxval=size).start()

        destination = os.path.join(path, sha256)
        binary = open(destination, "wb")

        for buf in req.iter_content(1024):
            if buf:
                binary.write(buf)
                bytes += len(buf)
                progress.update(bytes)

        progress.finish()
        binary.close()

        print("File downloaded at path: %s" % destination)

    def run(self):
        self.authenticate()

        while True:
            try:
                raw = raw_input(cyan("vxcage> "))
            except KeyboardInterrupt:
                print("")
                continue

            command = raw.strip().split(" ")

            if command[0] == "tags":
                self.tags_list()
            elif command[0] == "find":
                if len(command) == 3:
                    self.find_malware(command[1], command[2])
                else:
                    print("ERROR: Missing arguments (e.g. \"find key value\")")
            elif command[0] == "get":
                if len(command) == 3:
                    self.get_malware(command[1], command[2])
                else:
                    print("ERROR: Missing arguments (e.g. \"get sha256 /path/\")")
            elif command[0] == "quit" or command[0] == "exit":
                break

if __name__ == "__main__":
    logo()

    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", help="Host of VxCage server", default="localhost", action="store", required=False)
    parser.add_argument("-p", "--port", help="Port of VxCage server", default=8080, action="store", required=False)
    parser.add_argument("-s", "--ssl", help="Enable if the server is running over SSL", default=False, action="store_true", required=False)
    parser.add_argument("-a", "--auth", help="Enable if the server is prompting an HTTP authentication", default=False, action="store_true", required=False)
    args = parser.parse_args()

    vx = VxCage(host=args.host, port=args.port, ssl=args.ssl, auth=args.auth)
    vx.run()
