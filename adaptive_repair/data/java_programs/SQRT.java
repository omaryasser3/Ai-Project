package java_programs;

public class SQRT {
    public static double sqrt(double x, double epsilon) {
        double approx = x / 2.0;
        while (Math.abs(approx * approx - x) > epsilon) {
            approx = 0.5 * (approx + x / approx);
        }
        return approx;
    }
}