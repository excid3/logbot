#!/usr/bin/env python
"""
   Multibot

   A logbot manager for running multiple copies

   Written by Chris Oliver

   Includes python-irclib from http://python-irclib.sourceforge.net/

   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License
   as published by the Free Software Foundation; either version 2
   of the License, or any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA   02111-1307, USA.
"""


__author__ = "Chris Oliver <excid3@gmail.com>"
__version__ = "0.1.0"
__date__ = "08/11/2009"
__copyright__ = "Copyright (c) Chris Oliver"
__license__ = "GPL2"


import sys
import threading

import logbot


class BotLauncher(threading.Thread):
    def __init__(self, conf):
        self.conf = conf
        threading.Thread.__init__(self)
        
    def run(self):
        logbot.main(self.conf)


if __name__ == "__main__":
    configs = sys.argv[1:]
    if not configs:
        print "ERROR: Pass multiple logbot configuration files as arguments to launch multiple bots"
        sys.exit(1)
        
    for config in configs:
        BotLauncher(config).start()
    