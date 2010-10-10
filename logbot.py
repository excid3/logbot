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
from time import strftime

try:
    from hashlib import md5
except:
    import md5

from ircbot import SingleServerIRCBot
from irclib import nm_to_n


### Configuration options

DEBUG = False

SERVER = "irc.freenode.net"
PORT = 6667
SERVER_PASS = None
CHANNELS=["#excid3"]
NICK = "timber"
NICK_PASS = None

default_format = {
    "action" : '<span class="person" style="color:%color%">* %user% %message%</span>',
    "help" : 'Check out http://excid3.com',
    "join" : '-!- <span class="join">%user%</span> [%host%] has joined %channel%',
    "kick" : '-!- <span class="kick">%user%</span> was kicked from %channel% by %kicker% [%reason%]',
    "mode" : '-!- mode/<span class="mode">%channel%</span> [%modes% %person%] by %giver%',
    "nick" : '<span class="nick">%old%</span> is now known as <span class="nick">%new%</span>',
    "part" : '-!- <span class="part">%user%</span> [%host%] has parted %channel%',
    "pubmsg" : '<span class="person" style="color:%color%">&lt;%user%&gt;</span> %message%',
    "pubnotice" : '<span class="notice">-%user%:%channel%-</span> %message%',
    "quit" : '-!- <span class="quit">%user%</span> has quit [%message%]',
    "topic" : '<span class="topic">%user%</span> changed topic of <span class="topic">%channel%</span> to: %message%',
}

