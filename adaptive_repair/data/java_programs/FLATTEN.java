package java_programs;

import java.util.ArrayList;
import java.util.List;

public class FLATTEN {
    public static Object flatten(Object arr) {
        if (arr instanceof List) {
            List<Object> narr = (List<Object>) arr;
            List<Object> result = new ArrayList<>();
            for (Object x : narr) {
                if (x instanceof List) {
                    result.addAll((List<Object>) FLATTEN.flatten(x));
                } else {
                    result.add(x);
                }
            }
            return result;
        } else {
            return arr;
        }
    }
}