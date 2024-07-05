import sys
import os
import re
import time
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QMessageBox, QInputDialog, QTextEdit, QHBoxLayout
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InternalServerError
# Ensure the API key is set
genai.configure(api_key=os.getenv("Gemini_API"))


# Initialize the generative model
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

folder_path = ""

class FolderCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.project_type = None
        self.software_description = None
        self.response1 = None  # Initialize response1 here
        self.commands = None  # Initialize commands here
        self.response2 = None
        self.response3 = None
        self.response4 = None
        self.response5 = None
        
    def initUI(self):
        self.setWindowTitle('Folder Creator')

        layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        self.create_folder_button = QPushButton('Create Folder', self)
        self.create_folder_button.clicked.connect(self.create_folder)
        button_layout.addWidget(self.create_folder_button)
        
        self.file_structure_button = QPushButton('File Structure', self)
        self.file_structure_button.clicked.connect(self.generate_file_structure)
        self.file_structure_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.file_structure_button)
        
        self.explanation_button = QPushButton('Explanation', self)
        self.explanation_button.clicked.connect(self.generate_explanation)
        self.explanation_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.explanation_button)
        
        self.commands_button = QPushButton('CMD Commands', self)
        self.commands_button.clicked.connect(self.generate_commands)
        self.commands_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.commands_button)
        
        self.run_button = QPushButton('Run', self)
        self.run_button.clicked.connect(self.run_commands)
        self.run_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.run_button)
        
        self.strategies_button = QPushButton('Testing Strategies', self)
        self.strategies_button.clicked.connect(self.generate_strategies)
        self.strategies_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.strategies_button)
        
        self.deployment_button = QPushButton('Deployment Methods', self)
        self.deployment_button.clicked.connect(self.generate_deployment)
        self.deployment_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.deployment_button)
        
        self.read_me_button = QPushButton('README', self)
        self.read_me_button.clicked.connect(self.generate_read_me)
        self.read_me_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.read_me_button)
        
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_read_me)
        self.save_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)

        self.text_edit = QTextEdit(self)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)

    def create_folder(self):
        global folder_path
        
        # Open the file dialog to select the folder path
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", options=options)

        if folder_path:
            try:
                # Create the folder
                os.makedirs(folder_path, exist_ok=True)
                QMessageBox.information(self, 'Success', f'Folder created at: {folder_path}')
                self.get_user_input()
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not create folder: {e}')

    def get_user_input(self):
        self.project_type, ok = QInputDialog.getText(self, 'User Input', 'Enter your project type:')
        self.software_description, ok1 = QInputDialog.getText(self, 'User Input', 'What does your software do:')
        if ok and ok1:
            self.enable_buttons()
        else:
            QMessageBox.warning(self, 'Input Error', 'Both inputs are required.')

    def enable_buttons(self):
        self.file_structure_button.setEnabled(True)
        self.explanation_button.setEnabled(True)
        self.commands_button.setEnabled(True)
        self.strategies_button.setEnabled(True)
        self.deployment_button.setEnabled(True)
        self.read_me_button.setEnabled(True)

    def generate_file_structure(self):
        print("Project Type:", self.project_type)  # Debugging: Print the project type
        prompt = f"Provide ONLY professional and detailed file structure for a {self.project_type} project. NO EXPLANATION."
        self.response1 = self.generate_content_with_debug(prompt, "file structure")
        self.display_content(self.response1, "File Structure")

    def generate_explanation(self):
        if self.response1:  # Check if response1 is not None
            prompt = f"Provide a professional and detailed explanation for the following file structure of a {self.project_type} project:\n{self.response1}."
            self.response2 = self.generate_content_with_debug(prompt, "explanation")
            self.display_content(self.response2, "Explanation")
        else:
            QMessageBox.warning(self, 'Generate File Structure First', 'Please generate the file structure first.')

    def generate_commands(self):
        prompt = f"Provide a comprehensive list of command-line commands to set up and run a {self.project_type} project using the following directory: {folder_path}. NO EXPLANATION IN BETWEEN COMMANDS, EASIER TO COPY PASTE."
        self.commands = self.generate_content_with_debug(prompt, "commands")
        self.display_content(self.commands, "CMD Commands")
        self.run_button.setEnabled(True)  # Enable the run button after generating commands

    def generate_strategies(self):
        prompt = f"After the development of {self.software_description} using {self.project_type}, recommend the best testing strategies."
        self.response3 = self.generate_content_with_debug(prompt, "strategies")
        self.display_content(self.response3, "Testing Strategies")

    def generate_deployment(self):
        prompt = f"After the development of {self.software_description} using {self.project_type}, recommend the best possible deployment methods."
        self.response4 = self.generate_content_with_debug(prompt, "deployment")
        self.display_content(self.response4, "Deployment Methods")

    def generate_read_me(self):
        prompt = f"After the development of {self.software_description} using {self.project_type}, give detailed and professional content for README file. For example, in a Python project, include sections for installation, usage, and contributing guidelines. In a C++ project, include sections for building, running, and testing the application."
        self.response5 = self.generate_content_with_debug(prompt, "read_me")
        self.display_content(self.response5, "README")
        self.save_button.setEnabled(True)  # Enable the save button after generating README


    def generate_content_with_debug(self, prompt, description):
        max_retries = 5
        delay = 1  # Initial delay in seconds
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                print(f"Response for {description}:", response)  # Debugging: Print the entire response object

                if response.candidates and response.candidates[0].content.parts:
                    text_parts = [part.text for part in response.candidates[0].content.parts]
                    return ''.join(text_parts)
                else:
                    QMessageBox.critical(self, 'Content Error', f'The generated {description} content is invalid or blocked.')
                    return ""
            except InternalServerError as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed with InternalServerError. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            except ResourceExhausted as e:
                QMessageBox.critical(self, 'API Quota Exceeded', f'API quota has been exhausted. Please try again later.\n{e}')
                return ""
            except ValueError as e:
                QMessageBox.critical(self, 'Content Error', f'Error generating {description}: {e}')
                return ""
        QMessageBox.critical(self, 'Content Error', f'Failed to generate {description} content after {max_retries} attempts.')
        return ""

    def run_commands(self):
        if not self.commands:
            QMessageBox.warning(self, 'Generate Commands First', 'Please generate the commands first.')
            return

        # Prepare the commands to be written to a batch file
        batch_content = self.commands.replace("<br>", "\n")

        script_path = os.path.join(folder_path, "run_commands.bat")
        try:
            with open(script_path, "w") as file:
                file.write(batch_content)
            print(f"Commands to be run:\n{batch_content}")  # Debugging: Print the commands to be run
            print(f"Batch script path: {script_path}")  # Debugging: Print the batch script path
            # Run the batch file
            subprocess.run(["cmd", "/c", script_path], check=True)
            QMessageBox.information(self, 'Success', 'Commands executed successfully.')
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, 'Execution Error', f'Error running commands: {e}')
        except Exception as e:
            QMessageBox.critical(self, 'Execution Error', f'Error: {e}')

    def save_read_me(self):
        if self.response5:
            read_me_path = os.path.join(folder_path, "README.md")
            try:
                with open(read_me_path, "w", encoding="utf-8") as file:
                    file.write(self.response5)
                QMessageBox.information(self, 'Success', 'README.md file saved successfully.')
            except Exception as e:
                QMessageBox.critical(self, 'Save Error', f'Could not save README.md file: {e}')
        else:
            QMessageBox.warning(self, 'Generate README First', 'Please generate the README content first.')


    def display_content(self, content, title):
        self.text_edit.append(f"<h1 style='color:blue;'>{title}</h1>")
        self.text_edit.append(f"<div>{self.clean_response(content)}</div>")

    def clean_response(self, text):
        # Convert text between asterisks to bold using HTML <b> tags
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.*?)\*', r'<b>\1</b>', text)
        # Convert text between triple quotes to preformatted text using HTML <pre> tags
        text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
        # Replace newlines with <br> tags to preserve line breaks
        text = text.replace('\n', '<br>')
        # Remove '##' and make the following text bold
        text = re.sub(r'##\s*(.*?)<br>', r'<b>\1</b><br>', text)
        return text
    

