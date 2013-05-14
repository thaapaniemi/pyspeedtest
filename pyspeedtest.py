#!/usr/bin/python

import getopt, sys
from math import pow, sqrt
from speedtest import Speedtest

def main():
	speedtest = Speedtest()
	speedtest._host = "speedtest1.ak.ber.netsign.net"
	
	# Country code
	cc = None
	randomserver = False
	serverlist = False

	mode = 7
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hr:vm:d:s", ["help", "runs=","mode=","debug=","serverlist","server=","cc="])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)
	
	for o, a in opts:
		if o == "-v":
			speedtest._verbose = 1
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-r", "--runs"):
			try:
				speedtest._runs = int(a)
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
				speedtest._httpdebug = int(a)
			except ValueError:
				print 'Bad debug value'
				sys.exit(2)
		elif o in ("-s", "--server"):
			try:
				server = str(a)
				if a in ("AUTO", "auto"):
					speedtest.setNearestserver()
				elif a in ("RANDOM", "random"):
					randomserver = True
				else:
					speedtest.setServer(a)
							
			except ValueError:
				print 'Bad server value'
				sys.exit(2)
		elif o == "--cc":
			try:
				cc = str(a)
			except ValueError:
				print 'Bad country value'
				sys.exit(2)
		elif o == "--serverlist":
			serverlist = True
		####
	
	if randomserver == True:
		speedtest.setRandomServer(cc)
	if serverlist == True:
		for i in speedtest._getServerList(cc):
			print i
		sys.exit(0)
	
	print "Server: " + str(speedtest._host)

	if mode & 4 == 4:
		print 'Ping: %d ms' % speedtest.ping()
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
usage: pyspeedtest.py [-h] [-v] [-r N] [-m M] [-d L] [--server S] [--serverlist] [--cc CC]

Test your bandwidth speed using Speedtest.net servers.

optional arguments:
 -h, --help         show this help message and exit
 -v                 enabled verbose mode
 -r N, --runs=N     use N runs (default is 2).
 -m M, --mode=M     test mode: 1 - download, 2 - upload, 4 - ping, 1 + 2 + 4 = 7 - all (default).
 -d L, --debug=L    set httpconnection debug level (default is 0).
 --server S         set server: S=address, BEST for best server or RANDOM for random server
 --serverlist		print serverlist
 --cc=CC			Set country for random server/serverlist, CC: Country code
'''

if __name__ == '__main__':
	main()

