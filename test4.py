from multiprocessing import Process, Queue
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout, QLineEdit,QComboBox, QMessageBox, QStyle, QTableWidget, QTableWidgetItem, QAbstractItemView, QPlainTextEdit, QScrollArea, QHeaderView, QDateEdit, QTimeEdit, QCompleter, QAbstractScrollArea, QSizePolicy
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextCursor
import sys, os
from langchain_community.llms import Ollama
# import lag

steps = ""
step_dict = ""
count = 0
codes = []
desc = ""
ext_desc = ""

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

from PyQt5.QtCore import QThread

def generate_codes(step_dict, output_queue):
    codes = []
    llm = Ollama(model="codellama:13b")
    for i in step_dict:
        j = step_dict[i]
        if "shell" in j.lower():
            query = "Write the code for the shell command " + i
        elif "code" in j.lower():
            query = "Write the code for the command " + i
        else:
            continue
        result = ""
        for chunks in llm.stream(query):
            result += chunks
        codes.append(result)
    output_queue.put(codes)

class CodeGenerationProcess:
    def __init__(self, step_dict):
        self.step_dict = step_dict
        self.output_queue = Queue()

    def start(self):
        self.process = Process(target=generate_codes, args=(self.step_dict, self.output_queue))
        self.process.start()

    def get_codes(self):
        self.process.join()
        return self.output_queue.get()
       


class Worker(QObject):
    finished = pyqtSignal()
    update_text = pyqtSignal(str)

    def __init__(self, input, OS):
        super().__init__()
        self.input = input
        self.OS = OS

    def run_query_1(self):
        llm = Ollama(model="mistral")
        query = "Write the steps that a software engineer would use in order to make a software using Python with frontend using PyQt that would be able to" + self.input + "each step should be written in a way to classify it into 1 of the following 2 categories -1. Shell -> Needs some code to be written in the Command Prompt or Terminal2. Code -> That can be directly copied and pasted into VS Code3. The steps should be detailed enough that they could be used as a prompt to instruct some AI to do the next task and not contain any code or additional info as it would be added later by the other AI on" + self.OS + "operating system"
        print(query)
        result = ""
        for chunks in llm.stream(query):
            result += chunks
            self.update_text.emit(chunks)
            global steps
            steps = result
        self.finished.emit()

