import json
import os
import code_generation

# Define the path to the JSON file
json_file_path = os.path.join(os.path.dirname(__file__), 'data.json')

# Function to update the JSON file
def update_json_file():
    data = {
        'project_type': code_generation.project_type,
        'software_description': code_generation.software_description,
        'response1': code_generation.response1,
        'commands': code_generation.commands,
        'response2': code_generation.response2,
        'response3': code_generation.response3,
        'response4': code_generation.response4,
        'response5': code_generation.response5
    }

    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file)

# Update the JSON file initially
update_json_file()

# Update the JSON file whenever the variables are updated
code_generation.update_callback = update_json_file