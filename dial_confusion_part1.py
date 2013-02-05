#!/usr/bin/env python
import sys
import socket

def get_response(s, responsetype):
    try:
        response = s.recv(512)
    except:
        print "Response for %s has timed out\n" % responsetype
        return

    # Read until we timeout.  Another way to do this
    # would be using a nonblocking socket.
    while response:
        print response
        try:
            response = s.recv(512)
        except:
            break

def main(argv):
    if len(argv) != 7:
        print "Try again. 6 arguments"
        print "ip port user pass phone# phone#"
        return -1

    s = socket.socket()
    s.settimeout(2)
    s.connect((argv[1], int(argv[2])))

    get_response(s,"Connecting")

    s.send("Action:login\r\n")
    s.send("Username:%s\r\n" % (argv[3]))
    s.send("Secret:%s\r\n" % (argv[4]))
    s.send("\r\n")

    get_response(s,"Action:Login")

    s.send("Action:Originate\r\n")
    s.send("Channel:Gtalk/asterisk/+%s@voice.google.com\r\n" % (argv[6]))
    s.send("Exten:%s\r\n" % (argv[5]))
    s.send("Context:default\r\n")
    s.send("Priority:1\r\n")
    s.send("\r\n")

    get_response(s,"Action:Originate")

    s.close()
    return 0
if __name__=="__main__":
    main(sys.argv)
