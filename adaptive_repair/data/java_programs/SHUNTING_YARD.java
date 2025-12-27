package java_programs;

import java.util.*;

public class SHUNTING_YARD {

    private static final Map<String, Integer> precedence = new HashMap<>();

    static {
        precedence.put("+", 1);
        precedence.put("-", 1);
        precedence.put("*", 2);
        precedence.put("/", 2);
    }

    public static List<Object> shuntingYard(List<Object> tokens) {
        List<Object> rpntokens = new ArrayList<>();
        Deque<String> opstack = new ArrayDeque<>(); // Using Deque as a stack

        for (Object tokenObj : tokens) {
            Object currentTokenValue = null;
            boolean isNumber = false;

            // Attempt to parse the token as a number (int, float, etc.)
            if (tokenObj instanceof Integer) {
                currentTokenValue = (Integer) tokenObj;
                isNumber = true;
            } else if (tokenObj instanceof Double) {
                currentTokenValue = (Double) tokenObj;
                isNumber = true;
            } else if (tokenObj instanceof Float) {
                currentTokenValue = (Float) tokenObj;
                isNumber = true;
            } else if (tokenObj instanceof Long) {
                currentTokenValue = (Long) tokenObj;
                isNumber = true;
            } else if (tokenObj instanceof String) {
                String tokenStr = (String) tokenObj;
                try {
                    currentTokenValue = Integer.parseInt(tokenStr);
                    isNumber = true;
                } catch (NumberFormatException e1) {
                    try {
                        currentTokenValue = Double.parseDouble(tokenStr);
                        isNumber = true;
                    } catch (NumberFormatException e2) {
                        // Not a number string, proceed to operator/parenthesis checks
                    }
                }
            }

            if (isNumber) {
                rpntokens.add(currentTokenValue);
            } else { // Not a number, assume it's an operator or parenthesis string
                String token = tokenObj.toString(); // Convert to string for comparison

                if (token.equals("(")) { // Left parenthesis
                    opstack.push(token);
                } else if (token.equals(")")) { // Right parenthesis
                    // Pop operators from the stack to the output queue until a left parenthesis is encountered
                    while (!opstack.isEmpty() && !opstack.peek().equals("(")) {
                        rpntokens.add(opstack.pop());
                    }
                    if (!opstack.isEmpty() && opstack.peek().equals("(")) { // Discard the left parenthesis
                        opstack.pop();
                    } else {
                        // Mismatched parentheses: ')' without a preceding '('
                        throw new IllegalArgumentException("Mismatched parentheses: ')' without a preceding '('");
                    }
                } else { // Operator
                    String operator = token;
                    // Ensure the operator is known and has a defined precedence
                    if (!precedence.containsKey(operator)) {
                        throw new IllegalArgumentException(String.format("Unknown operator: '%s'", operator));
                    }

                    // While there's an operator on the stack, it's not a left parenthesis,
                    // and the current operator's precedence is less than or equal to the stack top's precedence
                    while (!opstack.isEmpty() && !opstack.peek().equals("(") &&
                           precedence.get(operator) <= precedence.get(opstack.peek())) {
                        rpntokens.add(opstack.pop());
                    }
                    opstack.push(operator);
                }
            }
        }

        // Pop any remaining operators from the stack to the output queue
        while (!opstack.isEmpty()) {
            if (opstack.peek().equals("(")) { // Mismatched parentheses: unclosed left parenthesis
                throw new IllegalArgumentException("Mismatched parentheses: unclosed left parenthesis");
            }
            rpntokens.add(opstack.pop());
        }

        return rpntokens;
    }
}