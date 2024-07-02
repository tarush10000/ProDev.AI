import sys
import os
import re
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QMessageBox, QInputDialog, QTextEdit, QHBoxLayout
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InternalServerError

# Ensure the API key is set
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
        prompt = f"Provide ONLY professional and detailed file structure for a {self.project_type} project. NO EXPLANATION."
        self.response1 = self.generate_content_with_debug(prompt, "file structure")
        self.display_content(self.response1, "File Structure")

    def generate_explanation(self):
        if self.response1:  # Check if response1 is not None
            prompt = f"Provide a professional and detailed explanation for the following file structure of a {self.project_type} project:\n{self.response1}"
            response2 = self.generate_content_with_debug(prompt, "explanation")
            self.display_content(response2, "Explanation")
        else:
            QMessageBox.warning(self, 'Generate File Structure First', 'Please generate the file structure first.')

    def generate_commands(self):
        prompt = f"Provide a comprehensive list of command-line commands to set up and run a {self.project_type} project using the following directory: {folder_path}. NO EXPLANATION IN BETWEEN COMMANDS, EASIER TO COPY PASTE."
        response = self.generate_content_with_debug(prompt, "commands")
        self.display_content(response, "CMD Commands")

    def generate_strategies(self):
        prompt = f"After the development of {self.software_description} using {self.project_type}, recommend the best testing strategies."
        response = self.generate_content_with_debug(prompt, "strategies")
        self.display_content(response, "Testing Strategies")

    def generate_deployment(self):
        prompt = f"After the development of {self.software_description} using {self.project_type}, recommend the best possible deployment methods."
        response = self.generate_content_with_debug(prompt, "deployment")
        self.display_content(response, "Deployment Methods")

    def generate_read_me(self):
        prompt = f"After the development of {self.software_description} using {self.project_type}, give detailed and professional content for README file."
        response = self.generate_content_with_debug(prompt, "read_me")
        self.display_content(response, "README")

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
