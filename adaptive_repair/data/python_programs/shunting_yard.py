def shunting_yard(tokens):
    precedence = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2
    }

    rpntokens = []
    opstack = []
    for token in tokens:
        if isinstance(token, int):
            rpntokens.append(token)
        else:
            # While there are operators on the stack with greater or equal precedence,
            # pop them to the output queue.
            while opstack and precedence[token] <= precedence[opstack[-1]]:
                rpntokens.append(opstack.pop())
            # Push the current operator onto the stack.
            opstack.append(token)

    # After processing all tokens, pop any remaining operators from the stack to the output.
    while opstack:
        rpntokens.append(opstack.pop())

    return rpntokens