def main():
    app = QApplication(sys.argv)
    ex = FolderCreator()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()




def create_folder(self):
    global folder_path
    
    # Open the file dialog to select the folder path
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    folder_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", options=options)

    if folder_path:
        try:
            # Create the folder
            os.makedirs(folder_path, exist_ok=True)
            QMessageBox.information(self, 'Success', f'Folder created at: {folder_path}')
            return folder_path
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not create folder: {e}')
def generate_file_structure(self , query , tech_stack):
    prompt = f"Provide ONLY professional and detailed file structure for a {query} project using {tech_stack}. NO EXPLANATION."
    return generate_content_with_debug(self , prompt, "file structure")
    
def generate_content_with_debug(self, prompt, description):
    max_retries = 5
    delay = 1  # Initial delay in seconds
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            print(f"Response for {description}:", response)  # Debugging: Print the entire response object

            if response.candidates and response.candidates[0].content.parts:
                text_parts = [part.text for part in response.candidates[0].content.parts]
                return ''.join(text_parts)
            else:
                QMessageBox.critical(self, 'Content Error', f'The generated {description} content is invalid or blocked.')
                return ""
        except InternalServerError as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed with InternalServerError. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
        except ResourceExhausted as e:
            QMessageBox.critical(self, 'API Quota Exceeded', f'API quota has been exhausted. Please try again later.\n{e}')
            return ""
        except ValueError as e:
            QMessageBox.critical(self, 'Content Error', f'Error generating {description}: {e}')
            return ""
    QMessageBox.critical(self, 'Content Error', f'Failed to generate {description} content after {max_retries} attempts.')
    return ""

