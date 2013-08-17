class Pseudo(object):
	def __init__(self, uplink):
		self.uplink = uplink
		self.nick = 'Q'
		self.num = self.uplink.makenick(self, self.nick, 'TheQBot','PyP10 Q')
		self.uplink.join("#p10", self.num, op=True)
		self.uplink.endburst(self)
	def _send(self, line, **kwargs):
		self.uplink.send(line, self.num, **kwargs)
	def gotmsg(self, msg, source, target):
		self._send("P #p10 :<%(fromnum)s> %(msg)s", fromnum=source, msg=msg)
