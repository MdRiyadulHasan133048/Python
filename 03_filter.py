n = [25,10,12,45,11,14,16,18,17,3]
square = [i*i for i in n]
print(square)

ans = list(filter(lambda x:x%2!=0,square))
print(ans)