def generate_implementation(self , query , technology , file_stucture):
    prompt = f"Provide a professional and detailed implementation for a {query} project using {technology} whith the following file structure \n{file_stucture}."
    data = clean_response(self ,generate_content_with_debug(self , prompt, "explanation"))
    return f"<div>{data}</div>"
    

def generate_strategies(self , query , technology):
    prompt = f"After the development of {query} using {technology}, recommend the best testing strategies."
    data = clean_response(self , generate_content_with_debug(self , prompt, "strategies"))
    return  f"<div>{data}</div>"

def generate_deployment(self, query , technology):
    prompt = f"After the development of {query} using {technology}, recommend the best possible deployment methods."
    data = clean_response(self ,generate_content_with_debug(self , prompt, "deployment"))
    return  f"<div>{data}</div>"

def generate_read_me(self, query , technology):
    prompt = f"After the development of {query} using {technology}, give detailed and professional content for README file. For example, in a Python project, include sections for installation, usage, and contributing guidelines. In a C++ project, include sections for building, running, and testing the application."
    data = generate_content_with_debug(self , prompt, "read_me")
    cleanData = clean_response(self , data)
    return  f"<div>{cleanData}</div>" , data

def clean_response(self, text):
    # Convert text between asterisks to bold using HTML <b> tags
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<b>\1</b>', text)
    # Convert text between triple quotes to preformatted text using HTML <pre> tags
    text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
    # Replace newlines with <br> tags to preserve line breaks
    text = text.replace('\n', '<br>')
    # Remove '##' and make the following text bold
    text = re.sub(r'##\s*(.*?)<br>', r'<b>\1</b><br>', text)
    return text

def save_read_me(self , folder_path , data):
    if data:
        read_me_path = os.path.join(folder_path, "README.md")
        try:
            print("folder_path" , folder_path)
            print(folder_path , read_me_path)
            with open(read_me_path, "w", encoding="utf-8") as file:
                file.write(data)
            QMessageBox.information(self, 'Success', 'README.md file saved successfully.')
        except Exception as e:
            QMessageBox.critical(self, 'Save Error', f'Could not save README.md file: {e}')
    else:
        QMessageBox.warning(self, 'Generate README First', 'Please generate the README content first.')