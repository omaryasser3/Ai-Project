package java_programs;

import java.util.ArrayList;
import java.util.List;

public class WRAP {
    public static void main(String[] args) {
        // Java's lastIndexOf(String str, int fromIndex) searches backward from fromIndex (inclusive).
        // Python's rfind(sub, start, end) searches in s[start:end] (end is exclusive).
        // To mimic Java's lastIndexOf(char, fromIndex), Python uses rfind(char, 0, fromIndex + 1).
        // So, Python's rfind("c", 0, 30 + 1) is equivalent to Java's lastIndexOf("c", 30).
        System.out.println("abc".lastIndexOf("c", 30));
    }

    public static List<String> wrap(String text, int cols) {
        List<String> lines = new ArrayList<>();

        while (text.length() > cols) {
            // Java's lastIndexOf(String str, int fromIndex) searches backward from fromIndex (inclusive).
            // Python's rfind(sub, start, end) searches in text[start:end] (end is exclusive).
            // To search up to 'cols' (inclusive) like Java, Python's 'end' parameter should be 'cols + 1'.
            // Thus, Python's rfind(" ", 0, cols + 1) is equivalent to Java's lastIndexOf(" ", cols).
            int splitPoint = text.lastIndexOf(" ", cols);

            String line;
            if (splitPoint == -1) { // No space found within the first 'cols' characters (or up to cols)
                splitPoint = cols; // Cut the word at 'cols'
                line = text.substring(0, splitPoint);
                text = text.substring(splitPoint);
            } else { // A space was found at 'splitPoint'
                line = text.substring(0, splitPoint);
                // Advance past the space character to avoid infinite loops or leading spaces
                text = text.substring(splitPoint + 1);
            }
            
            lines.add(line);
        }
        
        // The original code omitted the last segment of text if its length was <= cols.
        // This block ensures that any remaining text is added to the lines list.
        if (text.length() > 0) { // Only add if there's actual text left
            lines.add(text);
        }

        return lines;
    }
}