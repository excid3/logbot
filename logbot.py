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

# Imports
import os
import os.path
import irclib
from ftplib import FTP
from time import strftime

# Customizable Variables
########################
# Log format
extensions = {'text':'log',
             'html':'html'}
# Valid formats: text, html
FORMAT = 'text'

# Connection information
network = 'irc.freenode.net'
port = 6667
channels = ['#keryx']
nick = 'Excid3LogBot'
name = 'Excid3LogBot'

# FTP information
USE_FTP = False # Allow FTP uploads
host = '' # Server Ex. deathlok.dreamhost.com
username = ''
password = ''
# Folder on the server where the logs will be stored
# ALWAYS terminate with a /
# NOTE: This directory should already exist
# Ex: chdir = 'excid3.com/logs/'
chdir = ''

counter = 0
lines = 50

def write(channel, message):
    """ Write to the log file and console """
    # Format the message
    string = '%s %s' % (strftime('[%H:%M]'), message)
    if FORMAT == 'html':
        string += '<br />'
    string += '\n'
    
    # Make sure the local folder exists for logging this channel
    if not os.path.exists(channel):
        os.mkdir(channel)
        
    # Append the message to the file locally
    path = os.path.join(channel, '%s_%s.%s' % (channel, strftime('%m-%d-%Y'), \
                        extensions[FORMAT]))
    f = open(path, 'a')
    f.write(string)
    f.close()
    print '%s> %s' % (channel, message)

def handleJoin(connection, event):
    """ User joins channel """
    nick = event.source().split("!")
    
    try:
        nickmask = nick[1]
        nick = nick[0]
    except:
        nick = "unknown"
        nickmask = "unknown"
        
    write(event.target(), '%s (%s) has joined %s' % 
          (nick, nickmask, event.target()))
          
def handleInvite(connection, event):
    """ User invites bot to join channel """
    connection.join(event.arguments()[0])    

def handlePubMessage(connection, event): # Any public message
    """ Public message is sent """
    global counter, lines
    write(event.target(), '%s: %s' % \
            (event.source().split ('!')[0], event.arguments()[0]))
                                          
    # Update the counter and check it to see if its time to upload
    counter += 1
    if counter == lines and USE_FTP:
        upload()
        counter = 0

def handlePart(connection, event):
    """ User parts channel """
    write(event.target(), '%s has parted %s' % \
            (event.source().split('!')[0], event.target()))

def upload():
    """ Upload files via FTP """
    try:
        print 'Uploading logs to %s ...' % host
        
        # Create the FTP connection
        ftp = FTP(host, username, password)
        
        # Attempt to create the directory if it does not already exist
        try:    ftp.mkd(chdir)
        except: pass

        for channel in channels:
            # Attempt to create subdirectory for channel
            try:   ftp.mkd('%s%s' % (chdir, channel))
            except: pass
            
            # Move to the directory
            ftp.cwd('%s%s' % (chdir, channel))
            
            # Get the path for the filename
            path = os.path.join(channel, '%s_%s' % \
                    (channel, strftime('%m-%d-%Y')))
            
            # Open the file and store it via FTP
            f = open(path, 'rb')
            ftp.storbinary('STOR %s_%s.%s' % \
                    (channel, strftime('%m-%d-%Y'), extensions[FORMAT]), f)
            f.close()
            
        # Close the FTP connection
        ftp.quit()
        print 'Finished uploading logs to %s' % chdir
        
    except Exception, e:
        print e
        print 'Make sure your FTP information is correct.'

def main():
    """ Join the IRC server """

    # Write logs locally to logs/
    if not os.path.exists('logs'):
        os.mkdir('logs')
    os.chdir('logs')

    # Create an IRC object
    irc = irclib.IRC()

    # Setup the IRC functionality we want to log
    irc.add_global_handler('join', handleJoin)
    irc.add_global_handler('pubmsg', handlePubMessage)
    irc.add_global_handler('part', handlePart)
    irc.add_global_handler('invite', handleInvite)

    # Create a server object, connect and join the channel
    server = irc.server()
    server.connect(network, port, nick, ircname=name)
    for channel in channels:
        server.join(channel)

    # Jump into an infinte loop
    irc.process_forever()

if __name__ == '__main__':
    main()
