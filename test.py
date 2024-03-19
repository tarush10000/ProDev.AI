def modify_text(input_text):
    # Step 1: Remove unwanted characters
    modified_text = input_text.replace('[', '').replace(']', '').replace('{', '').replace('},', '\n').replace('}', '\n')

    # Step 2: Split the text into lines
    lines = modified_text.split('\n')

    # Step 3: Process each line
    processed_lines = []
    for line in lines:
        # Step 4: Check and remove text before the 2nd instance of ':'
        colon_index = line.find(':')
        second_colon_index = line.find(':', colon_index + 1)
        if second_colon_index != -1:
            line = line[second_colon_index + 1:]

        # Step 5: Remove inverted commas
        line = line.replace('"', '')

        # Step 6: Remove blank lines
        if line.strip():  # Check if line is not empty after stripping whitespace
            processed_lines.append(line)

    # Step 7: Write step number before each new line
    final_text = ""
    for i, line in enumerate(processed_lines, start=1):
        final_text += f"Step {i}: {line}\n"

    return final_text


if __name__ == "__main__":
    # Example usage
    input_text = """{
        "name": "John",
        "age": 30,
        "city": "New York"
    },
    {
        "name": "Alice",
        "age": 25,
        "city": "Los Angeles"
    }"""
    modified_text = modify_text(input_text)
    print(modified_text)

