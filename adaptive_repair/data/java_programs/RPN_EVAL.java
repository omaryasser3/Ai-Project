package java_programs;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.BiFunction;

public class RPN_EVAL {

    private static final Map<String, BiFunction<Double, Double, Double>> operators = new HashMap<>();

    static {
        operators.put("+", (a, b) -> a + b);
        operators.put("-", (a, b) -> a - b);
        operators.put("*", (a, b) -> a * b);
        operators.put("/", (a, b) -> a / b);
    }

    public static double rpn_eval(List<Object> tokens) {
        Deque<Double> stack = new ArrayDeque<>();

        for (Object token : tokens) {
            if (token instanceof Number) {
                stack.push(((Number) token).doubleValue()); // Ensure numbers are treated as doubles
            } else if (token instanceof String) {
                String operator = (String) token;
                if (!operators.containsKey(operator)) {
                    throw new IllegalArgumentException("Unknown operator: " + operator);
                }

                // For non-commutative operations like subtraction and division,
                // the order of operands matters. In RPN, when an operator is encountered,
                // the top two operands are popped. The first popped operand (top of stack)
                // is the right-hand side (RHS), and the second popped operand (below top of stack)
                // is the left-hand side (LHS).
                // The operation should be LHS op RHS.
                
                if (stack.size() < 2) {
                    throw new IllegalArgumentException("Insufficient operands for operator: " + operator);
                }

                // Pop RHS first
                Double rhs = stack.pop(); 
                // Pop LHS second
                Double lhs = stack.pop(); 

                // Apply the operator as 'lhs op rhs'
                Double result = operators.get(operator).apply(lhs, rhs);
                stack.push(result);
            } else {
                throw new IllegalArgumentException("Invalid token type: " + token.getClass().getName());
            }
        }

        if (stack.size() != 1) {
            throw new IllegalArgumentException("Invalid RPN expression: stack size is " + stack.size() + " at the end.");
        }

        return stack.pop();
    }
}