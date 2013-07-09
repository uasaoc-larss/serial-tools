serial-tools
============

Tools for testing and working with UART and other serial connections, as they relate to MAVLink.

The tools
---------

### serialdump.py

Does a hexdump from a serial port, optionally highlighting the start character of each message.

This script relies on the Python package "colorama" (from [https://pypi.python.org/pypi/colorama](https://pypi.python.org/pypi/colorama#downloads)) to provide highlighting on Windows. If not present, the script will still run, but highlighting will not be provided.
