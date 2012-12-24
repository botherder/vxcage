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

import sys
import getpass
import argparse
import requests

def color(text, color_code):
    return '\x1b[%dm%s\x1b[0m' % (color_code, text)

def red(text):
    return color(text, 31)

def green(text):
    return color(text, 32)

def yellow(text):
    return color(text, 33)

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

    def make_url(self, route):
        if self.ssl:
            url = "https://"
            self.port = 443
        else:
            url = "http://"
        
        url += "%s:%s%s" % (self.host, self.port, route)

        return url

    def initialize(self):
        try:
            req = requests.get(self.make_url("/test"),
                               auth=(self.username, self.password),
                               verify=False)
        except Exception as e:
            print("ERROR: %s" % e)
            return False

        return True

    def tags_list(self):
        req = requests.get(self.make_url("/tags/list"),
                           auth=(self.username, self.password),
                           verify=False)
        res = req.json

        print("Tags list:")
        for tag in res:
            print("  * " + tag)

    def run(self):
        self.authenticate()
        if not self.initialize():
            return

        while True:
            command = raw_input(cyan("vxcage> "))

            if command == "tags":
                self.tags_list()
            elif command == "quit":
                return

if __name__ == "__main__":
    logo()

    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", help="Host of VxCage server", default="localhost", action="store", required=False)
    parser.add_argument("-p", "--port", help="Port of VxCage server", default=8080, action="store", required=False)
    parser.add_argument("-s", "--ssl", help="Enable if the server is running over SSL", default=False, action="store_true", required=False)
    parser.add_argument("-a", "--auth", help="Enable if the server is prompting an HTTP authentication", default=False, action="store_true", required=False)
    args = parser.parse_args()

    try:
        vx = VxCage(host=args.host, port=args.port, ssl=args.ssl, auth=args.auth)
        vx.run()
    except KeyboardInterrupt:
        sys.exit(1)
