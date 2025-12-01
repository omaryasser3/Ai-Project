def wrap(text, cols):
    lines = []
    while len(text) > cols:
        # Search for the last space within the current column width (inclusive of cols index)
        end = text.rfind(' ', 0, cols + 1)

        if end == -1: # No space found in the first 'cols' characters
            # This means a word is longer than 'cols', so we must break the word.
            end = cols
        elif end == 0 and len(text) > 1: # Only space found is at the beginning, and text is not just a single space
            # This means the text starts with a space, and the subsequent word might exceed 'cols'.
            # To ensure progress and consume the leading space, we take just the space.
            end = 1
        # else: end is a valid space index > 0, which is fine.

        line, text = text[:end], text[end:]
        lines.append(line)

    # After the loop, append any remaining text. This segment will have a length
    # less than or equal to 'cols', making it a valid final line.
    if text:
        lines.append(text)

    return lines