class C:
	x = 4
	y = 7
	def f(self, x):
		print x
		print self.x
		print self.y
		self.z = x
o = C()
o.f(1)
