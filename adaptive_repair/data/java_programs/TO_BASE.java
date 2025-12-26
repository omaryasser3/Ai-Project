package java_programs;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class TO_BASE {
    public static String to_base(int num, int b) {
        List<Character> digits = new ArrayList<>();
        final String alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

        // Emulate a do-while loop to ensure it runs at least once,
        // which correctly handles num = 0 to produce "0".
        do {
            int i = num % b;
            num = num / b; // Integer division is default for int/int in Java
            digits.add(alphabet.charAt(i)); // Append the digit character
        } while (num != 0);

        // The digits are collected in reverse order (least significant first).
        // Reverse the list and join them into the final string.
        Collections.reverse(digits);

        StringBuilder resultBuilder = new StringBuilder(digits.size());
        for (char digit : digits) {
            resultBuilder.append(digit);
        }
        return resultBuilder.toString();
    }
}