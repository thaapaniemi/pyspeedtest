#!/usr/bin/python

import getopt, sys
from math import pow, sqrt
from speedtest import Speedtest

def main():
	speedtest = Speedtest()
	findserver = False
	mode = 7
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hr:vm:d:s", ["help", "runs=","mode=","debug="])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)
	
	for o, a in opts:
		if o == "-v":
			speedtest.VERBOSE = 1
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-r", "--runs"):
			try:
				speedtest.RUNS = int(a)
			except ValueError:
				print 'Bad runs value'
				sys.exit(2)
		elif o in ("-m", "--mode"):
			try:
				mode = int(a)
			except ValueError:
				print 'Bad mode value'
				sys.exit(2)
		elif o in ("-d", "--debug"):
			try:
				speedtest.HTTPDEBUG = int(a)
			except ValueError:
				print 'Bad debug value'
				sys.exit(2)
		elif o == "-s":
			findserver = True
		
	if findserver:
		speedtest.HOST = speedtest.chooseserver()
	if mode & 4 == 4:
		print 'Ping: %d ms' % speedtest.ping(speedtest.HOST)
	if mode & 1 == 1:
		print 'Download speed: ' + pretty_speed(speedtest.download())
	if mode & 2 == 2:
		print 'Upload speed: ' + pretty_speed(speedtest.upload())
	
def pretty_speed(speed):
	units = [ 'bps', 'Kbps', 'Mbps', 'Gbps' ]
	unit = 0
	while speed >= 1024:
		speed /= 1024
		unit += 1
	return '%0.2f %s' % (speed, units[unit])

def usage():
	print '''
usage: pyspeedtest.py [-h] [-v] [-r N] [-m M] [-d L]

Test your bandwidth speed using Speedtest.net servers.

optional arguments:
 -h, --help         show this help message and exit
 -v                 enabled verbose mode
 -r N, --runs=N     use N runs (default is 2).
 -m M, --mode=M     test mode: 1 - download, 2 - upload, 4 - ping, 1 + 2 + 4 = 7 - all (default).
 -d L, --debug=L    set httpconnection debug level (default is 0).
 -s                 find best server
'''

if __name__ == '__main__':
	main()

