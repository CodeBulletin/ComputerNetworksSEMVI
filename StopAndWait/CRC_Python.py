def XOR(a, b):
    if a == b:
        return '0'
    return '1'

def binary_modulo(a, b):
    i = 0
    #Skipping All zero in front eg if the input is 001.... we can ignore the first two zero
    while i < len(a) and a[i] != '1':
        i += 1

    while i < len(a) - len(b) + 1: #Looping over the message
        for j in range(len(b)): # Looping Over the polynomial
            a = a[:i + j] + XOR(a[i + j], b[j]) + a[i + j + 1:] #since strings are immutable this is equivalent to a[i + j] = XOR(a[i + j], b)
        while i < len(a) - 1 and a[i + 1] != '1': # Skipping All zeros
            i += 1
        i += 1
    return a

def addZeros(a, n): #function that adds n zeros to the end of a string
    for i in range(n):
        a = a + '0'
    return a

def RemoveZeros(a, n): #function that removes n characters from the end of a string
    return a[:len(a)-n]

def EncodeCRC(message, poly):
    # Adding n-1 zeros to the end of the message where n is the length of poly and after that finding a % b in binary
    x = binary_modulo(addZeros(message, len(poly)-1), poly)
    message += x[len(message):] # adding remainder back to message
    return message

def ValidateCRC(message, poly):
    x = binary_modulo(addZeros(message, len(poly)-1), poly) # Calculating a % b
    # Checking if all the digits are zero i.e Valid code
    y = sum([a == '1' for a in x])
    if y != 0:
        return False
    return True    
