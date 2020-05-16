import interpreter

while True:
    text = input('>>>> ')
    result,error = interpreter.run('<stdin>',text)

    if error != None:
        print(error.as_string())
    elif result:
        print(result)