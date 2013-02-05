#!/usr/bin/env python
'''
Copyright (C) 2010
David Vossel <dvossel@digium.com>

This program is free software, distributed under the terms of
the GNU General Public License Version 2.

Python
starpy
pygame
python optionparser module
python twisted framework

'''

import time
import string
import random
import threading
import math
import sys

from optparse import OptionParser
from twisted.application import service, internet
from twisted.internet import reactor, defer
from starpy import manager

import pygame
from pygame.locals import *
from pygame.color import THECOLORS

class Ball:
    def __init__(self, screen, size, speed, background, boxcolor):
        self.screen = screen
        screensize = self.screen.get_size()
        self.screenwidth = screensize[0]
        self.screenheight = screensize[1]

        self.x = self.startx = self.screenwidth/2
        self.y = self.starty = self.screenheight/2

        self.width = size
        self.height = size

        self.speed = speed
        self.maxSpeed = speed + (speed/2)
        self.minSpeed = speed - (speed/2)

        self.bgcolor = background
        self.boxcolor = boxcolor
        self.bounceOffRight = 1
        self.bounceOffleft = 1
        self.bounceOfftop = 1
        self.bounceOffbottom = 1

        self.startWait = 90
        self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
        self.playerList = []
        self.lastHit = None
        self.reset()

    def getCenter(self):
        return ((self.x + (self.width/2)), (self.y + (self.height/2)))

    def reset(self):
        # start in middle of screen
        self.waitFrames = self.startWait
        self.lastHit = None
        self.x = self.startx
        self.y = self.starty

        direction = 1
        if random.random() > .5:
            direction = -1
        self.vx = ((self.speed/2) + (random.random() * self.speed))* direction

        direction = 1
        if random.random() > .5:
            direction = -1
        self.vy = ((self.speed/2) + (random.random() * self.speed))* direction

    def trackPlayer(self, player):
        self.playerList.append(player)

    def detectCollision(self):
        for player in self.playerList:
                if player.rect.colliderect(self.rect):
                        return player
        return None

    def setWalls(self, top, bottom, left, right):
        self.bounceOffRight = right
        self.bounceOffleft = left
        self.bounceOfftop = top
        self.bounceOffbottom = bottom

    def draw(self):
        reset = 0
        if self.waitFrames > 0:
            self.waitFrames = self.waitFrames - 1
            self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect( self.screen, self.boxcolor, self.rect )
            return

        # Update position or reverse direction
        # Check for collision with the sides:
        hitPlayer = self.detectCollision()

        # if we hit player, recalculate velocities
        if hitPlayer != None and self.lastHit != hitPlayer:
            newVelocity = hitPlayer.getHitVelocity(self.getCenter())
            new_vx = self.vx + (math.fabs(self.vx) * newVelocity[0])
            new_vy = self.vy + (math.fabs(self.vy) * newVelocity[1])

            # increase velocity on turn around by 15%
            if (newVelocity[0] == 0):
                self.vx *= -1
                new_vx = self.vx + (self.vx * .15)
            if (newVelocity[1] == 0):
                self.vy *= -1
                new_vy = self.vy + (self.vy * .15)

            if math.fabs(new_vx) < self.maxSpeed and math.fabs(new_vx) > self.minSpeed:
                self.vx = new_vx
            if math.fabs(new_vy) < self.maxSpeed and math.fabs(new_vy) > self.minSpeed:
                self.vy = new_vy

            # the same player sound never touch it twice in a row
            self.lastHit = hitPlayer

        # get our New pos
        nx, ny = self.x + self.vx, self.y + self.vy

        # check if new pos is within bounds. reset if not.
        if hitPlayer == None:
            bound_x = nx + self.width
            bound_y = ny + self.height
            wall = None
            if bound_x >= self.screenwidth:
                reset = 1
                wall = 'right'
            elif nx <= 0:
                reset = 1
                wall = 'left'
            elif bound_y >= self.screenheight:
                reset = 1
                wall = 'down'
            elif ny <= 0:
                reset = 1
                wall = 'up'

            if reset:
                for player in self.playerList:
                    player.incScore(wall)
                self.reset() #out of bounds, reset and point lost
        # if ball did not reset, continue with new direction
        if reset == 0:
            self.x = nx
            self.y = ny
        # Draw the new box
        self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect( self.screen, self.boxcolor, self.rect )

    def setBackgroundColor(self, color):
        self.bgcolor=color
    def setBallColor(self, color):
        self.boxcolor=color

