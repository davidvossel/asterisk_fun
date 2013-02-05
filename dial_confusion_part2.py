#!/usr/bin/env python
import sys
import socket

def get_response(s, responsetype):
	response = " "
	print "Waiting for response for %s" % responsetype
	# Read until we timeout.  Another way to do this
	# would be using a nonblocking socket.
	while response:
		try:
			response = s.recv(1024)
		except:
			break
		print response

def main(argv):
	i = 6
	if len(argv) < 8:
		print "Try again at least 7 arguments"
		print "ip port user pass meetme_room phone# phone# ..."
		return -1

	s = socket.socket()
	s.settimeout(2)
	s.connect((argv[1], int(argv[2])))

	get_response(s,"Connecting")

	command = "Action:login\r\n"
	command += "Username:%s\r\n" % (argv[3])
	command += "Secret:%s\r\n" % (argv[4])
	command += "\r\n"
	s.send(command)

	get_response(s,"Action:Login")

	while i < len(argv):
		command = "Action:Originate\r\n"
		command += "Channel:Gtalk/asterisk/+%s@voice.google.com\r\n" % argv[i]
		command += "Application:MeetMe\r\n"
		command += "Data:%s,qr\r\n" % argv[5]
		command += "Priority:1\r\n"
		command += "\r\n"
		s.send(command)
		print "Calling %s" % argv[i]
		i += 1

	s.send("Action:logoff\r\n")

	s.close()
	return 0
if __name__=="__main__":
	main(sys.argv)
