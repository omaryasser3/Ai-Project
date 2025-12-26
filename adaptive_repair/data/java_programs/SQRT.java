package java_programs;
import java.util.*;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author derricklin
 */
public class SQRT {
    public static double sqrt(double x, double epsilon) {
        // Handle non-positive input, though the Babylonian method is typically for positive numbers.
        // For simplicity, we'll assume x >= 0 as per typical sqrt function domain.
        if (x < 0) {
            throw new IllegalArgumentException("Cannot compute square root of a negative number.");
        }
        if (x == 0) {
            return 0;
        }

        double approx = x / 2d; // Initial guess
        if (approx == 0) { // Handle case where x is very small, e.g., x=0.0000000001
            approx = x; // A better initial guess for very small x
        }
        if (approx == 0) { // If x itself is 0, this will be 0, handled above. If x is tiny, approx might still be 0.
            approx = 1e-10; // A very small positive number to avoid division by zero if x is extremely small
        }

        // The loop terminates when the square of the approximation is close enough to x.
        // This means approx * approx is approximately equal to x.
        while (Math.abs(approx * approx - x) > epsilon) {
            approx = 0.5d * (approx + x / approx);
        }
        return approx;
    }
}