class Player:
    def __init__(self, screen, size, speed, background, boxcolor, location, controller):
        self.screen = screen
        self.sideOffSet = 50
        screensize = self.screen.get_size()
        self.screenwidth = screensize[0]
        self.screenheight = screensize[1]
        self.controller = controller
        self.speed = speed
        self.leftright = 0
        self.topbottom = 0
        self.score = 0
        self.location = location

        if location == 'right':
            self.leftright = 1
            self.x = screensize[0] - size[1] - self.sideOffSet
            self.y = screensize[1]/2 - (size[0]/2)
            self.xScore = screensize[0] - size[1] - 20
            self.yScore = screensize[1]/2
            self.width = size[1]
            self.height = size[0]
        elif location == 'left':
            self.leftright = 1
            self.x = self.sideOffSet
            self.y = screensize[1]/2 - (size[0]/2)
            self.xScore = + 15
            self.yScore = screensize[1]/2
            self.width = size[1]
            self.height = size[0]
        elif location == 'down':
            self.topbottom = 1
            self.x = screensize[0]/2 - (size[0]/2)
            self.y = screensize[1] - size[1] - self.sideOffSet
            self.xScore = screensize[0]/2
            self.yScore = screensize[1] - size[1] - 20
            self.width = size[0]
            self.height = size[1]
        else:
            self.topbottom = 1
            self.x = screensize[0]/2 - (size[0]/2)
            self.y = self.sideOffSet
            self.xScore = screensize[0]/2
            self.yScore = + 15
            self.width = size[0]
            self.height = size[1]

        self.vx = speed
        self.vy = speed
        self.bgcolor = background
        self.boxcolor = boxcolor
        self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)

        self.myFont = pygame.font.Font(None, 36)

    def incScore(self, location):
        if location == self.location:
            self.score += 1

    def reset(self):
        self.score = 0

    def getHitVelocity(self, theirXY):
        ourXY = self.getCenter()
        x = 0
        y = 0
        if self.topbottom:
            res = theirXY[0] - ourXY[0]
            if res > 0:
                x = .25
            else:
                x = -.25
        if self.leftright:
            res = theirXY[1] - ourXY[1]
            if res > 0:
                y = .25
            else:
                y = -.25

        return (x,y)

    def getCenter(self):
        return ((self.x + (self.width/2)), (self.y + (self.height/2)))

    def draw(self):
        if self.leftright == 1:
            if self.controller.is_up() == True:
                self.y = self.y - self.speed
            if self.controller.is_down() == True:
                self.y = self.y + self.speed

        if self.topbottom == 1:
            if self.controller.is_right() == True:
                self.x = self.x - self.speed
            if self.controller.is_left() == True:
                self.x = self.x + self.speed

        boundx = self.screenheight - self.height
        boundy = self.screenwidth - self.width
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if self.y > boundx:
            self.y = boundx
        if self.x > boundy:
            self.x = boundy

        # Draw the player's score
        label = self.myFont.render(str(self.score), 0, (200,200,200))
        self.screen.blit(label, (self.xScore, self.yScore))

        # Draw the player
        self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.boxcolor, self.rect)

    def setBackgroundColor(self, color):
        self.bgcolor=color
    def setBallColor(self, color):
        self.boxcolor=color

class AMIController:
    def __init__(self, ip, port, name, secret):
        self.connected = False
        self.controlList = []
        self.ip = ip
        self.name = name
        self.secret = secret
        self.port = port

    def login(self):
        print "AMI Login INIT"
        self.ami_factory = manager.AMIFactory(self.name, self.secret)
        self.ami_factory.login(self.ip, self.port).addCallbacks(self.onConnect, self.onError)

    def onError(self, ami):
        print "AMI login failed"
        reactor.stop()

    def onConnect(self, ami):
        print "Connected to the AMI"
        self.ami = ami
        self.connected = True
        #subscribe to the events we care about
        self.ami.registerEvent('DTMF', self.onDTMFEvent)
        self.ami.registerEvent('Hangup', self.onHangupEvent)

    def onHangupEvent(self, ami, event):
        for c in self.controlList:
            c.readEventHangup(event)

    def onDTMFEvent(self, ami, event):
        for c in self.controlList:
            c.readEventDTMF(event)

    def addDTMFController(self, controller):
        self.controlList.append(controller)

