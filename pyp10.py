#!/usr/bin/python

import socket, time


uplink = None
modules = {}
modules['q'] = (__import__('modules.q', globals(), locals(), ['Pseudo'], 0)).Pseudo()

class config(object):
	name = 'services.p10'
	numeric = ']S'
	uplink = {
		'address': '127.0.0.1',
		'port': 4400,
		'name': 'test.p10',
		'password': 'password',
		'vhost': '', #bind to this ip - empty string '' for auto-select
	}

def process(line):
	words = line.split()
	print "process"
	if words[1] == "G" or words[1] == "PING":
		print "PING!", line
		uplink.send("Z %(numeric)s :%(id)s" % {'numeric': config.numeric, 'id': config.uplink['name']})

class Server(object):
	def __init__(self, numeric, name):
		self.isuplink = False
		self.numeric = numeric
		self.name = name
		self.clients = {}
	def send(self, line, source=None, **kwargs):
		if source is None:
			source = config.numeric
		uplink._transmit(source+" "+(line % kwargs))
		
class Uplink(Server):
	def __init__(self, *args, **kwargs):
		global uplink
		super(Uplink, self).__init__(*args, **kwargs)
		uplink = self
		self.isuplink = True
		self.data = ""

		self.sock = socket.socket()
		self.sock.bind((config.uplink['vhost'], 0))
		self.sock.connect((config.uplink['address'], config.uplink['port']))

		self._transmit("PASS %s" % (config.uplink['password']))
		self._transmit("SERVER %(name)s 1 %(time)s %(time)s J10 %(numeric)s]]] +s :PyP10 Services" % {'name': config.name, 'time': time.time(), 'numeric': config.numeric})
		self.send("EB")
		self._transmit("]S G services.p10 test.p10") #todo
	#def send - inherited
	def _transmit(self, line):
		print ">", line
		self.sock.sendall(line+"\r\n")
	def _receive(self):
		self.data += self.sock.recv(4096)
		while "\n" in self.data:
			pieces = self.data.split("\n", 1)
			line = pieces[0].strip()
			print "<", line
			process(line)
			self.data = pieces[1]
		return True
	def loop(self):
		keepgoing = True
		while keepgoing:
			keepgoing = self._receive()


class Account(object):
	pass

class Client(object):
	pass

uplink = Uplink(-1, '')
uplink.loop()
