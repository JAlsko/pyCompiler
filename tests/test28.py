def func1(x):
	return x + 1
	
def func2(f, n):
	return (f)(n)
	
print func2(func1, 5)