class DTMFController:
    def __init__(self, up, down, left, right, channelName):
        self.upDTMF = up
        self.downDTMF = down
        self.leftDTMF = left
        self.rightDTMF = right
        self.channelName = channelName
        self.up = self.down = self.right = self.left = 0
        self.aiEnabled = 0
        self.connectedUID = None

    def setAI(self, ai):
        self.aiEnabled = 1
        self.ai = ai

    def readEventHangup(self, event):
        try:
            if event['event'] == "Hangup" and event['uniqueid'] == self.connectedUID:
                # they disconnected, set connnectedUID = None so AI will kick back in
                self.connectedUID = None
        except:
            print "ERROR reading event"

    def readEventDTMF(self, event):
        try:
            if event['event'] == "DTMF" and (event['channel'].count(self.channelName) > 0):
                # This is the channel uniqueid we look for on hangup.
                if self.connectedUID == None:
                   self.connectedUID = event['uniqueid']

                if self.connectedUID != None and self.connectedUID != event['uniqueid']:
                    # we only care about the first channel with the correct channelName that
                    # registers with us.  As long as connectedUID is set, only accept DTMF
                    # from that channel.  We'll know when it hangs up because we're watching.
                    return

                if event['end'] == "Yes":
                #    print "end DTMF"
                    #self.up = self.down = self.right = self.left = 0
                    #print event['digit']
                    if event['digit'] == self.upDTMF:
                        self.up = 0
                    elif event['digit'] == self.downDTMF:
                        self.down = 0
                    elif event['digit'] == self.leftDTMF:
                        self.left = 0
                    elif event['digit'] == self.rightDTMF:
                        self.right = 0

                elif event['begin'] == "Yes":
                 #   print "begin DTMF"
                 #   print event['digit']
                    self.up = self.down = self.right = self.left = 0
                    if event['digit'] == self.upDTMF:
                        self.up = 1
                    elif event['digit'] == self.downDTMF:
                        self.down = 1
                    elif event['digit'] == self.leftDTMF:
                        self.left = 1
                    elif event['digit'] == self.rightDTMF:
                        self.right = 1
        except:
            print "ERROR reading event"

    def is_up(self):
        if self.aiEnabled == 1 and self.connectedUID == None:
            return self.ai.is_up()
        res = False
        if self.up:
            res = True
        return res
    def is_down(self):
        if self.aiEnabled == 1 and self.connectedUID == None:
            return self.ai.is_down()
        res = False
        if self.down:
            res = True
        return res
    def is_left(self):
        if self.aiEnabled == 1 and self.connectedUID == None:
            return self.ai.is_left()
        res = False
        if self.left:
            res = True
        return res
    def is_right(self):
        if self.aiEnabled == 1 and self.connectedUID == None:
            return self.ai.is_right()
        res = False
        if self.right:
            res = True
        return res

# tracks player to ball
class PongAI:
    def __init__(self, player, ball):
        self.player = player
        self.ball = ball
        self.up = self.down = self.right = self.left = 0

    def getDirection(self):
        playerPos = self.player.getCenter()
        ballPos = self.ball.getCenter()
        self.up = self.down = self.right = self.left = 0
        if ballPos[0] > playerPos[0]:
            self.left = 1
        else:
            self.right = 1

        if ballPos[1] > playerPos[1]:
            self.down = 1
        else:
            self.up = 1

    def is_up(self):
        self.getDirection()
        res = False
        if self.up:
            res = True
        return res
    def is_down(self):
        self.getDirection()
        res = False
        if self.down:
            res = True
        return res
    def is_left(self):
        self.getDirection()
        res = False
        if self.left:
            res = True
        return res
    def is_right(self):
        self.getDirection()
        res = False
        if self.right:
            res = True
        return res

