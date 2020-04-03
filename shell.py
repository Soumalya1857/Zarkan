import lexer1

while True:
    text = input('test > ')
    result,error = lexer1.run('<stdin>',text)

    if error != None:
        #print("it's an error")
        print(error.as_string())
    else:
        #print("it's not an error....its a ast")
        print(result)