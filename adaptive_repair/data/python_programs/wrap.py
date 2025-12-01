def wrap(text, cols):
    lines = []
    if cols <= 0:
        # The original code had a logical bug when cols was 0 or negative.
        # In such cases, the `end = cols` assignment (within the `if end <= 0:` block)
        # would cause `line` to be an empty string and `text` to remain unchanged,
        # leading to an infinite loop. This infinite loop prevented the final segment
        # of the text from ever being appended.
        # The fix ensures that if cols is non-positive, the entire text is appended
        # as a single line (if not empty) and the function returns.
        if text:
            lines.append(text)
        return lines

    # The loop should continue as long as there is any text remaining to be processed.
    while text:
        # If the remaining text is short enough to fit on a single line,
        # or if it's the very last segment, append it and we're done.
        if len(text) <= cols:
            lines.append(text)
            text = "" # Mark text as fully processed to exit the loop
            break

        # Try to find the last space within the current column limit.
        # The slice `0, cols + 1` means we search in `text[0]` through `text[cols]`.
        end = text.rfind(' ', 0, cols + 1)

        # If 'end' is -1 (no space found in the first 'cols' characters)
        # or 'end' is 0 (the only space found is at the very beginning,
        # which would result in an empty line if we break there),
        # then we must break the word at 'cols'.
        if end <= 0:
            # Since cols is guaranteed to be > 0 at this point due to the initial check,
            # setting end = cols ensures progress and breaks the word.
            end = cols
        
        # Extract the line and the remaining text.
        line, text = text[:end], text[end:]
        lines.append(line)

    return lines