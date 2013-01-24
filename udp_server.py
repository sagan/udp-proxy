#!/usr/bin/env python

# Super simple script that listens to a local UDP port and relays all packets to an arbitrary remote host.
# Packets that the host sends back will also be relayed to the local UDP client.
# Works with Python 2 and 3

import os
import hashlib
import sys 
import socket
import struct
import string
import json
import getopt
import random
import operator

def rand_bytes(num):
	return reduce(operator.add, ('%c' % random.randint(0, 255) for i in range(num)))

def fail(reason):
	sys.stderr.write(reason + '\n')
	sys.exit(1)

def get_table(key):
	m = hashlib.md5()
	m.update(key)
	s = m.digest()
	(a, b) = struct.unpack('<QQ', s)
	table = [c for c in string.maketrans('', '')]
	for i in xrange(1, 1024):
		table.sort(lambda x, y: int(a % (ord(x) + i) - a % (ord(y) + i)))
	return table

#md5 hash 16 bytes
def encrypt(data):
	h = hashlib.md5(data).digest()
	if len(data) <= 50:
		padlength = 150
	elif len(data) <= 100:
		padlength = 100
	elif len(data) <= 150:
		padlength = 50
	else:
		padlength = 10
	return (h + struct.pack('<H', padlength) + rand_bytes(padlength) + data).translate(encrypt_table)

# hash(16) + padlength(unsigned int, 2) + pad + data
def decrypt(data):
	if len(data) <= 150:
		return (False, '')
	de = data.translate(decrypt_table)
	padlength, = struct.unpack('<H', de[16:18]);
	h = de[:16]
	data = de[18 + padlength:]

	if hashlib.md5(data).digest() != h:
		return (False, data)
	return (True, data)

if __name__ == '__main__':
	os.chdir(os.path.dirname(__file__) or '.')
	
	try:
		with open('config.json', 'rb') as f:
			config = json.load(f)
		SERVER = config['server']
		SERVER_PORT = config['server_port']
		PORT = config['proxy_port']
		KEY = config['password']
	except:
		print "warning, config.json not found or can not be opened\n"

	optlist, args = getopt.getopt(sys.argv[1:], 's:p:k:l:')
	for key, value in optlist:
		if key == '-p':
			SERVER_PORT = int(value)
		elif key == '-k':
			KEY = value
		elif key == '-l':
			PORT = int(value)
		elif key == '-s':
			SERVER = value

	encrypt_table = ''.join(get_table(KEY))
	decrypt_table = string.maketrans(encrypt_table, string.maketrans('', ''))
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind(('', PORT))
	except:
		fail('Failed to bind on port ' + str(PORT))

	knownClient = None
	knownServer = (SERVER, SERVER_PORT)
	while True:
		data, addr = s.recvfrom(65535)

		if addr == knownServer:
			if not knownClient is None:
				s.sendto(encrypt(data), knownClient)
		else:
			result, data = decrypt(data)
			if not result:
				continue
			knownClient = addr
			s.sendto(data, knownServer)


