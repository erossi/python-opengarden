#!/bin/sh

../ogarden_cli.py --set-time 1318613340 \
	--send-programs test_short.csv \
	--set-sunsite 2 \
	--set-valve monostable \
	--set-allarm-level LOW \
	--device /dev/ttyUSB0

python /usr/share/doc/python-serial/examples/miniterm.py --port=/dev/ttyUSB0 --baud=9600 --lf

