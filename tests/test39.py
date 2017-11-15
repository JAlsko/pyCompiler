class C:
	x = 4
	y = 7
	def f(self, x):
		print self.x
		print self.y
o = C()
C.f(o, 1)
