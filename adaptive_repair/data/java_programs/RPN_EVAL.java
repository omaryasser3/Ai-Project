package java_programs;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class RPN_EVAL {

    // Functional interface for binary operations
    @FunctionalInterface
    private interface BinaryOperator {
        double apply(double a, double b);
    }

    // Map to store operators and their corresponding lambda functions
    private static final Map<String, BinaryOperator> op = new HashMap<>();

    // Static initializer block to populate the operator map
    static {
        op.put("+", (a, b) -> a + b);
        op.put("-", (a, b) -> a - b);
        op.put("*", (a, b) -> a * b);
        op.put("/", (a, b) -> {
            if (b == 0) {
                throw new IllegalArgumentException("Division by zero error.");
            }
            return a / b;
        });
    }

    public static double rpn_eval(List<Object> tokens) {
        Deque<Double> stack = new ArrayDeque<>();

        for (Object token : tokens) {
            // Handle both Integer and Double as numeric tokens
            if (token instanceof Integer || token instanceof Double) {
                // Convert all numbers to double for consistent arithmetic
                stack.push(((Number) token).doubleValue());
            }
            // Explicitly check if the token is a String
            else if (token instanceof String) {
                String operator = (String) token;
                // If it's a string, check if it's a known operator
                if (op.containsKey(operator)) {
                    // Ensure there are enough operands on the stack for the binary operator
                    if (stack.size() < 2) {
                        throw new IllegalArgumentException(
                                String.format("Invalid RPN expression: Not enough operands for operator '%s'", operator));
                    }

                    // Correct RPN operand order:
                    // For an operation 'operand1 op operand2', 'operand2' is the top of the stack,
                    // and 'operand1' is the second from the top.
                    double operand2 = stack.pop();
                    double operand1 = stack.pop();

                    BinaryOperator binOp = op.get(operator);
                    double result = binOp.apply(operand1, operand2);
                    stack.push(result);
                } else {
                    // It's a string, but not a known operator
                    throw new IllegalArgumentException(String.format("Unknown operator: '%s'", operator));
                }
            } else {
                // It's neither a number nor a string (e.g., Boolean, List, null).
                throw new IllegalArgumentException(
                        String.format("Unexpected token type: %s for token '%s'", token.getClass().getName(), token));
            }
        }

        // After processing all tokens, a valid RPN expression should leave exactly one result on the stack
        if (stack.size() != 1) {
            throw new IllegalArgumentException("Invalid RPN expression: stack did not end with a single result.");
        }

        return stack.pop();
    }
}