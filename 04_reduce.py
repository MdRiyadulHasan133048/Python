from functools import reduce
n = [5,10,12,3]
print(reduce(lambda x,y:x*y,n))