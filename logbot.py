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
from ftplib import FTP
from time import strftime


# Customizable Variables
########################
network = 'irc.freenode.net'
port = 6667
channels = ['#excid3', '#keryx']
nick = 'Timber'
owner = ['excid3|asus', 'mac9416']
logs_folder = 'logs'


html_header = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>%s</title>
    <link href="/static/css/stylesheet.css" rel="stylesheet" type="text/css" />
  </head>
  <body onload="init()">
  </body>
</html>
"""


class LogBot(object):
    def __init__(self, network, port, channels, owner, nick, folder):
        self.network = network
        self.port = port
        self.channels = channels
        self.owner = owner
        self.nick = nick
        self.folder = folder
        
    def start(self):
        # Write logs locally, so we need the folder to exist
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        os.chdir(self.folder)

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
        write(event.target(),
              "%s left the room (Kicked by %s (%s))" % \
              (

        
    def handleMode(self, connection, event):
        """Handles mode changes
        Writes messages to log
        """
        # person giving ops, #channel, [modes, person]
        print event.source(), event.target(), event.arguments()
        
    def handlePubNotice(self, connection, event):
        """Handles public notices
        Writes messages to log
        """
        # user, channel, [msg]
        print event.source(), event.target(), event.arguments()
        
    def handleQuit(self, connection, event):
        """Handles quite messages
        Writes messages to log
        """
        # user, channel?, [reason]
        print event.source(), event.target(), event.arguments()
        
    def handlePrivMessage(self, connection, event):
        """Handles private messages
        Used for owners to send instructions to bot
        """
        # sender, receiver (me), [msg]
        print event.source(), event.target(), event.arguments()
        
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
        
        print "%s (%s) has joined %s" % \
                              (nick,
                               nickmask,
                               event.target())
        
    def handlePubMessage(self, connection, event):
        """Handles public messages
        Writes messages to log
        """
        nick = event.source().split("!")[0]
        print "%s: %s" % \
              (nick,
               event.arguments()[0])
        
    def handlePart(self, connection, event):
        """Handles part messages
        Writes messages to log
        """
        nick = event.source().split("!")[0]
        print '%s has parted %s' % \
            (nick, 
             event.target())
             
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
            
    def write(self):
        pass

def main():
    bot = LogBot(network, port, channels, owner, nick, logs_folder)
    bot.start()

if __name__ == '__main__':
    main()
