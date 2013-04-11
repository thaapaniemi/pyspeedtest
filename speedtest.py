import urllib, httplib
import getopt, sys
from time import time
import random
from threading import Thread, currentThread
from math import pow, sqrt
import bisect
import re

class Speedtest:
	HOST = 'speedtest-po.vodafone.pt'
	RUNS = 2
	VERBOSE = 0
	HTTPDEBUG = 0
	
	DOWNLOAD_FILES = [
	'/speedtest/random350x350.jpg',
	'/speedtest/random500x500.jpg',
	'/speedtest/random1500x1500.jpg',
	]
	
	UPLOAD_FILES = [
	132884,
	493638
	]
	
	def printv(self,msg):
		if self.VERBOSE : print msg
	
	def downloadthread(self,connection, url):
		connection.request('GET', url, None, { 'Connection': 'Keep-Alive'})
		response = connection.getresponse()
		self_thread = currentThread()
		self_thread.downloaded = len(response.read())
	
	def download(self):
		total_downloaded = 0
		connections = []
		for run in range(self.RUNS):
			connection = httplib.HTTPConnection(self.HOST)
			connection.set_debuglevel(self.HTTPDEBUG)
			connection.connect()
			connections.append(connection)
		total_start_time = time()
		for current_file in self.DOWNLOAD_FILES:
			threads = []
			for run in range(self.RUNS):
				thread = Thread(target = self.downloadthread, args = (connections[run], current_file + '?x=' + str(int(time() * 1000))))
				thread.run_number = run
				thread.start()
				threads.append(thread)
			for thread in threads:
				thread.join()
				total_downloaded += thread.downloaded
				self.printv('Run %d for %s finished' % (thread.run_number, current_file))
		total_ms = (time() - total_start_time) * 1000
		for connection in connections:
			connection.close()
		self.printv('Took %d ms to download %d bytes' % (total_ms, total_downloaded))
		return (total_downloaded * 8000 / total_ms)
	
	def uploadthread(self,connection, data):
		url = '/speedtest/upload.php?x=' + str(random.random())
		connection.request('POST', url, data, {'Connection': 'Keep-Alive', 'Content-Type': 'application/x-www-form-urlencoded'})
		response = connection.getresponse()
		reply = response.read()
		self_thread = currentThread()
		self_thread.uploaded = int(reply.split('=')[1])
	
	def upload(self):
		connections = []
		for run in range(self.RUNS):
			connection = httplib.HTTPConnection(self.HOST)
			connection.set_debuglevel(self.HTTPDEBUG)
			connection.connect()
			connections.append(connection)
			
		post_data = []
		ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
		for current_file_size in self.UPLOAD_FILES:
			values = {'content0' : ''.join(random.choice(ALPHABET) for i in range(current_file_size)) }
			post_data.append(urllib.urlencode(values))
			
		total_uploaded = 0
		total_start_time = time()
		for data in post_data:
			threads = []
			for run in range(self.RUNS):
				thread = Thread(target = self.uploadthread, args = (connections[run], data))
				thread.run_number = run
				thread.start()
				threads.append(thread)
			for thread in threads:
				thread.join()
				self.printv('Run %d for %d bytes finished' % (thread.run_number, thread.uploaded))
				total_uploaded += thread.uploaded
		total_ms = (time() - total_start_time) * 1000
		for connection in connections:
			connection.close()
		self.printv('Took %d ms to upload %d bytes' % (total_ms, total_uploaded))
		return (total_uploaded * 8000 / total_ms)
	
	def ping(self,server):
		connection = httplib.HTTPConnection(server)
		connection.set_debuglevel(self.HTTPDEBUG)
		connection.connect()
		times = []
		worst = 0
		for i in range(5):
			total_start_time = time()
			connection.request('GET', '/speedtest/latency.txt?x=' + str(random.random()), None, { 'Connection': 'Keep-Alive'})
			response = connection.getresponse()
			response.read()
			total_ms = time() - total_start_time
			times.append(total_ms)
			if total_ms > worst:
				worst = total_ms
		times.remove(worst)
		total_ms = sum(times) * 250 # * 1000 / number of tries (4) = 250
		connection.close()
		self.printv('Latency for %s - %d' % (server, total_ms))
		return total_ms
	
	def chooseserver(self):
		connection = httplib.HTTPConnection('www.speedtest.net')
		connection.set_debuglevel(self.HTTPDEBUG)
		connection.connect()
		now = int(time() * 1000)
		extra_headers = {
			'Connection': 'Keep-Alive',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2',
		}
		connection.request('GET', '/speedtest-config.php?x=' + str(now), None, extra_headers)
		response = connection.getresponse()
		reply = response.read()
	 	m = re.search('<client ip="([^"]*)" lat="([^"]*)" lon="([^"]*)"',reply)
		location = None
		if m == None:
			printv("Failed to retrieve coordinates")
			return None
		location = m.groups()
		self.printv('Your IP: %s\nYour latitude: %s\nYour longitude: %s' % location)
		connection.request('GET', '/speedtest-servers.php?x=' + str(now), None, extra_headers)
		response = connection.getresponse()
		reply = response.read()
		server_list = re.findall('<server url="([^"]*)" lat="([^"]*)" lon="([^"]*)"', reply)
		my_lat = float(location[1])
		my_lon = float(location[2])
		sorted_server_list = []
		for server in server_list:
			s_lat = float(server[1])
			s_lon = float(server[2])
			distance = sqrt(pow(s_lat - my_lat,2) + pow(s_lon - my_lon, 2))
			bisect.insort_left(sorted_server_list,(distance, server[0]))
		best_server = (999999, '')
		for server in sorted_server_list[:10]:
			print server[1]
			m = re.search('http://([^/]+)/speedtest/upload\.php',server[1])
			if not m : continue
			server_host = m.groups()[0]
			latency = self.ping(server_host)
			if latency < best_server[0]:
				best_server = (latency, server_host)
		self.printv('Best server: ' + best_server[1])
		return best_server[1]

#/Speedtest
