#!/usr/bin/env python

import sys, os
import serial
import argparse

def set_color(c):
    '''Change console color'''
    if not args.plain:
        sys.stdout.write('\033[3' + str(c) + 'm')

def reset_color():
    '''Reset console color to default'''
    if not args.plain:
        sys.stdout.write('\033[0m')

color_i = 1
id_i = 0
class SerialWrapper(object):
    def __init__(self, port, baudrate):
        global color_i, id_i
        self.serial = serial.Serial(port=port, baudrate=baudrate)
        self.row = 0
        self.col = 0
        self.next_to_echo = 0
        self.buf = bytearray(16)
        self.color = color_i
        self.sid = id_i
        id_i += 1
        color_i += 1
        if color_i == 7:
            color_i = 1

    def echo_to_others(self):
        global serials
        for s in serials:
            if s.sid == self.sid:
                continue
            s.serial.write(self.buf[self.next_to_echo:self.col])
            self.next_to_echo = self.col

    def new_row(self):
        '''Print a row when completed and reset'''
        self.echo_to_others()
        self.next_to_echo = 0
        self.col = 0
        if not args.quiet:
            set_color(self.color)

            #Print counter
            print "%08x " % (self.row * 16),
    
            #Print hex
            for i in xrange(len(self.buf)):
                print "%02x" % self.buf[i],
                if i == 7:
                    print "",

            #Print ASCII
            print " |%s|" % str(self.buf).translate('................................ !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~.................................................................................................................................')

        self.row += 1

parser = argparse.ArgumentParser(description="Bridge two or more serial ports")
parser.add_argument("-p", "--plain", help="Turn off highlighting", action="store_true")
parser.add_argument("-q", "--quiet", help="Do not dump to screen", action="store_true")
parser.add_argument("port", help="Serial device to bridge, e.g. COM5 or /dev/ttyUSB0. More than two may be specified.", nargs='+')
parser.add_argument("baudrate", help="The baudrate for the serial devices", type=int)
args = parser.parse_args()

if not args.plain and os.name == 'nt':
    try:
        import colorama
        colorama.init()
    except ImportError:
        sys.stderr.write("Error with 'colorama' module, and using Windows. Turning colors off.\nHint: use -p to prevent this message, or install colorama if you have not:\nhttps://pypi.python.org/pypi/colorama#downloads\n\n")
        args.plain = True

serials = []
for s in args.port:
    #[serial, rowcounter, colcounter, bytearray, color]
    serials.append(SerialWrapper(s, args.baudrate))

try:
    while True:
        #receive from ports
        for s in serials:
            while True:
                if s.serial.inWaiting():
                    s.buf[s.col] = s.serial.read()[0]
                    s.col += 1
                    #if completed a row, print it and reset
                    if s.col == 16:
                        s.new_row()
                        break
                else:
                    s.echo_to_others()
                    break
except KeyboardInterrupt:
    pass
finally:
    if not args.quiet:
        reset_color()
    for s in serials:
        s.serial.close()
