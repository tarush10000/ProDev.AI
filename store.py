import json
import os
import code_generation

# Define the path to the JSON file
json_file_path = os.path.join(os.path.dirname(__file__), 'data.json')

# Sample demo data
demoData = [
    {"title": "how to make a calculator in pyqt6", "content": {}},
    {"title": "how to make a video player in pyqt6", "content": {}},
    # ... other items ...
    {"title": "how to make a chat application last in pyqt6", "content": {}}
]

# Function to update the JSON file
def update_json_file():
    # Find the current item in demoData based on the project_type
    current_item = next((item for item in demoData if item['title'] == code_generation.project_type), None)

    if current_item:
        current_item['content'] = {
            'project_type': code_generation.project_type,
            'software_description': code_generation.software_description,
            'response1': code_generation.response1,
            'commands': code_generation.commands,
            'response2': code_generation.response2,
            'response3': code_generation.response3,
            'response4': code_generation.response4,
            'response5': code_generation.response5
        }

    # Read existing data if file exists
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    # Update or append the current item
    updated = False
    for item in existing_data:
        if item['title'] == code_generation.project_type:
            item['content'] = current_item['content']
            updated = True
            break
    
    if not updated:
        existing_data.append(current_item)

    # Write the updated data back to the file
    with open(json_file_path, 'w') as json_file:
        json.dump(existing_data, json_file, indent=2)

# Update the JSON file initially
update_json_file()

# Update the JSON file whenever the variables are updated
code_generation.update_callback = update_json_file