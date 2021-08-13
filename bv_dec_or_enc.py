table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr={}
for i in range(58):
	tr[table[i]]=i
s=[11,10,3,8,4,6,2,9,5,7]
xor=177451812
add=100618342136696320

def dec(x):
	r=0
	for i in range(10):
		r+=tr[x[s[i]]]*58**i
	return (r-add)^xor

def enc(x):
	x=(x^xor)+add
	r=list('BV          ')
	for i in range(10):
		r[s[i]]=table[x//58**i%58]
	return ''.join(r)