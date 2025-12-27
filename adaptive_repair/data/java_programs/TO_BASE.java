package java_programs;

public class TO_BASE {
    public static String to_base(int num, int b) {
        StringBuilder digitsBuilder = new StringBuilder();
        String alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

        if (num == 0) {
            return "0";
        }

        while (num > 0) {
            int i = num % b;
            num = num / b;
            digitsBuilder.append(alphabet.charAt(i));
        }

        return digitsBuilder.reverse().toString();
    }
}