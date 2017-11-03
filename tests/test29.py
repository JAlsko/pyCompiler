def wrap(n):
	return func(n, 0)

def func(n, tot):
	return tot if n == 0 else func(n + -1, tot + n)
	
print wrap(10)
