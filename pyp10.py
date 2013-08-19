#!/usr/bin/python

import socket, time


uplink = None
modules = {}
modcount = 0

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
	autoload = ['q', 'do']

b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]"

class User(object):
	def __init__(self, num, nick, hostmask, modes, account):
		self.num = num
		self.nick = nick
		self.hostmask = hostmask
		self.modes = modes
		self.account = account

		if 'o' in self.modes:
			self.oper = True
		else:
			self.oper = False

		if self.account is not None:
			self.authed = True
		else:
			self.authed = False

class Uplink(object):
	def __init__(self):
		global uplink
		uplink = self

		self.lastnum = None # last numeric used, as [int,int,int]
		self.nicks = {} # 'nick': Pseudo-object
		self.nums = {} # 'num': Pseudo-objecta
		self.users = {} # 'num': User-objects
		self.data = "" # receive buffer

		self.bursting = True
		self.bursted = 0
		self.burstchans = {}

		self.sock = socket.socket()
		self.sock.bind((config.uplink['vhost'], 0))
		self.sock.connect((config.uplink['address'], config.uplink['port']))

		self._transmit("PASS %s" % (config.uplink['password']))
		self._transmit("SERVER %(name)s 1 %(time)s %(time)s J10 %(numeric)s]]] +s :PyP10 Services" % {'name': config.name, 'time': time.time(), 'numeric': config.numeric})
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
			self._process(line)
			self.data = pieces[1]
		return True
	def loop(self):
		keepgoing = True
		while keepgoing:
			if self.bursting and self.bursted >= modcount:
				self._burstisdone()
			keepgoing = self._receive()

	def _process(self, line):
		if ' :' in line:
			extrapos = line.find(' :')
			extra = line[extrapos+2:]
			line = line[0:extrapos]
			words = line.split()
			words.append(extra)
		else:
			extrapos = -1
			extra = None
			words = line.split()

		# words = ['ABACB', 'P', '#p10']; extra = 'Hi there!'
		if words[1] == "G" or words[1] == "PING":
			self.send("Z %(numeric)s :%(id)s" % {'numeric': config.numeric, 'id': config.uplink['name']})
		elif words[1] == "EB":
			self.send("EA")
		elif words[1] == "P" or words[1] == "PRIVMSG":
			source = words[0]
			target = words[2]
			if extra is None:
				extra = ' '.join(words[3:])
			if '@' in target:
				tonick = target.split('@', 1)
				self.nicks[tonick].gotmsg(extra, source, target)
			elif '#' in target:
				pass # no processing
			elif '$' in target:
				pass # no processing
			else:
				self.nums[target].gotmsg(extra, source, target)
		elif words[1] == "N" or words[1] == "NICK":
			nick = words[2]
			hostmask = words[5]+"@"+words[6]
			if words[7][0] == '+':
				modes = words[7][1:]
				if 'r' in modes and 'h' in modes:
					rpos = modes.find('r')
					hpos = modes.find('h')
					if rpos > hpos:
						account = words[9]
					else:
						account = words[8]
				elif 'r' in modes:
					account = modes[8]
				else:
					account = None
			num = words[-2]
			print repr((num, nick, hostmask, modes, account, extra))
			self.users[num] = User(num, nick, hostmask, modes, account)
	def _newnum(self): #FIXME increment only one value, not all!
		if self.lastnum is None:
			self.lastnum = [0,0,0]
		else:
			self.lastnum = [i+1 for i in self.lastnum]
		num =  config.numeric
		num += b64[self.lastnum[2]]
		num += b64[self.lastnum[1]]
		num += b64[self.lastnum[0]]
		return num

	def makenick(self, obj, nick, ident, realname):
		newnum = self._newnum()
		self.send("N %(nick)s 1 %(time)s %(ident)s %(host)s +doknXr pyp10 DAqAAB %(num)s :%(name)s", nick=nick, ident=ident, name=realname, time=time.time(), host=config.name, num=newnum)
		self.nums[newnum] = obj
		self.nicks[nick] = obj
		return newnum
	def getuser(self, num):
		return self.users[num]
	def join(self, chan, source, op=False):
#		if self.bursting:
#			if chan not in self.burstchans:
#				self.burstchans[chan] = {'ops':[], 'regs':[]}
#
#			if op:
#				self.burstchans[chan]['ops'].append(source)
#			else:
#				self.burtschans[chan]['regs'].append(source)
#		else: # not bursting
		self.send("J %(chan)s %(time)s", source, chan=chan, time=time.time()+3600)
		if op:
			self.send("OM %(chan)s +nto %(num)s", source, chan=chan, num=source)
	def endburst(self, module):
		self.bursted += 1
		print module.num, self.bursted, modcount
	def _burstisdone(self):
		self.bursting = False
		for chname, chan in self.burstchans.iteritems():
			users = chan['regs']

			if len(chan['ops']) != 0:
				chan['ops'][0] += ':o'
				users.extend(chan['ops'])

			mems = ','.join(users)
			self.send("B %(chan)s 780000001 +nt %(members)s", chan=chname, members=mems)
		self.send("EB")
		self.burtchans = {}

class Account(object):
	pass

class Client(object):
	pass

uplink = Uplink()

for modu in config.autoload:
	modules[modu] = (__import__('modules.'+str(modu), globals(), locals(), ['Pseudo'], 0)).Pseudo(uplink)
	modcount += 1

uplink.loop()
