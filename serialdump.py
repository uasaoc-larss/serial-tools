#!/usr/bin/env python

import sys, os
import serial
import argparse

def highlight(s):
    '''Return the value as a string, sourrounded by ANSI escapes to highlight'''
    if args.plain:
        return str(s)
    else:
        return '\033[31;1;7m' + str(s) + '\033[0m'

def is_packet_start(c):
    '''Return true if it is the start of a message'''
    if not args.mavlink09 and c == 0xFE:
        return True
    if args.mavlink09 and c == 0x55:
        return True
    return False

def print_hex_char(c):
    '''Print a character in hex, highlighting if necessary'''
    if is_packet_start(c):
        print highlight("%02x" % c),
    else:
        print "%02x" % c,

def print_hex(serial_device):
    '''Print the hex portion of the dump'''
    line = bytearray(16)
    for i in xrange(16):
        line[i] = serial_device.read()[0]
        print_hex_char(line[i])
        if i == 7:
            print "",
    return line

def print_ascii(line):
    stringed = str(line).translate('................................ !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~.................................................................................................................................')
    sys.stdout.write("  |")
    for i in xrange(len(line)):
        if is_packet_start(line[i]):
            c = highlight(stringed[i])
        else:
            c = stringed[i]
        sys.stdout.write(c)
    print "|"

parser = argparse.ArgumentParser(description="Dump data from a serial port")
parser.add_argument("port", help="The serial device to dump from, e.g. COM5 or /dev/ttyUSB0")
parser.add_argument("baudrate", help="The baudrate for the serial device", type=int)
parser.add_argument("-p", "--plain", help="Turn off highlighting", action="store_true")
parser.add_argument("-9", "--mavlink09", help="Highlight for MAVLink 0.9", action="store_true")
args = parser.parse_args()

if not args.plain and os.name == 'nt':
    try:
        import colorama
        colorama.init()
    except ImportError:
        sys.stderr.write("Error with 'colorama' module, and using Windows. Turning colors off.\nHint: use -p to prevent this message, or install colorama if you have not:\nhttps://pypi.python.org/pypi/colorama#downloads\n\n")
        args.plain = True

serial_1 = serial.Serial(port=args.port, baudrate=args.baudrate)

try:
    counter = 0
    while 1:
        #Print counter
        print "%08x " % (counter * 16),
    
        #Print hex
        line = print_hex(serial_1)

        #Print ASCII
        print_ascii(line)

        #Increment counter
        counter += 1
except KeyboardInterrupt:
    pass
