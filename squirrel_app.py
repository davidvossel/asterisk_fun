#!/usr/bin/env python
'''
Copyright (C) 2010
David Vossel 

This program is free software, distributed under the terms of
the GNU General Public License Version 2.
'''

# This script connects to an Asterisk box over AMI.
# As new channels are created, it randomly places
# a pitchshift effect... on the lucky ones.
#
# usage  ./script.py -u  -s  -i  -p 

import sys
import socket
from optparse import OptionParser

import sys
import socket
import random

def main(argv):
    parser = OptionParser()
    parser.add_option("-i", "--ipaddress", dest="ip", default="127.0.0.1",
                      help="ami ip address (default: 127.0.0.1)")
    parser.add_option("-p", "--port", dest="port", type="int",
                      default=5038,
                      help="ami ip address port (default: 5038)")
    parser.add_option("-u", "--username", dest="user", help="ami username")
    parser.add_option("-s", "--secret", dest="secret", help="ami secret")
    (options, args) = parser.parse_args(argv)

    amiUser = options.user
    amiSecret = options.secret
    amiIp = options.ip
    amiPort = options.port

    # ---- The stuff that matters -----
    s = socket.socket()
    s.connect((amiIp, amiPort))

    # log in to AMI
    s.send("\r\n")
    s.send("Action: login\r\n")
    s.send("Username: %s\r\n" % amiUser)
    s.send("Secret: %s\r\n" % amiSecret)
    s.send("\r\n")

    while 1:
        d = {}
        # wait for incoming AMI events
        events = s.recv(512)
        print events

        # convert the event into a dictionary for easy access
        for line in events.splitlines():
            if (len(line) == 0):
                break
            list = line.split(':')
            if len(list) < 2:
                break
            d[list[0].strip()] = list[1].strip()

        if ("Event" not in d) or (d['Event'] != "Newchannel") or ("Channel" not in d):
            continue

        # time to roll the dice. %20 chance you are getting pitch shifted.
        if (random.randint(1,100) % 5) != 0:
            continue

        print "Lets mess with them"
        s.send("Action: Setvar\r\n")
        s.send("Channel: %s\r\n" % d['Channel'])
        s.send("Variable: PITCH_SHIFT(both)\r\n")
        s.send("Value: 1.8\r\n")
        s.send("\r\n")

    s.close()
    return 0
if __name__=="__main__":
    main(sys.argv)

