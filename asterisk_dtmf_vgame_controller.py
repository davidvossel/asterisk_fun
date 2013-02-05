#!/usr/bin/env python
'''
Copyright (C) 2010
David Vossel <dvossel@digium.com>

This program is free software, distributed under the terms of
the GNU General Public License Version 2.
'''

import sys
import socket
from optparse import OptionParser

import pygame
from pygame.locals import *
from pygame.color import THECOLORS

class DtmfController:
    def __init__(self, winsize, argv):
        parser = OptionParser()
        parser.add_option("-i", "--ipaddress", dest="ip", default="127.0.0.1",
                          help="ami ip address (default: 127.0.0.1)")
        parser.add_option("-p", "--port", dest="port", type="int",
                          default=5038,
                          help="ami ip address port (default: 5038)")
        parser.add_option("-u", "--username", dest="user", help="ami username")
        parser.add_option("-s", "--secret", dest="secret", help="ami secret")
        (options, args) = parser.parse_args(argv)

        self.amiUser = options.user
        self.amiSecret = options.secret
        self.amiIp = options.ip
        self.amiPort = options.port

        pygame.init()
        self.winsize = winsize
        self.screen = pygame.display.set_mode(self.winsize,0,8)
        pygame.display.set_caption('EVERYTHING\'S STUPID!')
        self.screen.fill(THECOLORS["black"])
        screensize = self.screen.get_size()
        self.screenwidth = screensize[0]
        self.screenheight = screensize[1]

        self.boxSize = 40
        self.boxSpeed = 10
        self.up = 0
        self.down = 0
        self.right = 0
        self.left = 0

        self.x = self.startx = self.screenwidth/2
        self.y = self.starty = self.screenheight/2

        self.s = socket.socket()
        self.queue = "\r\n"

    def amiLogin(self):
        self.s.connect((self.amiIp, self.amiPort))
        self.s.setblocking(0) # never wait on read

        self.s.send("Action: login\r\n")
        self.s.send("Username: %s\r\n" % self.amiUser)
        self.s.send("Secret: %s\r\n" % self.amiSecret)
        self.s.send("\r\n")

    def readEvents(self):
        while True:
            try:
                response = self.s.recv(512)
            except:
                break
            self.queue += response

    def processEventQueue(self):
        lines = self.queue.splitlines()
        for line in lines:
            if line.count("Digit: 2"): #up
                self.up = 1
            if line.count("Digit: 5"): #down
                self.down = 1
            if line.count("Digit: 4"): #left
                self.left = 1
            if line.count("Digit: 6"): #right
                self.right = 1

            if line.count("End: Yes"): #end motion
                self.up = self.down = self.right = self.left = 0
            print line

        # clear the queue
        self.queue = ""

    def drawObjects(self):
        if self.right == 1:
            self.x += 10
        if self.left == 1:
            self.x -= 10
        if self.up == 1:
            self.y -= 10
        if self.down == 1:
            self.y += 10

        self.rect = pygame.rect.Rect(self.x, self.y, self.boxSize, self.boxSize)
        pygame.draw.rect( self.screen, THECOLORS["red"], self.rect )

    def gameLoop(self):
        done = False
        clock = pygame.time.Clock()
        while not done:
            # erase screen every time
            self.screen.fill(THECOLORS["black"])

            # Get DTMF info from Asterisk
            self.readEvents()
            self.processEventQueue()
            self.drawObjects()

            pygame.display.update()
            # Event Handling:
            events = pygame.event.get( )
            for e in events:
                if( e.type == QUIT ):
                    done = True
                    break
                elif (e.type == KEYDOWN):
                    if( e.key == K_ESCAPE ):
                        done = True
                        break
                    if( e.key == K_f ):
                        pygame.display.toggle_fullscreen()

            # Limit to 30 frames per second.
            clock.tick(30)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    game = DtmfController((400, 400), argv)
    game.amiLogin()
    game.gameLoop()

    print "Exiting!"
    return
if __name__=="__main__":
    main()
