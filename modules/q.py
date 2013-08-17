class Pseudo(object):
	def __init__(self, uplink):
		self.uplink = uplink
		self.num = self.uplink.makenick(self, 'Q','TheQBot','PyP10 Q')
		self.send("J #p10 780000000")
	def send(self, line, **kwargs):
		self.uplink.send(line, self.num, **kwargs)
