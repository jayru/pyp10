import sys

class Pseudo(object):
	def __init__(self, uplink):
		self.uplink = uplink
		self.nick = 'Do'
		self.num = self.uplink.makenick(self, self.nick, 'TheDoBot','PyP10 Do')
		self.uplink.join("#p10", self.num, op=True)
		self.uplink.endburst(self)
	def _send(self, line, **kwargs):
		self.uplink.send(line, self.num, **kwargs)
	def gotmsg(self, msg, source, target):
		command, args = msg.split(None, 1)
		if command == 'exec':
			try:
				exec(args, globals(), locals())
			except:
				self._send("P #p10 :!%(fromnum)s! exec - Exception: %(exc)r", fromnum=source, exc=sys.exc_info()[1])
			else:
				self._send("P #p10 :!%(fromnum)s! exec - Done.", fromnum=source)
		elif command == 'eval':
			retval = None
			try:
				retval = eval(args, globals(), locals())
			except:
				self._send("P #p10 :!%(fromnum)s! eval - Exception: %(exc)r", fromnum=source, exc=sys.exc_info()[1])
			else:
				self._send("P #p10 :!%(fromnum)s! eval - Return: %(retval)r", fromnum=source, retval=retval)
