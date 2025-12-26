package java_programs;

import java.util.ArrayList;
import java.util.List;
import java.lang.Math;

public class SIEVE {

    public static List<Integer> sieve(int maxVal) {
        if (maxVal < 2) {
            return new ArrayList<>();
        }

        // Initialize a boolean array where isPrime[i] is true if i is potentially prime
        // This array will be used to mark composite numbers.
        boolean[] isPrime = new boolean[maxVal + 1];
        // Initialize all elements to true, as per Python's [True] * N
        for (int i = 0; i <= maxVal; i++) {
            isPrime[i] = true;
        }

        isPrime[0] = false; // 0 is not prime
        isPrime[1] = false; // 1 is not prime

        // Iterate from 2 up to the square root of maxVal.
        // Any composite number n will have at least one prime factor less than or equal to sqrt(n).
        for (int p = 2; p <= Math.sqrt(maxVal); p++) {
            // If isPrime[p] is still true, then p is a prime number.
            if (isPrime[p]) {
                // Mark all multiples of p (starting from p*p) as not prime.
                // Multiples less than p*p (e.g., 2*p, 3*p, etc.) would have already been marked
                // by smaller prime factors (2, 3, etc.).
                for (int multiple = p * p; multiple <= maxVal; multiple += p) {
                    isPrime[multiple] = false;
                }
            }
        }

        // Collect all numbers that are marked as prime into a list.
        List<Integer> primes = new ArrayList<>();
        for (int i = 0; i <= maxVal; i++) {
            if (isPrime[i]) {
                primes.add(i);
            }
        }
        return primes;
    }
}