class PDA(QWidget):
    def __init__(self):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        # set window properties
        self.setWindowTitle('ProDev.AI')
        screen_height = self.app.desktop().screenGeometry().height()
        screen_width = self.app.desktop().screenGeometry().width()
        self.setFixedSize(screen_width, screen_height)
        self.setStyleSheet("background-color: rgb(12, 12, 12);")
        self.showMaximized()

        # main layout of the window
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignVCenter)
        main_screen_widget = QWidget()
        main_screen_widget.setStyleSheet("background-color: rgb(12, 12, 12); color : rgb(255,255,255); padding: 10px")
        main_screen_widget.setLayout(layout)

        directory_layout = QVBoxLayout()
        directory_layout.setAlignment(Qt.AlignVCenter)       

        logo = QLabel()
        logo_image = QPixmap(resource_path('images/logo.png'))
        logo_image = logo_image.scaledToWidth(int(screen_width * 0.14))
        logo.setPixmap(logo_image)
        logo.setAlignment(Qt.AlignCenter)

        actual_directory_widget = QWidget()
        actual_directory_layout = QVBoxLayout()
        actual_directory_layout.setAlignment(Qt.AlignTop)
        actual_directory_widget.setLayout(actual_directory_layout)
        actual_directory_widget.setStyleSheet("background-color: rgb(50,50,50); font-size: 17px; padding: 10px;")
        actual_directory_widget.setFixedWidth(int(screen_width * 0.15))
        actual_directory_widget.setFixedHeight(int(screen_height * 0.9))

        directory_layout.addWidget(logo)
        directory_layout.addWidget(actual_directory_widget)

        workspace_layout = QVBoxLayout()
        workspace_layout.setSpacing(0)
        workspace_layout.setAlignment(Qt.AlignVCenter)
        workspace_widget = QWidget()
        workspace_widget.setLayout(workspace_layout)

        step_area_layout = QHBoxLayout()
        step_area_layout.setSpacing(20)
        step_area_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        step_area_widget = QWidget()
        step_area_widget.setLayout(step_area_layout)
        step_area_widget.setStyleSheet("padding: 10px;")
        step_area_widget.setFixedHeight(int(screen_height * 0.8))
        step_area_widget.setFixedWidth(int(screen_width * 0.8))

        step_layout = QVBoxLayout()
        step_layout.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        step_widget = QWidget()
        step_widget.setLayout(step_layout)
        step_widget.setStyleSheet("padding: 10px;  border: 1px solid rgb(255,255,255); border-radius: 20px")
        step_edit_play_layout = QHBoxLayout()
        step_edit_play_layout.setAlignment(Qt.AlignRight)
        step_edit_play_widget = QWidget()
        step_edit_play_widget.setLayout(step_edit_play_layout)
        step_edit_play_widget.setStyleSheet("padding: 10px; border: 0px;")
        step_edit_button = QPushButton()
        step_edit_image = QPixmap(resource_path('images/edit.png'))
        step_edit_image = step_edit_image.scaledToHeight(int(screen_height * 0.05))
        step_edit_button.setIcon(QIcon(step_edit_image))
        step_edit_button.setCursor(Qt.PointingHandCursor)
        step_edit_button.setFlat(True)
        step_edit_button.clicked.connect(lambda: self.edit_steps(step_edit_button, step_save_button, step_text_widget, step_edit_play_layout, step_play_button))
        step_save_button = QPushButton()
        step_save_image = QPixmap(resource_path('images/save.png'))
        step_save_image = step_save_image.scaledToHeight(int(screen_height * 0.05))
        step_save_button.setIcon(QIcon(step_save_image))
        step_save_button.setCursor(Qt.PointingHandCursor)
        step_save_button.setFlat(True)
        step_save_button.setVisible(False)
        step_save_button.clicked.connect(lambda: self.save_edit_steps(step_edit_button, step_save_button, step_text_widget, step_edit_play_layout, step_play_button))
        step_play_button = QPushButton()
        step_play_image = QPixmap(resource_path('images/play.png'))
        step_play_image = step_play_image.scaledToHeight(int(screen_height * 0.05))
        step_play_button.setIcon(QIcon(step_play_image))
        step_play_button.setCursor(Qt.PointingHandCursor)
        step_play_button.setFlat(True)
        step_play_button.clicked.connect(lambda: self.run_description(step_description_widget, step_play_button, step_prev_button, step_next_button, step_heading_label))
        
        step_edit_play_layout.addWidget(step_edit_button)
        step_edit_play_layout.addWidget(step_save_button)
        step_edit_play_layout.addWidget(step_play_button)

        step_text_widget = QPlainTextEdit()
        step_text_widget.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 23px")
        step_text_widget.setFixedWidth(int(screen_width * 0.37))
        step_text_widget.setReadOnly(True)
        step_layout.addWidget(step_edit_play_widget)
        step_layout.addWidget(step_text_widget)

        step_description_layout = QVBoxLayout()
        step_description_layout.setContentsMargins(0, 0, 0, 0)
        step_description_layout.setAlignment(Qt.AlignTop)
        step_description_widget = QWidget()
        step_description_widget.setLayout(step_description_layout)
        step_description_widget.setStyleSheet("background-color: rgb(50,50,50);color: rgb(255,255,255) ;font-size: 17px; border-radius: 20px; margin: 0px; padding: 0px;")
        step_description_widget.setFixedWidth(int(screen_width * 0.37))
        step_description_heading_layout = QHBoxLayout()
        step_description_heading_layout.setAlignment(Qt.AlignHCenter)
        step_description_heading_layout.setContentsMargins(0, 0, 0, 0)
        step_description_heading_widget = QWidget()
        step_description_heading_widget.setLayout(step_description_heading_layout)
        step_description_heading_widget.setStyleSheet("background-color: #3A46AC; padding: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border: 0px; margin: 0px")
        step_description_heading_widget.setFixedHeight(int(screen_height * 0.04))
        global count 
        step_heading_label = QLabel("Step " + str(count))
        step_heading_label.setVisible(False)
        step_heading_label.setStyleSheet("color: rgb(255,255,255); font-size: 17px; font: Montserrat; border: 0px; font-weight: 500")
        step_prev_button_image = QPixmap(resource_path('images/prev.png'))
        step_prev_button_image = step_prev_button_image.scaledToHeight(int(screen_height * 0.03))
        step_prev_button = QPushButton()
        step_prev_button.setIcon(QIcon(step_prev_button_image))
        step_prev_button.setCursor(Qt.PointingHandCursor)
        step_prev_button.setFlat(True)
        step_prev_button.setVisible(False)
        step_prev_button.clicked.connect(lambda: self.prev_step(step_heading_label, code_heading_label, code_heading_widget, code_text_widget, code_description_heading_widget, code_description_text_widget))
        step_next_button_image = QPixmap(resource_path('images/next.png'))
        step_next_button_image = step_next_button_image.scaledToHeight(int(screen_height * 0.03))
        step_next_button = QPushButton()
        step_next_button.setIcon(QIcon(step_next_button_image))
        step_next_button.setCursor(Qt.PointingHandCursor)
        step_next_button.setVisible(False)
        step_next_button.setFlat(True)

        step_description_heading_layout.addWidget(step_prev_button)
        step_description_heading_layout.addWidget(step_heading_label)
        step_description_heading_layout.addWidget(step_next_button)

        step_description_content_layout = QVBoxLayout()
        step_description_content_layout.setSpacing(30)  
        step_description_content_widget = QWidget()
        step_description_content_widget.setLayout(step_description_content_layout)
        step_description_content_widget.setStyleSheet("background-color: rgb(50,50,50);padding: 10px; border: 0px")
        step_description_content_layout.setAlignment(Qt.AlignVCenter)
        step_description_content_layout.setContentsMargins(15, 15, 15, 15)

        code_layout = QVBoxLayout()
        code_layout.setAlignment(Qt.AlignTop)
        code_layout.setContentsMargins(0, 0, 0, 0)
        code_widget = QWidget()
        code_widget.setLayout(code_layout)
        code_widget.setStyleSheet("background-color: #212121;border-radius: 20px; border: 0px; margin: 0px; padding: 0px;")
        code_widget.setFixedHeight(int(screen_height * 0.3))
        code_heading_layout = QHBoxLayout()
        code_heading_layout.setContentsMargins(0,0,0,0)
        code_heading_widget = QWidget()
        code_heading_widget.setLayout(code_heading_layout)
        code_heading_widget.setStyleSheet("background-color: #3A46AC; padding: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border: 0px; margin: 0px")
        code_heading_widget.setFixedHeight(int(screen_height * 0.04))
        code_heading_label = QLabel("Code")
        code_heading_label.setStyleSheet("color: rgb(255,255,255); font-size: 17px; font: Montserrat; border: 0px; font-weight: 500")

        code_heading_layout.addWidget(code_heading_label)

        code_text_layout = QVBoxLayout()
        code_text_widget = QPlainTextEdit()
        code_text_widget.setStyleSheet("color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 20px; font: Montserrat; border-top-left-radius: 0px; border-top-right-radius: 0px; border: 0px;")
        code_text_widget.setLayout(code_text_layout) 
        code_text_widget.setReadOnly(True)       

        code_layout.addWidget(code_heading_widget)  
        code_layout.addWidget(code_text_widget)

        code_description_layout = QVBoxLayout()
        code_description_layout.setAlignment(Qt.AlignTop)
        code_description_layout.setContentsMargins(0, 0, 0, 0)
        code_description_widget = QWidget()
        code_description_widget.setLayout(code_description_layout)
        code_description_widget.setStyleSheet("background-color: #212121;padding: 10px; border-radius: 20px; border: 0px;")
        code_description_widget.setFixedHeight(int(screen_height * 0.3))
        code_description_heading_layout = QHBoxLayout()
        code_description_heading_layout.setContentsMargins(0,0,0,0)
        code_description_heading_widget = QWidget()
        code_description_heading_widget.setLayout(code_description_heading_layout)
        code_description_heading_widget.setStyleSheet("background-color: #3A46AC; padding: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border: 0px; margin: 0px")
        code_description_heading_widget.setFixedHeight(int(screen_height * 0.04)) 
        code_description_heading_label = QLabel("Description")
        code_description_heading_label.setStyleSheet("color: rgb(255,255,255); font-size: 17px; font: Montserrat; border: 0px; font-weight: 500")
        code_description_text_layout = QVBoxLayout()
        code_description_text_widget = QPlainTextEdit()
        code_description_text_widget.setStyleSheet("color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 20px; font: Montserrat; border-top-left-radius: 0px; border-top-right-radius: 0px; border: 0px;")
        code_description_text_widget.setLayout(code_description_text_layout)
        code_description_text_widget.setReadOnly(True)

        code_description_heading_layout.addWidget(code_description_heading_label)

        code_description_layout.addWidget(code_description_heading_widget)
        code_description_layout.addWidget(code_description_text_widget)


        step_description_content_layout.addWidget(code_widget)
        step_description_content_layout.addWidget(code_description_widget)

        step_description_layout.addWidget(step_description_heading_widget)
        step_description_layout.addWidget(step_description_content_widget)

        step_area_layout.addWidget(step_widget)
        step_area_layout.addWidget(step_description_widget)

        instruction_layout = QHBoxLayout()
        instruction_widget = QWidget()
        instruction_widget.setLayout(instruction_layout)
        instruction_text_widget = QPlainTextEdit()
        instruction_text_widget.setStyleSheet("border-radius : 20px; color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 2px solid rgb(255,255,255);")
        instruction_text_widget.setFixedHeight(int(screen_height * 0.07))
        instruction_send_button = QPushButton()
        instruction_send_image = QPixmap(resource_path('images/play.png'))
        instruction_send_image = instruction_send_image.scaledToHeight(int(screen_height * 0.05))
        instruction_send_button.setIcon(QIcon(instruction_send_image))
        instruction_send_button.setCursor(Qt.PointingHandCursor)
        instruction_send_button.setFlat(True)
        OS = "Windows"
        instruction_send_button.clicked.connect(lambda: self.run_query(instruction_text_widget.toPlainText(), step_text_widget, OS, instruction_send_button))

        instruction_layout.addWidget(instruction_text_widget)
        instruction_layout.addWidget(instruction_send_button)

        workspace_layout.addWidget(step_area_widget)
        workspace_layout.addWidget(instruction_widget)


        layout.addLayout(directory_layout)
        layout.addWidget(workspace_widget)
        
        self.setLayout(layout)
    
    def show_error(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxCritical')))
        error_box.setStyleSheet(
                    "QMessageBox {"
                    "background-color: rgb(0,0,0);"
                    "}"
                    "QMessageBox QLabel {"
                    "color: #ffffff;"
                    "font-size: 14px;"
                    "}"
                    "QMessageBox QPushButton {"
                    "background-color: #007ACC;"
                    "color: white;"
                    "border: 1px solid #007ACC;"
                    "border-radius: 10px;"
                    "width: 100px;"
                    "height: 30px;"
                    "}"
                    "QMessageBox QPushButton:hover {"
                    "background-color: #005EAD;"
                    "}"
                )
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()

    def run_query(self, input, steps_widget, OS, send_icon):
        
        check = self.check_input(input)
        if "Yes" in check:
            self.worker = Worker(input, OS)
            icon_image = QPixmap(resource_path('images/play-blue.png'))
            icon_image = icon_image.scaledToHeight(int(self.app.desktop().screenGeometry().height() * 0.05))
            send_icon.setIcon(QIcon(icon_image))
            steps_widget.clear()
            self.worker.update_text.connect(lambda text: self.append_text(text, steps_widget, OS))
            self.worker.finished.connect(self.worker_finished)
            self.worker_thread = QThread()
            self.worker.moveToThread(self.worker_thread)
            self.worker_thread.started.connect(self.worker.run_query_1)
            self.worker_thread.start()
        else:
            self.show_error(check)
            return
        

    def check_input(self, user_input):
        llm = Ollama(model="mistral")
        query = "You have to tell if the given prompt is a valid description of a software. Prompt: " + user_input + " .Reply 'Yes' or 'No' only and the result shouldn't exceed 15 words."
        result = ""
        for chunks in llm.stream(query):
            result += chunks
        print(result)
        return result

    def append_text(self, text, steps_widget, OS):
        steps_widget.moveCursor(QTextCursor.End)
        steps_widget.insertPlainText(text)

    def worker_finished(self):
        self.worker_thread.quit()
        self.worker_thread.wait()

    def edit_steps(self, step_edit_button, step_save_button, step_text_widget, step_edit_play_layout, step_play_button):
        step_edit_button.setVisible(False)
        step_save_button.setVisible(True)
        step_text_widget.setReadOnly(False)  
        step_play_button.setVisible(False)

    def save_edit_steps(self, step_edit_button, step_save_button, step_text_widget, step_edit_play_layout, step_play_button):
        step_edit_button.setVisible(True)
        step_save_button.setVisible(False)
        step_text_widget.setReadOnly(True)  
        step_play_button.setVisible(True)
        global steps
        steps = step_text_widget.toPlainText()
        print(steps)
    
    def categorize_text(self , input_text):
        parts = input_text.split('Category')[1:] 
        print(parts)    
        output = []
        
        for part in parts:
            print(">>>>>>>>>>>>running categorize_text function part <<<<<<<<<<<")
            lines = part.strip().split('\n', 1)
            category_name = lines[0].strip()
            text = lines[1].strip() if len(lines) > 1 else ''
            output.append({category_name: text})
        
        return output   

    def format_text_data(self , input_text):
        lines = input_text.split('\n')
        formatted_entries = []
        current_entry = []
        
        for line in lines:
            if line.strip():
                if line[0].isdigit():
                    if current_entry:
                        formatted_entries.append(' '.join(current_entry))
                        current_entry = []
                    current_entry.append(line[1:].strip())
                else:
                    current_entry.append(line.strip())
        if current_entry:
            formatted_entries.append(' '.join(current_entry))
        
        return formatted_entries

    def create_dict(self,json_data):
        result = {}
        for i in json_data:
            for command in self.format_text_data(list(i.values())[0]):
                if "Shell" in list(i.keys())[0]:
                    result[command] = "Shell"
                elif "Code" in list(i.keys())[0]:
                    result[command] = "Code"
        print ("results >>>>>>>>>>" ,result)
        return result
            
    
    def run_description(self, steps_widget, send_icon, step_prev_button, step_next_button, step_heading_label):        
        step_prev_button.setVisible(True)
        step_next_button.setVisible(True)
        step_heading_label.setVisible(True)
        print(">>>>>>>>>>>>running description function <<<<<<<<<<<")
        global steps
        json_data = self.categorize_text(steps)
        print(json_data)
        global step_dict
        step_dict = self.create_dict(json_data)
        code_gen_process = CodeGenerationProcess(step_dict)
        code_gen_process.start()
        codes = code_gen_process.get_codes()
        print(codes)


if __name__ == '__main__':

    app = QApplication([])
    PDA_ui = PDA()
    PDA_ui.show()
    app.exec_()