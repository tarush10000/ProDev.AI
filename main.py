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
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        margin = int(screen_height * 0.03)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(0)

        # layout 1
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_widget = QWidget()
        main_widget.setStyleSheet("")
        main_widget.setContentsMargins(0, 0, 0, 0)
        main_widget.setFixedHeight(int(0.9*screen_height))
        main_widget.setLayout(main_layout)
        
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        logo_image = QPixmap(resource_path('images/logo.png'))
        logo_image = logo_image.scaledToHeight(int(screen_height * 0.03))
        logo_label = QLabel()
        logo_label.setPixmap(logo_image)
        logo_layout.addWidget(logo_label)

        step_layout = QVBoxLayout()
        step_layout.setAlignment(Qt.AlignTop)
        step_edit_play_layout = QHBoxLayout()
        step_edit_play_layout.setAlignment(Qt.AlignRight)
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
        step_text_widget.setStyleSheet("background-color: rgb(50,50,50); border-radius : 20px; color: rgb(255,255,255); font-size: 17px; padding: 10px;")
        step_text_widget.setFixedHeight(int(screen_height * 0.65))
        step_text_widget.setReadOnly(True)
        step_layout.addLayout(step_edit_play_layout)
        step_layout.addWidget(step_text_widget)

        instruction_layout = QHBoxLayout()
        instruction_widget = QWidget()
        instruction_widget.setLayout(instruction_layout)
        instruction_text_widget = QPlainTextEdit()
        instruction_text_widget.setStyleSheet("background-color: rgb(50,50,50); border-radius : 20px; color: rgb(255,255,255); font-size: 17px; padding: 10px;")
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

        main_layout.addLayout(logo_layout)
        main_layout.addLayout(step_layout)
        main_layout.addWidget(instruction_widget)

        layout.addWidget(main_widget)
        
        self.setLayout(layout)
    
    def run_query(self, input, steps_widget, OS, send_icon):
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