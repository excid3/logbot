#!/usr/bin/env python
"""
   LogBot

   A minimal IRC log bot with FTP uploads

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
__version__ = "0.2.1"
__date__ = "08/11/2009"
__copyright__ = "Copyright (c) Chris Oliver"
__license__ = "GPL2"


import os
import os.path
import irclib

from ConfigParser import ConfigParser
from ftplib import FTP
from optparse import OptionParser
from time import strftime


html_header = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>%s</title>
    <link href="%s" rel="stylesheet" type="text/css" />
  </head>
  <body>
  </body>
</html>
"""


class LogBot(object):
    def __init__(self, network, port, channels, owner, nick, password, folder, stylesheet):
        self.network = network
        self.port = port
        self.channels = channels
        self.owner = owner
        self.nick = nick
        self.password = password
        self.folder = folder
        self.stylesheet = stylesheet
        
    def start(self):
        # Write logs locally, so we need the folder to exist
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        #os.chdir(self.folder)

        # Create an IRC object
        self.irc = irclib.IRC()

        # Setup the IRC functionality we want to log
        handlers = {'join': self.handleJoin,
                    'pubmsg': self.handlePubMessage,
                    'privmsg': self.handlePrivMessage,
                    'part': self.handlePart,
                    'invite': self.handleInvite,
                    'kick': self.handleKick,
                    'mode': self.handleMode,
                    'pubnotice': self.handlePubNotice,
                    'quit': self.handleQuit}
        for key, val in handlers.items():
            self.irc.add_global_handler(key, val)

        # Create a server object, connect and join the channel
        self.server = self.irc.server()
        self.server.connect(self.network, self.port, self.nick, ircname=self.nick)

        if self.password:        
            self.server.privmsg("nickserv", "identify %s" % self.password)

        for channel in self.channels:
            self.server.join(channel)

        # Jump into an infinte loop
        self.irc.process_forever()
    
            #eventtype -- A string describing the event.
            #source -- The originator of the event (a nick mask or a server).
            #target -- The target of the event (a nick or a channel).
            #arguments 
            
    def handleKick(self, connection, event):
        """Handles kick messages
        Writes messages to log
        """
        # kicker, channel, [person, reason]
        # event.source(), event.target(), event.arguments()
        person, reason = event.arguments()
        self.write(event.target(),
                   "-!- <span class=\"kick\">%s</span> was kicked from %s by %s [%s]" % \
                   (person, event.target(), event.source().split("!")[0], reason))
        
    def handleMode(self, connection, event):
        """Handles mode changes
        Writes messages to log
        """
        # person giving ops, #channel, [modes, person]
        #print event.source(), event.target(), event.arguments()
        modes, person = event.arguments()
        self.write(event.target(), 
    	           "-!- mode/<span class=\"mode\">%s</span> [%s %s] by %s" % \
		           (event.target(), modes, person, event.source().split("!")[0]))
        
    def handlePubNotice(self, connection, event):
        """Handles public notices
        Writes messages to log
        """
        # user, channel, [msg]
        #print event.source(), event.target(), event.arguments()
        self.write(event.target(), 
                   "<span class=\"notice\">-%s:%s-</span> %s" % \
                   (event.source().split("!")[0], event.target(), event.arguments()[0]))
				   
    def handleQuit(self, connection, event):
        """Handles quite messages
        Writes messages to log
        """
        # user, channel?, [reason]
        #print event.source(), event.target(), event.arguments()
        self.write(None,
                   "-!- <span class=\"quit\">%s</span> has quit [%s]" % \
                   (event.source().split("!")[0], event.arguments()[0]))
        
    def handlePrivMessage(self, connection, event):
        """Handles private messages
        Used for owners to send instructions to bot
        """
        # sender, receiver (me), [msg]
        print "PRIVATE MESSGAE", event.source(), event.target(), event.arguments()
        
    def handleJoin(self, connection, event):
        """Handles user join messages
        Writes messages to log
        """
        nick = event.source().split("!")
        try:
            nickmask = nick[1]
        except:
            nickmask = "unknown"
        nick = nick[0]
        
        self.write(event.target(),
                   "-!- <span class=\"join\">%s</span> (%s) has joined %s" % \
                   (nick, nickmask, event.target()))
        
    def handlePubMessage(self, connection, event):
        """Handles public messages
        Writes messages to log
        """
        nick = event.source().split("!")[0]
        self.write(event.target(),
                   "<span class=\"person\">&lt;%s&gt;</span> %s" % \
                   (nick, event.arguments()[0]))
        
    def handlePart(self, connection, event):
        """Handles part messages
        Writes messages to log
        """
        nick = event.source().split("!")[0]
        self.write(event.target(),
                   "-!- <span class=\"part\">%s</span> has parted %s" % \
                   (nick, event.target()))
             
    def handleInvite(self, connection, event):
        """Handles invitations from IRC users
        Only accept invites to join a channel if they are from an owner
        """
        nick = event.source().split("!")[0]
        
        # Only allow invites from owner(s)
        if not nick in self.owner:
            print "Invite from %s denied" % nick
            return
            
        for channel in event.arguments():
            self.server.join(channel)
            
    def write(self, channel, message):
        time = strftime("%H:%M:%S")
        date = strftime("%d-%m-%Y")
        if channel:
            print "%s> %s %s" % (channel, time, message)
            channels = [channel]
        else:
            # Quits don't have channels
            print "%s %s" % (time, message)
            channels = self.channels

        for channel in channels:
            path = os.path.abspath(os.path.join(self.folder, channel))
            if not os.path.exists(path):
                # Create the folder if it doesn't exist
                os.mkdir(path)
            
            path = os.path.join(path, date+".html")
            if not os.path.exists(path):
                # Create the html header
                f = open(path, "wb")
                f.write(html_header % (("%s | Logs for %s" % (channel, date)), self.stylesheet))
                f.close()

            data = open(path, "rb").readlines()[:-2]
            data.append("<a href=\"#%s\" name=\"%s\" class=\"time\">[%s]</a> %s<br />\n" % (time, time, time, message))
            data += ["  </body>\n", "</html>\n"]
            
            f = open(path, "wb")
            f.writelines(data)
            
def main(conf):
    """
    Start the bot using a config file.

    :Parameters:
       - `conf`: config file location
    """
    CONFIG = ConfigParser()
    CONFIG.read(conf)
    network = CONFIG.get('irc', 'network')
    port = CONFIG.getint('irc', 'port')
    channels = CONFIG.get('irc', 'channels').split(',')
    nick = CONFIG.get('irc', 'nick')
    try:
        password = CONFIG.get('irc', 'password')
    except:
        password = None
    owner = CONFIG.get('irc', 'owners').split(',')
    logs_folder = CONFIG.get('log', 'folder')
    stylesheet = CONFIG.get('log', 'stylesheet')

    bot = LogBot(network, port, channels, owner, nick, password, logs_folder, stylesheet)
    try:
        bot.start()
    except KeyboardInterrupt:
        pass

		
if __name__ == '__main__':
    # Require a config
    parser = OptionParser()
    parser.add_option('-c', '--config', dest='conf', help='Config to use')
    (options, args) = parser.parse_args()

    if not options.conf or not os.access(options.conf, os.R_OK):
        parser.print_help()
        raise SystemExit(1)
    main(options.conf)
