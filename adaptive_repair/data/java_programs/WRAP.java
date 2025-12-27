package java_programs;

import java.util.ArrayList;
import java.util.List;

public class WRAP {

    public static void main(String[] args) {
        // This was a test line in the original Python code to understand rfind behavior.
        // The equivalent in Java for "abc".rfind("c", 0, 30 + 1) is "abc".lastIndexOf("c", 30).
        System.out.println("abc".lastIndexOf("c", 30));
    }

    public static List<String> wrap(String text, int cols) {
        List<String> lines = new ArrayList<>();

        while (text.length() > 0) { // Loop as long as there's text remaining
            if (text.length() <= cols) {
                // The remaining text fits on one line, so add it and we're done.
                lines.add(text);
                text = ""; // Mark text as fully processed
                break; // Exit the loop
            }
            
            // If text is longer than cols, try to find a break point
            // Java's lastIndexOf(search_string, from_index) searches backward from from_index.
            // This means it searches within text[0...from_index].
            // This matches Python's rfind(sub, 0, cols + 1) which searches text[0...cols].
            int end = text.lastIndexOf(" ", cols);

            if (end == -1) {
                // No space found within the first 'cols' characters, so break the word.
                end = cols;
            }
            
            String line = text.substring(0, end);
            text = text.substring(end);
            
            // After splitting, remove any leading spaces from the remaining text
            // to ensure the next line doesn't start with a space and to prevent
            // infinite loops if 'end' pointed to a space at the beginning of 'text'.
            text = text.stripLeading(); // Equivalent to Python's lstrip()
            
            lines.add(line);
        }
        
        return lines;
    }
}