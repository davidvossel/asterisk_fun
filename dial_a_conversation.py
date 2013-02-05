#!/usr/bin/env python
import sys
import os
import random

#EXAMPLE USAGE
#exten =>s,1,Answer()
#; here "/usr/src/" is the location of starters.txt
#exten =>s,n,AGI(/usr/src/dial_a_conversation.py,"/usr/src/")
#
def print_debug(debug):
    sys.stderr.write(debug)
    sys.stderr.flush()

def print_env():
    print_debug("\n--------- START ENV --------\n")
    while 1:
        line = sys.stdin.readline()
        if line == '\n':
            break
        print_debug(line)
    print_debug("\n")

def write_command(command):
    print_debug(command)
    sys.stdout.write(command)
    sys.stdout.flush()

def print_result():
    result = sys.stdin.readline().strip()
    print_debug("\n--------- RESULT --------\n")
    print_debug(result)
    print_debug("\n")

def get_random_line(filename):
    f = file(filename,'rb')
    lines = f.readlines()
    pos = random.randint(0,(len(lines)-1))
    f.close()
    return lines[pos]

def main(argv):
    if len(argv) != 2:
        print_debug("ERROR, 1 argument required\n")
        print_debug("Please provide directory of starters.txt")

    txtfile = "%sstarters.txt" % argv[1]
    print_debug("Text file = %s\n" % txtfile)
    # make a random name for our audio file
    audiofile = "%stest%d-%d" % (argv[1], random.randint(0,99999), random.randint(0,99999))
    print_debug("Audio file = %s\n" % audiofile)
    # read line from file
    line = "echo \"%s\" | text2wave -f 8000 -o %s.wav" % (get_random_line(txtfile), audiofile)
    # make audio file
    os.system(line)
    # read and print environment variables passed from Asterisk
    print_env()
    # tell Asterisk to play back the file
    write_command("EXEC Playback %s\n" % audiofile)
    # get the result of the Playback
    print_result()
    # remove the wav file that was created earlier
    os.system("rm %s.wav" % audiofile)
    return 0
if __name__=="__main__":
    main(sys.argv)
