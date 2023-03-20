# lambda function
f= lambda a,b :a*b 
result = f(10,5)
print(result)

# 02 example add and subtract 
add_sub = lambda a,b:(a+b, a-b)

x,y = add_sub(10,5)
print(x)
print(y)

# 03 example finding max from two numbers

mx = lambda x,y : x if x>y else y
print(mx(50,100))

