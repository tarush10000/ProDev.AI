from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout, QLineEdit,QComboBox, QMessageBox, QStyle, QTableWidget, QTableWidgetItem, QAbstractItemView, QPlainTextEdit, QScrollArea, QHeaderView, QDateEdit, QTimeEdit, QCompleter, QAbstractScrollArea, QSizePolicy, QFileSystemModel, QSplitter, QInputDialog, QFileDialog, QTreeView
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime, pyqtSignal, QObject, QThread , QUrl
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextCursor , QDesktopServices
import sys, os
import re
import step_generation

steps = ""
category = []
coding = []
codes = []
count = 0
max_count = 0

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

        self.currentDirectory = ''
        actual_directory_widget = QWidget()
        actual_directory_layout = QVBoxLayout()
        actual_directory_layout.setSpacing(0)
        actual_directory_layout.setContentsMargins(0, 0, 0, 0)
        actual_directory_layout.setAlignment(Qt.AlignTop)
        actual_directory_widget.setLayout(actual_directory_layout)
        actual_directory_widget.setStyleSheet("background-color: rgb(50,50,50); font-size: 17px;")
        actual_directory_widget.setFixedWidth(int(screen_width * 0.15))
        actual_directory_widget.setFixedHeight(int(screen_height * 0.9))
        actual_directory_heading_layout = QHBoxLayout()
        actual_directory_heading_layout.setContentsMargins(0, 0, 0, 0)
        actual_directory_heading_layout.setSpacing(0)
        actual_directory_heading_layout.setAlignment(Qt.AlignVCenter)
        actual_directory_heading_widget = QWidget()
        actual_directory_heading_widget.setStyleSheet("background-color: #3A46AC; padding: 10px; border: 0px; margin: 0px")
        actual_directory_heading_widget.setLayout(actual_directory_heading_layout)
        actual_directory_label = QLabel("Directory")
        actual_directory_label.setStyleSheet("color: rgb(255,255,255); font-size: 17px; font: Montserrat; border: 0px; font-weight: 500")
        actual_directory_label.setAlignment(Qt.AlignCenter)
        directory_folder_browse_image = QPixmap(resource_path('images/browse.png'))
        directory_folder_browse_image = directory_folder_browse_image.scaledToHeight(int(screen_height * 0.05))
        directory_folder_browse_button = QPushButton()
        directory_folder_browse_button.setIcon(QIcon(directory_folder_browse_image))
        directory_folder_browse_button.setCursor(Qt.PointingHandCursor)
        directory_folder_browse_button.setFlat(True)
        directory_folder_browse_button.clicked.connect(self.openFolder)
        directory_new_folder_image = QPixmap(resource_path('images/newfolder.png'))
        directory_new_folder_image = directory_new_folder_image.scaledToHeight(int(screen_height * 0.05))
        self.directory_new_folder_button = QPushButton()
        self.directory_new_folder_button.setIcon(QIcon(directory_new_folder_image))
        self.directory_new_folder_button.setCursor(Qt.PointingHandCursor)
        self.directory_new_folder_button.setFlat(True)
        self.directory_new_folder_button.clicked.connect(self.createFolder)
        directory_new_file_image = QPixmap(resource_path('images/newfile.png'))
        directory_new_file_image = directory_new_file_image.scaledToHeight(int(screen_height * 0.05))
        self.directory_new_file_button = QPushButton()
        self.directory_new_file_button.setIcon(QIcon(directory_new_file_image))
        self.directory_new_file_button.setCursor(Qt.PointingHandCursor)
        self.directory_new_file_button.setFlat(True)
        self.directory_new_file_button.clicked.connect(self.createFile)

        actual_directory_heading_layout.addWidget(actual_directory_label)
        actual_directory_heading_layout.addWidget(directory_folder_browse_button)
        actual_directory_heading_layout.addWidget(self.directory_new_folder_button)
        actual_directory_heading_layout.addWidget(self.directory_new_file_button)     
        
        self.directory_tree_view = QTreeView()
        self.directory_tree_view.setStyleSheet("")

        actual_directory_layout.addWidget(actual_directory_heading_widget)
        actual_directory_layout.addWidget(self.directory_tree_view)

        self.model = QFileSystemModel()
        self.treeView = QTreeView()
        self.directory_tree_view.setModel(self.model)
        self.treeView.setModel(self.model)
        self.treeView.doubleClicked.connect(self.onFileDoubleClicked)
        self.directory_tree_view.doubleClicked.connect(self.onFileDoubleClicked)

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
        step_play_button.clicked.connect(lambda: self.run_description(step_description_widget, step_play_button, step_prev_button, step_next_button, step_heading_label, step_text_widget))
        
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
        step_next_button.clicked.connect(lambda: step_generation.next_step(step_heading_label, code_heading_label, code_heading_widget, code_text_widget, code_description_heading_widget, code_description_text_widget))

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
        code_heading_label.setFixedWidth(int(screen_width * 0.3))
        code_copy_image = QPixmap(resource_path('images/copy.png'))
        code_copy_image = code_copy_image.scaledToHeight(int(screen_height * 0.03))
        code_copy_button = QPushButton()
        code_copy_button.setIcon(QIcon(code_copy_image))
        code_copy_button.setCursor(Qt.PointingHandCursor)
        code_copy_button.setFlat(True)
        code_copy_button.clicked.connect(lambda: self.copy_code(code_text_widget))
        code_edit_image = QPixmap(resource_path('images/edit.png'))
        code_edit_image = code_edit_image.scaledToHeight(int(screen_height * 0.03))
        code_edit_button = QPushButton()
        code_edit_button.setIcon(QIcon(code_edit_image))
        code_edit_button.setCursor(Qt.PointingHandCursor)
        code_edit_button.setFlat(True)
        code_edit_button.setVisible(True)
        code_edit_button.clicked.connect(lambda: self.edit_code(code_edit_button, code_save_button, code_text_widget, code_play_button))
        code_save_image = QPixmap(resource_path('images/save.png'))
        code_save_image = code_save_image.scaledToHeight(int(screen_height * 0.03))
        code_save_button = QPushButton()
        code_save_button.setIcon(QIcon(code_save_image))
        code_save_button.setCursor(Qt.PointingHandCursor)
        code_save_button.setFlat(True)
        code_save_button.setVisible(False)
        code_save_button.clicked.connect(lambda: self.save_code(code_edit_button, code_save_button, code_text_widget, code_play_button))
        code_play_image = QPixmap(resource_path('images/play.png'))
        code_play_image = code_play_image.scaledToHeight(int(screen_height * 0.03))
        code_play_button = QPushButton()
        code_play_button.setIcon(QIcon(code_play_image))
        code_play_button.setCursor(Qt.PointingHandCursor)
        code_play_button.setFlat(True)
        code_play_button.setVisible(True)
        code_play_button.clicked.connect(lambda: step_generation.run_code(code_text_widget, code_play_button))
        
        code_heading_layout.addWidget(code_heading_label)
        code_heading_layout.addWidget(code_copy_button)
        code_heading_layout.addWidget(code_edit_button)
        code_heading_layout.addWidget(code_save_button)
        code_heading_layout.addWidget(code_play_button)

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
        code_description_heading_label.setFixedWidth(int(screen_width * 0.3))
        code_description_heading_label.setStyleSheet("color: rgb(255,255,255); font-size: 17px; font: Montserrat; border: 0px; font-weight: 500")
        code_description_add_image = QPixmap(resource_path('images/add.png'))
        code_description_add_image = code_description_add_image.scaledToHeight(int(screen_height * 0.03))
        code_description_add_button = QPushButton()
        code_description_add_button.setIcon(QIcon(code_description_add_image))
        code_description_add_button.setCursor(Qt.PointingHandCursor)
        code_description_add_button.setFlat(True)
        code_description_add_button.clicked.connect(lambda: step_generation.add_description(code_text_widget, code_description_text_widget))
        code_description_text_layout = QVBoxLayout()
        code_description_text_widget = QPlainTextEdit()
        code_description_text_widget.setStyleSheet("color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 20px; font: Montserrat; border-top-left-radius: 0px; border-top-right-radius: 0px; border: 0px;")
        code_description_text_widget.setLayout(code_description_text_layout)
        code_description_text_widget.setReadOnly(True)

        code_description_heading_layout.addWidget(code_description_heading_label)
        code_description_heading_layout.addWidget(code_description_add_button)

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
        
        check = step_generation.check_input(input)
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
            try:
                steps_generated = step_generation.run_query_1()
            except:
                steps_generated = "Error in step generation"
            self.worker_thread.started.connect(self.worker.run_query_1)
            self.worker_thread.start()
        else:
            self.show_error(check)
            return


    def append_text(self, text, steps_widget, OS):
        steps_widget.moveCursor(QTextCursor.End)
        steps_widget.insertPlainText(text)

    def worker_finished(self):
        self.worker_thread.quit()
        self.worker_thread.wait()

    def edit_steps(self, step_edit_button, step_save_button, step_text_widget, step_edit_play_layout, step_play_button):
        global steps
        step_text_widget.setPlainText(steps)
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
            
    
    def run_description(self, steps_widget, send_icon, step_prev_button, step_next_button, step_heading_label, step_text_widget):        
        global result2
        global steps
        result2 = self.modify_text(steps)
        step_text_widget.setPlainText(result2)
        step_prev_button.setVisible(True)
        step_next_button.setVisible(True)
        step_heading_label.setVisible(True)
        print(">>>>>>>>>>>>running description function <<<<<<<<<<<")
        try:
            steps = eval(steps)
        except SyntaxError:
            # If a SyntaxError occurs, skip the first character and try again.
            try:
                first_occurrence = steps.find('[')
                second_occurrence = steps.find('[', first_occurrence + 1)
                steps = eval(steps[second_occurrence:])
                print(f"Evaluated steps type after SyntaxError handling: {type(steps)}")
            except Exception as e:
                # If another error occurs, handle it or return a message.
                print(f"Error after skipping first character: {e}")
                return

        # Ensure steps is a list; if not, this could be the source of the AttributeError
        if not isinstance(steps, list):
            print("Error: 'steps' is not a list.")
            return

        global category
        global coding
        global max_count

        # Assuming category and coding are intended to be lists
        if 'category' not in globals():
            category = []
        if 'coding' not in globals():
            coding = []

        for item in steps:
            # Check if the item is a dictionary before attempting to use .get()
            if isinstance(item, dict):
                category.append(item.get('category'))
                coding.append(item.get('step'))
            else:
                print(f"Item in steps is not a dictionary: {item}")

        print(category)
        print(coding)
        max_count = len(category)

            

    def copy_code(self, code_text_widget):
        code_text_widget.selectAll()
        code_text_widget.copy()

    def edit_code(self, code_edit_button, code_save_button, code_text_widget, code_play_button):
        code_edit_button.setVisible(False)
        code_save_button.setVisible(True)
        code_text_widget.setReadOnly(False)  
        code_play_button.setVisible(False)

    def save_code(self, code_edit_button, code_save_button, code_text_widget, code_play_button):
        code_edit_button.setVisible(True)
        code_save_button.setVisible(False)
        code_text_widget.setReadOnly(True)  
        code_play_button.setVisible(True)
        # global codes
        # codes[count] = code_text_widget.toPlainText()

    

    def openFolder(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if directory:
            self.currentDirectory = directory
            self.model.setRootPath(directory)
            self.treeView.setRootIndex(self.model.index(directory))
            self.directory_tree_view.setRootIndex(self.model.index(directory))
            self.directory_new_file_button.setEnabled(True)
            self.directory_new_folder_button.setEnabled(True)

    def createFile(self):
        if self.currentDirectory:
            name, _ = QFileDialog.getSaveFileName(self, "Create File", self.currentDirectory)
            if name:
                with open(name, 'w') as file:
                    pass
                self.model.setRootPath(self.currentDirectory)  # Refresh view
        else:
            self.show_error("Please select a folder first.")

    def createFolder(self):
        if self.currentDirectory:
            folderName, ok = QInputDialog.getText(self, "Create Folder", "Folder name:")
            if ok and folderName:
                fullPath = os.path.join(self.currentDirectory, folderName)
                try:
                    os.makedirs(fullPath, exist_ok=True)
                    self.model.setRootPath(self.currentDirectory)  # Refresh view
                    self.treeView.setRootIndex(self.model.index(self.currentDirectory))
                except Exception as e:
                    self.show_error(str(e))
        else:
            self.show_error("Please select a folder first.")
    def onFileDoubleClicked(self, index):
        print("Double clicked")
        # Get the file path from the model
        filePath = self.model.filePath(index)
        if os.path.isfile(filePath):
            # Open the file with the default application
            QDesktopServices.openUrl(QUrl.fromLocalFile(filePath))
    def prev_step(self, step_heading_label, code_heading_label, code_heading_widget, code_text_widget, code_description_heading_widget, code_description_text_widget):
        global count
        global codes
        if count > 1:
            count -= 1
            step_heading_label.setText("Step "+ str(count))
            code_text_widget.setPlainText(codes[count-1])
            code_description_text_widget.setPlainText(coding[count-1])
            if category[count-1].lower() == "shell":
                code_heading_label.setText("Shell Command")
                code_heading_widget.setStyleSheet("background-color: #EB5E55; padding: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border: 0px; margin: 0px")
                code_description_heading_widget.setStyleSheet("background-color: #EB5E55; padding: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border: 0px; margin: 0px")
            else:
                code_heading_label.setText("Code")
                code_heading_widget.setStyleSheet("background-color: #3A46AC; padding: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border: 0px; margin: 0px")
                code_description_heading_widget.setStyleSheet("background-color: #3A46AC; padding: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border: 0px; margin: 0px")

    
    def modify_text(self, input_text):
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


    def detect_and_remove_markdown(self, code_text):
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

if __name__ == '__main__':

    app = QApplication([])
    PDA_ui = PDA()
    PDA_ui.show()
    app.exec_()