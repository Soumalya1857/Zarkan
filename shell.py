import interpreter

while True:
    text = input('test > ')
    result,error = interpreter.run('<stdin>',text)

    if error != None:
    
        print(error.as_string())
    else:
        
        print(result)