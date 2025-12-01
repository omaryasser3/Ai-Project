def rpn_eval(tokens):
    def op(symbol, a, b):
        # The lambda functions are defined such that 'a' is the first argument
        # and 'b' is the second argument in the lambda's scope. However, when
        # popping from the stack, 'a' (first pop) is the second operand in RPN
        # and 'b' (second pop) is the first operand in RPN. To correctly compute
        # 'first_operand op second_operand', we need to pass them in the correct order.
        # The fix below swaps 'a' and 'b' in the call to op, so the lambda
        # receives (first_operand, second_operand).
        return {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y
        }[symbol](a, b)

    stack = []

    for token in tokens:
        if isinstance(token, float):
            stack.append(token)
        else:
            # When popping from the stack for an RPN operation:
            # 'a' is the second operand (the one pushed last)
            # 'b' is the first operand (the one pushed second to last)
            a = stack.pop() # This is the second operand
            b = stack.pop() # This is the first operand
            stack.append(
                op(token, b, a) # Corrected: Pass b (first operand) then a (second operand)
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
