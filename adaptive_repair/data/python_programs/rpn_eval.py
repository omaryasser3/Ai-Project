def rpn_eval(tokens):
    def op(symbol, a, b):
        return {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b
        }[symbol](a, b)

    stack = []

    for token in tokens:
        if isinstance(token, float):
            stack.append(token)
        else:
            # The first operand popped (a) is the right-hand side operand.
            # The second operand popped (b) is the left-hand side operand.
            # For non-commutative operations (like subtraction and division),
            # the operation should be b OP a.
            a = stack.pop() # Right operand
            b = stack.pop() # Left operand
            stack.append(
                op(token, b, a) # Corrected order: b then a
            )

    return stack.pop()



"""
Reverse Polish Notation

Four-function calculator with input given in Reverse Polish Notation (RPN).

Input:
    A list of values and operators encoded as floats and strings

Precondition:
    all(
        isinstance(token, float) or token in ('+', '-', '*', '/') for token in tokens
    )

Example:
    >>> rpn_eval([3.0, 5.0, '+', 2.0, '/'])
    4.0
"""
