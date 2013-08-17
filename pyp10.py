#!/usr/bin/python

import socket, time


uplink = None
modules = {}

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
	autoload = ['q']

b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]"

def process(line):
	words = line.split()
	if words[1] == "G" or words[1] == "PING":
		uplink.send("Z %(numeric)s :%(id)s" % {'numeric': config.numeric, 'id': config.uplink['name']})

class Uplink(object):
	def __init__(self):
		global uplink
		uplink = self

		self.lastnum = None # last numeric used, as [int,int,int]
		self.nicks = {} # 'nick': Pseudo-object
		self.data = "" # receive buffer

		self.sock = socket.socket()
		self.sock.bind((config.uplink['vhost'], 0))
		self.sock.connect((config.uplink['address'], config.uplink['port']))

		self._transmit("PASS %s" % (config.uplink['password']))
		self._transmit("SERVER %(name)s 1 %(time)s %(time)s J10 %(numeric)s]]] +s :PyP10 Services" % {'name': config.name, 'time': time.time(), 'numeric': config.numeric})
		self.send("EB")
	def send(self, line, source=None, **kwargs):
		if source is None:
			source = config.numeric
		self._transmit(source+" "+(line % kwargs))
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

	def _newnum(self):
		if self.lastnum is None:
			self.lastnum = [0,0,0]
		else:
			self.lastnum = [i+1 for i in lastnum]
		num =  config.numeric
		num += b64[self.lastnum[2]]
		num += b64[self.lastnum[1]]
		num += b64[self.lastnum[0]]
		return num

	def makenick(self, obj, nick, ident, realname):
		newnum = self._newnum()
		self.send("N %(nick)s 1 %(time)s %(ident)s %(host)s +oknXr pyp10 DAqAAB %(num)s :%(name)s", nick=nick, ident=ident, name=realname, time=time.time(), host=config.name, num=newnum)
		self.nicks[nick] = obj
		return newnum


class Account(object):
	pass

class Client(object):
	pass

uplink = Uplink()

for modu in config.autoload:
	modules[modu] = (__import__('modules.'+str(modu), globals(), locals(), ['Pseudo'], 0)).Pseudo(uplink)

uplink.loop()