html_header = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>%title%</title>
    <style type="text/css">
        body {
            background-color: #F8F8FF;
            font-family: Fixed, monospace;
            font-size: 13px;
        }
        h1 {
            font-family: sans-serif;
            font-size: 24px;
            text-align: center;
        }
        a, .time {
            color: #525552;
            text-decoration: none;
        }
        a:hover, .time:hover { text-decoration: underline; }
        .person { color: #DD1144; }
        .join, .part, .quit, .kick, .mode, .topic, .nick { color: #42558C; }
        .notice { color: #AE768C; }
    </style>
  </head>
  <body>
  <h1>%title%</h1>
  </body>
</html>
"""


### Helper functions

def append_line(filename, line):
    data = open(filename, "rb").readlines()[:-2]
    data += [line, "\n<br />", "\n</body>", "\n</html>"]
    write_lines(filename, data)

def write_lines(filename, lines):
    f = open(filename, "wb")
    f.writelines(lines)
    f.close()

def write_string(filename, string):
    f = open(filename, "wb")
    f.write(string)
    f.close()


### Logbot class

class Logbot(SingleServerIRCBot):
    def __init__(self, server, port, server_pass=None, channels=[],
                 nick="timber", nick_pass=None, format=default_format):
        SingleServerIRCBot.__init__(self,
                                    [(server, port, server_pass)],
                                    nick,
                                    nick)
                                    
        self.chans = channels
        self.format = format
        
        print "Logbot %s" % __version__
        print "Connecting to %s:%i..." % (server, port)
        print "Press Ctrl-C to quit"                         

    def quit(self):
        self.connection.disconnect("Quitting...")
          
    def color(self, user):
        return "#%s" % md5(user).hexdigest()[:6]

    def format_event(self, name, event, params):
        print event.target()
        print event.source()
        print event.arguments()
        msg = self.format[name]
        for key, val in params.iteritems():
            msg = msg.replace(key, val)

        # Always replace %user% with e.source()
        # and %channel% with e.target()    
        msg = msg.replace("%user%", nm_to_n(event.source()))
        msg = msg.replace("%host%", event.source())
        try: msg = msg.replace("%channel%", event.target())
        except: pass
        msg = msg.replace("%color%", self.color(nm_to_n(event.source())))
        try: msg = msg.replace("%message%", event.arguments()[0])
        except: pass
        
        return msg

    def write_event(self, name, event, params={}):        
        # Format the event properly
        chans = event.target()
        msg = self.format_event(name, event, params)
        
        # Quit goes across all channels
        if not chans or not chans.startswith("#"):
            chans = self.chans
        else:
            chans = [chans]
        
        for chan in chans:
            self.append_log_msg(chan, msg)
        
    def append_log_msg(self, channel, msg):
        print "%s >>> %s" % (channel, msg)

        # Create the channel path if necessary
        chan_path = "logs/%s" % channel
        if not os.path.exists(chan_path):
            os.makedirs(chan_path)
            
            # Create channel index
            write_string("%s/index.html" % chan_path, html_header.replace("%title%", "%s | Logs" % channel))

            # Append channel to log index
            append_line("logs/index.html", '<a href="%s/index.html">%s</a>' % (channel.replace("#", "%23"), channel))
        
        # Current log
        time = strftime("%H:%M:%S")
        date = strftime("%Y-%m-%d")
        log_path = "logs/%s/%s.html" % (channel, date)
        
        # Create the log date index if it doesnt exist
        if not os.path.exists(log_path):
            write_string(log_path, html_header.replace("%title%", "%s | Logs for %s" % (channel, date)))
            
            # Append date log
            append_line("%s/index.html" % chan_path, '<a href="%s.html">%s</a>' % (date, date))
            
        # Append current message
        message = "<a href=\"#%s\" name=\"%s\" class=\"time\">[%s]</a> %s" % \
                                          (time, time, time, msg)
        append_line(log_path, message)
        
    ### These are the IRC events
                            
    def on_all_raw_messages(self, c, e):
        """Display all IRC connections in terminal"""
        if DEBUG: print e.arguments()[0]
        
    def on_welcome(self, c, e):
        """Join channels after successful connection"""
        for chan in self.chans:
            c.join(chan)
            
    def on_nicknameinuse(self, c, e):
        """Nickname in use"""
        c.nick(c.get_nickname() + "_")
    
    def on_invite(self, c, e):
        """Arbitrarily join any channel invited to"""
        c.join(e.arguments()[0])
        #TODO: Save? Rewrite config file?
    
    ### Loggable events
    
    def on_action(self, c, e):
        """Someone says /me"""
        self.write_event("action", e)
        
    def on_join(self, c, e):
        self.write_event("join", e)
        
    def on_kick(self, c, e):
        self.write_event("kick", e,
                         {"%kicker%" : e.source(),
                          "%channel%" : e.target(),
                          "%user%" : e.arguments()[0],
                          "%reason%" : e.arguments()[1],
                         })

    def on_mode(self, c, e):
        self.write_event("mode", e,
                         {"%modes%" : e.arguments()[0],
                          "%person%" : e.arguments()[1],
                          "%giver%" : nm_to_n(e.source()),
                         })
                         
    def on_nick(self, c, e):
        self.write_event("nick", e,
                         {"%new%" : nm_to_n(e.source()),
                          "%old%" : e.target(),
                         })
        
    def on_part(self, c, e):
        self.write_event("part", e)

    def on_pubmsg(self, c, e):
        self.write_event("pubmsg", e)
        
    def on_pubnotice(self, c, e):
        self.write_event("pubnotice", e)
        
    def on_privmsg(self, c, e):
        c.privmsg(nm_to_n(e.source()), self.format["help"])
        
    def on_quit(self, c, e):
        self.write_event("quit", e)
        
    def on_topic(self, c, e):
        self.write_event("topic", e)

        
def main():
    # Create the logs directory
    if not os.path.exists("logs"):
        os.makedirs("logs")
        write_string("logs/index.html", html_header.replace("%title%", "Chat Logs"))
    
    # Start the bot
    bot = Logbot(SERVER, PORT, SERVER_PASS, CHANNELS, NICK, NICK_PASS)
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.quit()
    

if __name__ == "__main__":
    main()