package java_programs;

import java.util.ArrayList;
import java.util.List;

public class GET_FACTORS {
    public static List<Integer> getFactors(int n) {
        if (n == 1) {
            return new ArrayList<>();
        }
        int maxVal = (int) Math.sqrt(n) + 1;
        for (int i = 2; i < maxVal; i++) {
            if (n % i == 0) {
                List<Integer> factors = new ArrayList<>();
                factors.add(i);
                factors.addAll(GET_FACTORS.getFactors(n / i));
                return factors;
            }
        }
        List<Integer> primeFactor = new ArrayList<>();
        primeFactor.add(n);
        return primeFactor;
    }
}