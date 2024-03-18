from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout, QLineEdit,QComboBox, QMessageBox, QStyle, QTableWidget, QTableWidgetItem, QAbstractItemView, QPlainTextEdit, QScrollArea, QHeaderView, QDateEdit, QTimeEdit, QCompleter, QAbstractScrollArea, QSizePolicy
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextCursor
import sys, os
from langchain_community.llms import Ollama
# import lag

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


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
        self.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.showMaximized()

        # main layout of the window
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignVCenter)
        main_screen_widget = QWidget()
        main_screen_widget.setStyleSheet("background-color: rgb(0,0,0); color : rgb(255,255,255); padding: 10px")
        main_screen_widget.setLayout(layout)

        directory_layout = QVBoxLayout()
        directory_layout.setAlignment(Qt.AlignVCenter)
        expected_directory_widget = QWidget()
        expected_directory_layout = QVBoxLayout()
        expected_directory_layout.setAlignment(Qt.AlignTop)
        expected_directory_widget.setLayout(expected_directory_layout)
        expected_directory_widget.setStyleSheet("background-color: rgb(50,50,50); font-size: 17px; padding: 10px;")
        expected_directory_widget.setFixedWidth(int(screen_width * 0.15))
        expected_directory_widget.setFixedHeight(int(screen_height * 0.45))        

        actual_directory_widget = QWidget()
        actual_directory_layout = QVBoxLayout()
        actual_directory_layout.setAlignment(Qt.AlignTop)
        actual_directory_widget.setLayout(actual_directory_layout)
        actual_directory_widget.setStyleSheet("background-color: rgb(50,50,50); font-size: 17px; padding: 10px;")
        actual_directory_widget.setFixedWidth(int(screen_width * 0.15))
        actual_directory_widget.setFixedHeight(int(screen_height * 0.45))

        directory_layout.addWidget(expected_directory_widget)
        directory_layout.addWidget(actual_directory_widget)

        workspace_layout = QVBoxLayout()
        workspace_layout.setAlignment(Qt.AlignVCenter)
        workspace_widget = QWidget()
        workspace_widget.setLayout(workspace_layout)

        step_area_layout = QHBoxLayout()
        step_area_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        step_area_widget = QWidget()
        step_area_widget.setLayout(step_area_layout)
        step_area_widget.setStyleSheet("padding: 10px;")
        step_area_widget.setFixedHeight(int(screen_height * 0.8))
        step_area_widget.setFixedWidth(int(screen_width * 0.8))

        step_layout = QVBoxLayout()
        step_layout.setAlignment(Qt.AlignVCenter)
        step_widget = QWidget()
        step_widget.setLayout(step_layout)
        step_widget.setStyleSheet("padding: 10px;  border: 2px solid rgb(255,255,255); border-radius: 20px")
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
        step_play_button = QPushButton()
        step_play_image = QPixmap(resource_path('images/play.png'))
        step_play_image = step_play_image.scaledToHeight(int(screen_height * 0.05))
        step_play_button.setIcon(QIcon(step_play_image))
        step_play_button.setCursor(Qt.PointingHandCursor)
        step_play_button.setFlat(True)
        
        step_edit_play_layout.addWidget(step_edit_button)
        step_edit_play_layout.addWidget(step_play_button)

        step_text_widget = QPlainTextEdit()
        step_text_widget.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 0px")
        step_text_widget.setFixedWidth(int(screen_width * 0.37))
        step_text_widget.setReadOnly(True)
        step_layout.addWidget(step_edit_play_widget)
        step_layout.addWidget(step_text_widget)

        step_description_layout = QVBoxLayout()
        step_description_widget = QWidget()
        step_description_widget.setLayout(step_description_layout)
        step_description_widget.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255) ;font-size: 17px; padding: 10px;")
        step_description_widget.setFixedWidth(int(screen_width * 0.37))

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

if __name__ == '__main__':

    app = QApplication([])
    PDA_ui = PDA()
    PDA_ui.show()
    app.exec_()