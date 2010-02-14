#!/usr/bin/env python
"""
   LogBot

   A minimal IRC log bot

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
__version__ = "0.3.0"
__date__ = "08/11/2009"
__copyright__ = "Copyright (c) Chris Oliver"
__license__ = "GPL2"


import os
import os.path
import shutil

from ConfigParser import ConfigParser
from ftplib import FTP
from optparse import OptionParser
from time import strftime

from irclib import nm_to_n
from ircbot import SingleServerIRCBot


html_header = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>%s</title>
    <link href="stylesheet.css" rel="stylesheet" type="text/css" />
  </head>
  <body>
  </body>
</html>
"""

index_header = """<h1>%s</h1><br />"""


class LogBot(SingleServerIRCBot):
    def __init__(self, server, port, channels, owners, nickname, password):
        """Initialize this badboy"""
        SingleServerIRCBot.__init__(self, [(server, port, password)], 
                                          nickname, 
                                          nickname)
        self.chans = channels
    
    def set_format(self, folder, format, stylesheet):
        self.folder = folder
        self.format = format
        self.stylesheet = stylesheet
        
    def on_nicknameinuse(self, c, e):
        """Append an underscore to the nick if it's already in use"""
        c.nick(c.get_nickname() + "_")
        
    def on_welcome(self, c, e):
        """Join the channels once we have made a successful connection"""
        for channel in self.chans:
            c.join(channel)

    def on_pubmsg(self, c, e):
        user = nm_to_n(e.source())
        message = e.arguments()[0]
        channel = e.target()
        self.write(channel, self.format["pubmsg"].replace("%user%", user) \
                                                 .replace("%message%", message))
                                         
    def on_invite(self, c, e):
        pass
    
    def on_join(self, c, e):
        user = nm_to_n(e.source())
        host = e.source()
        channel = e.target()
        self.write(channel, self.format["join"].replace("%user%", user) \
                                               .replace("%host%", host) \
                                               .replace("%channel%", channel))
    
    def on_kick(self, c, e):
        kicker = e.source()
        channel = e.target()
        user, reason = e.arguments()
        self.write(channel, self.format["kick"].replace("%kicker%", kicker) \
                                               .replace("%channel%", channel) \
                                               .replace("%user%", user) \
                                               .replace("%reason%", reason))
                                 
    def on_mode(self, c, e):
        modes, person = e.arguments()
        channel = e.target()
        giver = nm_to_n(e.source())
        self.write(channel, self.format["mode"].replace("%channel%", channel) \
                                               .replace("%modes%", modes) \
                                               .replace("%person%", person) \
                                               .replace("%giver%", giver))
        
    def on_part(self, c, e):
        user = nm_to_n(e.source())
        channel = e.target()
        self.write(channel, self.format["part"].replace("%user%", user) \
                                               .replace("%channel%", channel))
                                 
    def on_privmsg(self, c, e):
        pass

    def on_topic(self, c, e):
        user = nm_to_n(e.source())
        channel = e.target()
        topic = e.arguments()[0]
        self.write(channel, self.format["topic"].replace("%user%", user) \
                                                .replace("%channel%", channel) \
                                                .replace("%topic%", topic))

    def on_nick(self, c, e):
        new = nm_to_n(e.source())
        old = e.target()
        self.write(None, self.format["nick"].replace("%old%", old) \
                                               .replace("%new%", new))

    def on_pubnotice(self, c, e):
        user = nm_to_n(e.source())
        channel = e.target()
        message = e.arguments()[0]
        self.write(channel, self.format["pubnotice"].replace("%user%", user) \
                                              .replace("%channel%", channel) \
                                              .replace("%message%", message))
            
    def on_quit(self, c, e):
        user = nm_to_n(e.source())
        reason = e.arguments()[0]
        channel = e.target()
        self.write(channel, self.format["quit"].replace("%user%", user) \
                                               .replace("%reason%", reason))

    def write(self, channel, message):
        time = strftime("%H:%M:%S")
        date = strftime("%d-%m-%Y")
        if channel:
            print "%s> %s %s" % (channel, time, message)
            channels = [channel]
        else:
            # Quit/nick don't have channels
            print "%s %s" % (time, message)
            channels = self.chans

        index = os.path.join(self.folder, "index.html")
        if not os.path.exists(self.folder):
            # Create the log folder if we need to
            os.mkdir(self.folder)
            create_html_file(index, "Logged Channels")
            append_to_index(index, index_header % "Logged Channels")
            shutil.copy2(self.stylesheet, self.folder)

        for channel in channels:
            path = os.path.abspath(os.path.join(self.folder, channel))
            
            if not os.path.exists(path):
                os.mkdir(path)
                
            if not os.path.exists(os.path.join(path, "stylesheet.css")):
                shutil.copy2(self.stylesheet, path)
            
            chan_index = os.path.join(path, "index.html")
            path = os.path.join(path, date+".html")
            if not os.path.exists(path):                
                create_html_file(chan_index, "%s | Logs" % channel)
                append_to_index(chan_index, index_header % "%s | Logs" % channel)
                
                append_to_index(index, "<a href=\"%%23%s\">%s</a>" % \
                                       (channel[1:]+"/index.html", channel))
                                       
                create_html_file(path, "%s | Logs for %s" % (channel, date))
                append_to_index(chan_index, "<a href=\"%s\">%s</a>" % \
                                            (date+".html", date))

            str = "<a href=\"#%s\" name=\"%s\" class=\"time\">[%s]</a> %s" % \
                                              (time, time, time, message)
            append_to_index(path, str, True)        


def create_html_file(path, title):
    f = open(path, "wb")
    f.write(html_header % title)
    f.close()


def append_to_index(path, line, br=False, back=-2):
    data = open(path, "rb").readlines()[:back]
    if br: data += [line + "<br />\n"]
    else:  data += [line + "\n"]
    data += ["  </body>\n", "</html>\n"]
    
    f = open(path, "wb")
    f.writelines(data)
    f.close()


def main(conf):
    """
    Start the bot using a config file.

    :Parameters:
       - `conf`: config file location
    """
    CONFIG = ConfigParser()
    CONFIG.read(conf)
    
    # Get the irc network configuration
    server = CONFIG.get("irc", "server")
    port = CONFIG.getint("irc", "port")
    channels = CONFIG.get("irc", "channels").split(",")
    nick = CONFIG.get("irc", "nick")
    try:
        password = CONFIG.get("irc", "password")
    except:
        password = None
    owner = CONFIG.get("irc", "owners").split(",")
    
    # Get the log section
    folder = CONFIG.get("log", "folder")
    stylesheet = CONFIG.get("log", "stylesheet")
    
    # Get the formation information
    types = ["join", "kick", "mode", "nick", "part", "pubmsg", "pubnotice", 
             "quit", "topic"]
    format = {}
    for type in types:
        format[type] = CONFIG.get("format", type)
        
    bot = LogBot(server, port, channels, owner, nick, password)
    bot.set_format(folder, format, stylesheet)
    bot.start()


if __name__ == "__main__":
    # Require a config
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="conf", help="Config to use")
    (options, args) = parser.parse_args()

    if not options.conf or not os.access(options.conf, os.R_OK):
        parser.print_help()
        raise SystemExit(1)
    main(options.conf)