class AstPong:
    def __init__(self, winsize, argv):

        # Get AMI login info
        parser = OptionParser()
        parser.add_option("-i", "--ipaddress", dest="ip", default="127.0.0.1",
                          help="AMI ip address (default: 127.0.0.1)")
        parser.add_option("-p", "--port", dest="port", type="int",
                          default=5038,
                          help="AMI ip address port (default: 5038)")
        parser.add_option("-u", "--username", dest="user", help="AMI username")
        parser.add_option("-s", "--secret", dest="secret", help="AMI secret")
        (options, args) = parser.parse_args(argv)

        self.amiUser = options.user
        self.amiSecret = options.secret
        self.amiIp = options.ip
        self.amiPort = options.port

        self.winsize = winsize
        self.drawObjects = []
        self.playerSize = (90,15)
        self.ballSize = 20
        self.playerSpeed = 10
        self.ballSpeed = 10

        reactor.callWhenRunning(self.startGame)

    def startGame(self):

        if self.amiIp and self.amiUser and self.amiSecret:
            self.man = AMIController(self.amiIp, self.amiPort, self.amiUser, self.amiSecret)
            self.man.login()
        else:
            print "Invalid Arguments\n"
            reactor.stop()
            return

        pygame.init()
        self.screen = pygame.display.set_mode(self.winsize,0,8)
        pygame.display.set_caption('EVERYTHING\'S STUPID!')
        self.screen.fill(THECOLORS["black"])

        self.controller1 = DTMFController('1','2','fake','fake', "player1")
        self.controller2 = DTMFController('1','2','fake','fake', "player2")
        self.controller3 = DTMFController('fake','fake','1','2', "player3")
        self.controller4 = DTMFController('fake','fake','1','2', "player4")

        self.man.addDTMFController(self.controller1)
        self.man.addDTMFController(self.controller2)
        self.man.addDTMFController(self.controller3)
        self.man.addDTMFController(self.controller4)

        self.player1 = Player(self.screen, self.playerSize, self.playerSpeed, THECOLORS["black"], THECOLORS["blue"], 'left', self.controller1)
        self.player2 = Player(self.screen, self.playerSize, self.playerSpeed, THECOLORS["black"], THECOLORS["green"], 'right', self.controller2)
        self.player3 = Player(self.screen, self.playerSize, self.playerSpeed, THECOLORS["black"], THECOLORS["red"], 'up', self.controller3)
        self.player4 = Player(self.screen, self.playerSize, self.playerSpeed, THECOLORS["black"], THECOLORS["orange"], 'down', self.controller4)
        self.ball1 = Ball(self.screen, self.ballSize, self.ballSpeed, THECOLORS["black"], THECOLORS["white"])

        self.ball1.trackPlayer(self.player1)
        self.ball1.trackPlayer(self.player2)
        self.ball1.trackPlayer(self.player3)
        self.ball1.trackPlayer(self.player4)
        self.ball1.setWalls(0,0,0,0) #tell not to bounce of any walls since 4 players

        # Set AI
        self.controller1.setAI(PongAI(self.player1, self.ball1))
        self.controller2.setAI(PongAI(self.player2, self.ball1))
        self.controller3.setAI(PongAI(self.player3, self.ball1))
        self.controller4.setAI(PongAI(self.player4, self.ball1))

        self.drawObjects.append(self.player1)
        self.drawObjects.append(self.player2)
        self.drawObjects.append(self.player3)
        self.drawObjects.append(self.player4)
        self.drawObjects.append(self.ball1)

        loopThread = threading.Thread(target=self.gameLoop)
        loopThread.start()

    def shutdown(self):
         if reactor.running:
            print "Stopping Reactor!"
            reactor.stop()

    def gameLoop(self):
        done = False
        clock = pygame.time.Clock()
        while not done:
            if not reactor.running:
                done = True
                break
           # erase screen every time
            self.screen.fill(THECOLORS["black"])
            for o in self.drawObjects:
                o.draw()
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
            # Limit to 30 frames per second.  This gives the other threads
            # plenty of time to watch for DTMF updates over network. Going faster
            # than this has no benifit.
            clock.tick(30)

        if reactor.running:
            reactor.callLater(1, self.shutdown())

def main(argv=None):
    if argv is None:
        argv = sys.argv
    game = AstPong((700, 700), argv)
    reactor.run()
    print "Exiting!"

    return
if __name__=="__main__":
    main()

