package java_programs;

import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class SHUNTING_YARD {

    public static List<Object> shunting_yard(List<Object> tokens) {
        // Define operator precedence
        Map<String, Integer> precedence = new HashMap<>();
        precedence.put("+", 1);
        precedence.put("-", 1);
        precedence.put("*", 2);
        precedence.put("/", 2);

        // RPN output list
        List<Object> rpnTokens = new ArrayList<>();
        // Operator stack
        Deque<String> opStack = new LinkedList<>(); // The stack should only contain string operators

        for (Object token : tokens) {
            if (token instanceof Integer || token instanceof Float || token instanceof Double) {
                // If the token is a number, add it to the RPN output list
                rpnTokens.add(token);
            } else if (token instanceof String) { // Ensure token is a string before treating as operator
                String operator = (String) token;
                // Check if the operator is known
                if (!precedence.containsKey(operator)) {
                    throw new IllegalArgumentException("Unknown operator: " + operator);
                }

                // Pop operators from the stack to the RPN list as long as they have higher or equal precedence
                // than the current operator, and the stack is not empty and the top is a known operator.
                // The condition `opStack.peek() != null && precedence.containsKey(opStack.peek())` ensures we only compare known operators on stack.
                while (!opStack.isEmpty() &&
                       precedence.containsKey(opStack.peek()) &&
                       precedence.get(operator) <= precedence.get(opStack.peek())) {
                    rpnTokens.add(opStack.pop());
                }
                // Push the current operator onto the stack
                opStack.push(operator);
            } else {
                // Handle unexpected token types, which would otherwise lead to runtime errors
                throw new IllegalArgumentException("Unexpected token type: " + token.getClass().getName() + " for token: " + token);
            }
        }

        // Pop any remaining operators from the stack to the RPN list
        while (!opStack.isEmpty()) {
            rpnTokens.add(opStack.pop());
        }

        return rpnTokens;
    }
}