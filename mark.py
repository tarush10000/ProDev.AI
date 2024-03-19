import re

def detect_and_remove_markdown(code_text):
    # Define Markdown code block pattern for triple backticks, capturing content inside
    markdown_pattern = r'```(?:[\s\S]*?)\n?([\s\S]*?)\n?```'

    # Use re.findall to check if Markdown code blocks are present
    matches = re.findall(markdown_pattern, code_text)
    if matches:
        # Markdown detected, remove the enclosing backticks and keep the content
        modified_code = re.sub(markdown_pattern, r'\1', code_text)
        markdown_detected = True
    else:
        # No Markdown detected, return the original code
        modified_code = code_text
        markdown_detected = False
    
    return modified_code.strip(), markdown_detected

# Example usage
input_code = """
 ```python
import os

def create_directory(directory):
    try:
        os.mkdir(directory)
        print(f"Successfully created {directory}!")
    except FileExistsError:
        print("A file or directory with that name already exists.")

def navigate_to_directory(directory):
    try:
        os.chdir(directory)
        print(f"Successfully navigated to {directory}!")
    except FileNotFoundError:
        print("The specified directory does not exist.")

def prompt():
    return input("Enter a command (create, navigate): ")

def main():
    while True:
        command = prompt()
        if command == "create":
            directory = input("Enter a directory name: ")
            create_directory(directory)
        elif command == "navigate":
            directory = input("Enter a directory path: ")
            navigate_to_directory(directory)
        else:
            print("Invalid command.")
            continue
``` ```python
import os

def create_directory(directory):
    os.mkdir(directory)
    print(f"Successfully created {directory}!")

def navigate_to_directory(directory):
    os.chdir(directory)
    print(f"Successfully navigated to {directory}!")

def prompt():
    return input("Enter a command (create, navigate): ")

def main():
    while True:
        command = prompt()
        if command == "create":
            directory = input("Enter a directory name: ")
            create_directory(directory)
        elif command == "navigate":
            directory = input("Enter a directory path: ")
            navigate_to_directory(directory)
        else:
            print("Invalid command.")
            continue
"""


# Detect and remove Markdown
modified_code, markdown_detected = detect_and_remove_markdown(input_code)

# Output modified code
print("Modified Code:")
print(modified_code)

# Output whether Markdown was detected and removed
if markdown_detected:
    print("Markdown code block detected and removed.")
else:
    print("No Markdown code block detected.")

