from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout, QLineEdit, 
                            QComboBox, QMessageBox, QStyle, QTableWidget, QTableWidgetItem, QAbstractItemView, 
                            QPlainTextEdit, QScrollArea, QHeaderView, QDateEdit, QTimeEdit, QCompleter, 
                            QAbstractScrollArea, QSizePolicy, QFileSystemModel, QSplitter, QInputDialog,QToolBox, QGroupBox, QTextEdit, 
                            QFileDialog, QFrame, QTreeView, QStackedWidget, QRadioButton, QButtonGroup , QDialog)
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime, pyqtSignal, QObject, QThread, QUrl
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextCursor, QDesktopServices
import sys, os
from demoHistory import demoData
from code_generation import create_folder , generate_file_structure , generate_strategies , generate_deployment , generate_read_me
#import step_generation

steps = ""
category = []
coding = []
codes = []
count = 0
max_count = 0
query = ""
technology = ""
folder_path = ""
folder_structure = ""

# Theme colors
primary_color = "#0c0c0c"  # Dark mode background
secondary_color = "#ffffff"  # Dark mode text

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProDev.AI")
        self.setWindowIcon(QIcon(resource_path("")))
        self.app = app
        self.theme = "dark"
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setWindowTitle('ProDev.AI')
        screen_height = self.app.desktop().screenGeometry().height()
        screen_width = self.app.desktop().screenGeometry().width()
        self.setFixedSize(screen_width, screen_height)
        self.update_theme()
        self.showMaximized()

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignVCenter)
        layout.setSpacing(10)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignVCenter)
        main_layout.setSpacing(10)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        # header
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.setSpacing(10)
        header_widget = QWidget()
        header_widget.setLayout(header_layout)

        logo = QLabel()
        logo_image = QPixmap(resource_path('images/logo.png'))
        logo_image = logo_image.scaledToWidth(int(screen_width * 0.14))
        logo.setPixmap(logo_image)
        logo.setAlignment(Qt.AlignCenter)

        navbar_container = QFrame()
        navbar_container.setFixedWidth(int(screen_width * 0.8))

        navbar_layout = QHBoxLayout(navbar_container)
        navbar_layout.setAlignment(Qt.AlignCenter)
        navbar_layout.setSpacing(160)

        # Navbar items
        guide_label = QLabel("Guide")
        history_label = QLabel("History")
        settings_label = QLabel("Settings")

        # Set focus policy to labels
        guide_label.setFocusPolicy(Qt.StrongFocus)
        history_label.setFocusPolicy(Qt.StrongFocus)
        settings_label.setFocusPolicy(Qt.StrongFocus)

        # Style for navbar items
        nav_item_style = f"""
        QLabel {{
            color: #888888;
            font-size: 18px;
        }}
        QLabel:hover {{
            color: {secondary_color};
        }}
        QLabel:focus {{
            color: {secondary_color};
            text-decoration: underline;
        }}
        QLabel:pressed {{
            text-decoration: underline;
        }}
        """

        guide_label.setStyleSheet(nav_item_style)
        history_label.setStyleSheet(nav_item_style)
        settings_label.setStyleSheet(nav_item_style)

        navbar_layout.addWidget(guide_label)
        navbar_layout.addWidget(history_label)
        navbar_layout.addWidget(settings_label)

        header_layout.addWidget(logo)
        header_layout.addWidget(navbar_container)

        main_layout.addWidget(header_widget)
        
        # Stacked Widget for different pages
        self.stacked_widget = QStackedWidget()
        
        # Guide Page
        self.guide_widget = self.create_guide_widget(screen_height, screen_width)
        self.stacked_widget.addWidget(self.guide_widget)

        # History Page
        self.history_widget = self.create_history_widget()
        self.stacked_widget.addWidget(self.history_widget)

        # Settings Page
        self.settings_widget = self.create_settings_widget()
        self.stacked_widget.addWidget(self.settings_widget)

        main_layout.addWidget(self.stacked_widget)

        layout.addWidget(main_widget)
        self.setLayout(layout)

        # Connect click events
        guide_label.mousePressEvent = lambda event: self.stacked_widget.setCurrentIndex(0)
        history_label.mousePressEvent = lambda event: self.stacked_widget.setCurrentIndex(1)
        settings_label.mousePressEvent = lambda event: self.stacked_widget.setCurrentIndex(2)


    def create_guide_widget(self, screen_height, screen_width):
        guide_widget = QWidget()
        guide_layout = QVBoxLayout()
        
        guide_widget = QWidget()
        guide_layout = QVBoxLayout(guide_widget)

        step_area_layout = QHBoxLayout()
        step_area_layout.setSpacing(20)
        step_area_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        step_area_widget = QWidget()
        step_area_widget.setLayout(step_area_layout)
        step_area_widget.setStyleSheet("padding: 10px;")
        step_area_widget.setFixedHeight(int(screen_height * 0.75))
        step_area_widget.setFixedWidth(int(screen_width * 0.94))

        # step_layout = QVBoxLayout()
        # step_layout.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        # step_widget = QWidget()
        # step_widget.setLayout(step_layout)
        # step_widget.setStyleSheet("padding: 10px;  border: 1px solid rgb(255,255,255); border-radius: 20px")
        # step_edit_play_layout = QHBoxLayout()
        # step_edit_play_layout.setAlignment(Qt.AlignRight)
        # step_edit_play_widget = QWidget()
        # step_edit_play_widget.setLayout(step_edit_play_layout)
        # step_edit_play_widget.setStyleSheet("padding: 10px; border: 0px;")
        # step_edit_button = QPushButton()
        # step_edit_image = QPixmap(resource_path('images/edit.png'))
        # step_edit_image = step_edit_image.scaledToHeight(int(screen_height * 0.05))
        # step_edit_button.setIcon(QIcon(step_edit_image))
        # step_edit_button.setCursor(Qt.PointingHandCursor)
        # step_edit_button.setFlat(True)
        # step_edit_button.clicked.connect(lambda: self.edit_steps(step_edit_button, step_save_button, step_text_widget, step_edit_play_layout, step_play_button))
        # step_save_button = QPushButton()
        # step_save_image = QPixmap(resource_path('images/save.png'))
        # step_save_image = step_save_image.scaledToHeight(int(screen_height * 0.05))
        # step_save_button.setIcon(QIcon(step_save_image))
        # step_save_button.setCursor(Qt.PointingHandCursor)
        # step_save_button.setFlat(True)
        # step_save_button.setVisible(False)
        # step_save_button.clicked.connect(lambda: self.save_edit_steps(step_edit_button, step_save_button, step_text_widget, step_edit_play_layout, step_play_button))
        # step_play_button = QPushButton()
        # step_play_image = QPixmap(resource_path('images/play.png'))
        # step_play_image = step_play_image.scaledToHeight(int(screen_height * 0.05))
        # step_play_button.setIcon(QIcon(step_play_image))
        # step_play_button.setCursor(Qt.PointingHandCursor)
        # step_play_button.setFlat(True)
        # step_play_button.clicked.connect(lambda: self.run_description(step_description_widget, step_play_button, step_prev_button, step_next_button, step_heading_label, step_text_widget))
        
        # step_edit_play_layout.addWidget(step_edit_button)
        # step_edit_play_layout.addWidget(step_save_button)
        # step_edit_play_layout.addWidget(step_play_button)

        # step_text_widget = QPlainTextEdit()
        # step_text_widget.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 23px")
        # step_text_widget.setFixedWidth(int(screen_width * 0.5))
        # step_text_widget.setReadOnly(True)
        # step_layout.addWidget(step_edit_play_widget)
        # step_layout.addWidget(step_text_widget)

        step_layout = QVBoxLayout()
        step_layout.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        step_widget = QWidget()
        step_widget.setLayout(step_layout)
        step_widget.setStyleSheet("padding: 10px;  border: 1px solid rgb(255,255,255); border-radius: 20px")

        step_toolbox_layout = QVBoxLayout()
        step_toolbox_layout.setAlignment(Qt.AlignTop)
        step_toolbox_layout.setContentsMargins(0, 0, 0, 0)
        step_toolbox_widget = QWidget()
        step_toolbox_widget.setLayout(step_toolbox_layout)
        step_toolbox_widget.setStyleSheet("padding: 10px; border: 1px solid rgb(255,255,255); border-radius: 20px")

        step_toolbox = QToolBox()
        step_toolbox.setStyleSheet("""
                                        QToolBox::tab {
                                            padding: 30px;
                                            background: rgb(50,50,50);
                                            color: white;
                                            border: 0px;
                                            font-size: 20px;
                                            border-radius: 20px;
                                        }
                                    """)

        # Step 1
        step_group1 = QGroupBox()
        step_layout1 = QVBoxLayout()

        step_text_widget1 = QTextEdit()
        step_text_widget1.setReadOnly(True)
        # step_text_widget1.setPlainText("In this project, we will be using the following technologies:\n\n1. Python\n2. Django\n3. HTML\n4. CSS\n5. JavaScript\n6. Bootstrap\n7. SQLite\n\nLet's get started!")
        step_text_widget1.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 5px;")

        button_layout1 = QHBoxLayout()
        # play_button1 = QPushButton("Play")
        edit_button1 = QPushButton("Edit")

        # play_button1.clicked.connect(lambda checked: self.run_description(1))
        edit_button1.clicked.connect(lambda checked: self.create_tech_popup(step_text_widget1))

        # button_layout1.addWidget(play_button1)
        button_layout1.addWidget(edit_button1)
        
        step_layout1.addWidget(step_text_widget1)
        step_layout1.addLayout(button_layout1)

        step_group1.setLayout(step_layout1)
        step_toolbox.addItem(step_group1, "Step 1: Technology to be used")

        # Step 2
        step_group2 = QGroupBox()
        step_layout2 = QVBoxLayout()

        step_text_widget2 = QTextEdit()
        step_text_widget2.setReadOnly(True)
        step_text_widget2.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 5px;")

        button_layout2 = QHBoxLayout()
        # play_button2 = QPushButton("Play")
        edit_button2 = QPushButton("select")
        # play_button2.clicked.connect(lambda checked: self.run_description(2))
        edit_button2.clicked.connect(lambda : self.save_folder_path(step_text_widget2))

        # button_layout2.addWidget(play_button2)
        button_layout2.addWidget(edit_button2)

        step_layout2.addWidget(step_text_widget2)
        step_layout2.addLayout(button_layout2)

        step_group2.setLayout(step_layout2)
        step_toolbox.addItem(step_group2, "Step 2: Choose Location of project")

        # Step 3
        step_group3 = QGroupBox()
        step_layout3 = QVBoxLayout()

        step_text_widget3 = QTextEdit()
        step_text_widget3.setReadOnly(True)
        step_text_widget3.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 5px;")

        button_layout3 = QHBoxLayout()
        # play_button3 = QPushButton("Play")
        edit_button3 = QPushButton("Generate")

        # play_button3.clicked.connect(lambda checked: self.run_description(3))
        edit_button3.clicked.connect(lambda : self.save_file_structure(step_text_widget3))

        # button_layout3.addWidget(play_button3)
        button_layout3.addWidget(edit_button3)

        step_layout3.addWidget(step_text_widget3)
        step_layout3.addLayout(button_layout3)

        step_group3.setLayout(step_layout3)
        step_toolbox.addItem(step_group3, "Step 3: Create file / folder structure")

        # Step 4
        step_group4 = QGroupBox()
        step_layout4 = QVBoxLayout()

        step_text_widget4 = QTextEdit()
        step_text_widget4.setReadOnly(True)
        step_text_widget4.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 5px;")

        button_layout4 = QHBoxLayout()
        play_button4 = QPushButton("Play")
        edit_button4 = QPushButton("Edit")

        play_button4.clicked.connect(lambda checked: self.run_description(4))
        edit_button4.clicked.connect(lambda checked: self.edit_step(4))

        button_layout4.addWidget(play_button4)
        button_layout4.addWidget(edit_button4)

        step_layout4.addWidget(step_text_widget4)
        step_layout4.addLayout(button_layout4)

        step_group4.setLayout(step_layout4)
        step_toolbox.addItem(step_group4, "Step 4: Implementation")

        # Step 5
        step_group5 = QGroupBox()
        step_layout5 = QVBoxLayout()

        step_text_widget5 = QTextEdit()
        step_text_widget5.setReadOnly(True)
        step_text_widget5.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 5px;")

        button_layout5 = QHBoxLayout()
        # play_button5 = QPushButton("Play")
        edit_button5 = QPushButton("Generate")

        # play_button5.clicked.connect(lambda checked: self.run_description(5))
        edit_button5.clicked.connect(lambda : self.save_tests(step_text_widget5) )

        # button_layout5.addWidget(play_button5)
        button_layout5.addWidget(edit_button5)

        step_layout5.addWidget(step_text_widget5)
        step_layout5.addLayout(button_layout5)

        step_group5.setLayout(step_layout5)
        step_toolbox.addItem(step_group5, "Step 5: Testing")

        # Step 6
        step_group6 = QGroupBox()
        step_layout6 = QVBoxLayout()

        step_text_widget6 = QTextEdit()
        step_text_widget6.setReadOnly(True)
        step_text_widget6.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 5px;")

        button_layout6 = QHBoxLayout()
        # play_button6 = QPushButton("Play")
        edit_button6 = QPushButton("Generate")

        # play_button6.clicked.connect(lambda checked: self.run_description(6))
        edit_button6.clicked.connect(lambda : self.save_deployment(step_text_widget6))

        # button_layout6.addWidget(play_button6)
        button_layout6.addWidget(edit_button6)

        step_layout6.addWidget(step_text_widget6)
        step_layout6.addLayout(button_layout6)

        step_group6.setLayout(step_layout6)
        step_toolbox.addItem(step_group6, "Step 6: Deployment")

        # Step 7
        step_group7 = QGroupBox()
        step_layout7 = QVBoxLayout()

        step_text_widget7 = QTextEdit()
        step_text_widget7.setReadOnly(True)
        step_text_widget7.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 0px; border-radius: 5px;")

        button_layout7 = QHBoxLayout()
        # play_button7 = QPushButton("Play")
        edit_button7 = QPushButton("Generate")

        # play_button7.clicked.connect(lambda checked: self.run_description(7))
        edit_button7.clicked.connect(lambda : self.save_docs(step_text_widget7))

        # button_layout7.addWidget(play_button7)
        button_layout7.addWidget(edit_button7)

        step_layout7.addWidget(step_text_widget7)
        step_layout7.addLayout(button_layout7)

        step_group7.setLayout(step_layout7)
        step_toolbox.addItem(step_group7, "Step 7: Documentation")

        step_toolbox_layout.addWidget(step_toolbox)
        step_area_layout.addWidget(step_toolbox_widget)
        
        
        self.step_text_widget1 = step_text_widget1
        self.step_text_widget2 = step_text_widget2
        self.step_text_widget3 = step_text_widget3
        self.step_text_widget4 = step_text_widget4
        self.step_text_widget5 = step_text_widget5
        self.step_text_widget6 = step_text_widget6
        self.step_text_widget7 = step_text_widget7


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

        # step_area_layout.addWidget(step_widget)
        step_area_layout.addWidget(step_description_widget)

        instruction_layout = QHBoxLayout()
        instruction_widget = QWidget()
        instruction_widget.setLayout(instruction_layout)
        instruction_text_widget = QPlainTextEdit()
        instruction_text_widget.setStyleSheet("border-radius : 20px; color: rgb(255,255,255); font-size: 17px; padding: 10px; border: 2px solid rgb(255,255,255);")
        instruction_text_widget.setFixedHeight(int(screen_height * 0.07))
        # instruction_text_widget.setFixedWidth(int(screen_width * 0.9))
        instruction_send_button = QPushButton()
        instruction_send_image = QPixmap(resource_path('images/play.png'))
        instruction_send_image = instruction_send_image.scaledToHeight(int(screen_height * 0.05))
        instruction_send_button.setIcon(QIcon(instruction_send_image))
        instruction_send_button.setCursor(Qt.PointingHandCursor)
        instruction_send_button.setFlat(True)
        OS = "Windows"
        # instruction_send_button.clicked.connect(lambda: print("Instruction sent" , instruction_text_widget.toPlainText()))
        instruction_send_button.clicked.connect(lambda: self.querySubmit(instruction_text_widget.toPlainText() , step_text_widget1 , step_text_widget2 ,step_text_widget3,step_text_widget5))

        instruction_layout.addWidget(instruction_text_widget)
        instruction_layout.addWidget(instruction_send_button)

        guide_layout.addWidget(step_area_widget)
        guide_layout.addWidget(instruction_widget)
        
        guide_widget.setLayout(guide_layout)
        return guide_widget

    def querySubmit(self , queryUser , step_text_widget1 ,step_text_widget2 ,step_text_widget3 , step_text_widget5):
        global query
        query = queryUser
        print(query)
        self.create_tech_popup( step_text_widget1 )
        folder_path = create_folder(self)
        step_text_widget2.setPlainText(folder_path)
        # global technology
        # print(technology)
        # print(query)
        
        # folder_structure = generate_file_structure(self , query , technology)
        # step_text_widget3.setPlainText(folder_structure)
        # testingStrategy = generate_strategies(self , query , technology)
        # print(testingStrategy)
        # step_text_widget5.append(testingStrategy)
        
    def save_folder_path(self ,  step_text_widget2):
        global folder_path
        folder_path = create_folder(self)
        step_text_widget2.setPlainText(folder_path)
        
    def save_file_structure(self , step_text_widget3):
        global folder_structure
        folder_structure = generate_file_structure(self , query , technology)
        step_text_widget3.setPlainText(folder_structure)
    def save_tests(self , step_text_widget5):
        testingStrategy = generate_strategies(self , query , technology)
        print(testingStrategy)
        step_text_widget5.append(testingStrategy)
    
    def save_deployment(self , step_text_widget6):
        deployment = generate_deployment(self , query , technology)
        print(deployment)
        step_text_widget6.append(deployment)
    def save_docs(self , step_text_widget7):
        read_me = generate_read_me(self , query , technology)
        print(read_me)
        step_text_widget7.append(read_me)
        
    def create_tech_popup(self , step_text_widget1):
        tech_popup = QDialog()
        tech_popup.setWindowTitle("tech_Popup")
        tech_popup_layout = QVBoxLayout()
        tech_popup_text = QLabel("What Technology do you want to use?")
        tech_popup_input = QLineEdit()
        tech_popup_button = QPushButton("Submit")
        tech_popup_button.clicked.connect(lambda: self.submit_tech(tech_popup_input.text() , tech_popup , step_text_widget1))
        tech_popup_layout.addWidget(tech_popup_text)
        tech_popup_layout.addWidget(tech_popup_input)
        tech_popup_layout.addWidget(tech_popup_button)
        tech_popup.setLayout(tech_popup_layout)
        tech_popup.exec_()

    def submit_tech(self, tech , tech_popup ,step_text_widget1):
        # Do something with the submitted tech
        print("Submitted tech:", tech)
        tech_popup.close()
        global technology
        technology = tech
        step_text_widget1.setPlainText(tech)
        
    
    
    def create_history_widget(self):
        history_widget = QWidget()
        history_layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search history...")
        search_button = QPushButton(QIcon(resource_path('images/search.png')), "")
        search_layout.addWidget(search_bar)
        search_layout.addWidget(search_button)

        # History content (placeholder)
        history_content = QLabel("History Content")
        history_content.setAlignment(Qt.AlignCenter)
        history_layout.addLayout(search_layout)
        history_scroll_area = QScrollArea()
        history_scroll_area.setWidgetResizable(True)
        history_scroll_widget = QWidget()
        history_scroll_layout = QVBoxLayout(history_scroll_widget)
        history_scroll_area.setWidget(history_scroll_widget)
        
        for i in demoData :
            history_item = QPushButton(i["title"])
            history_item.setStyleSheet("background-color: grey; margin: 5px; padding: 10px; border: 0; color: white; font-size: 20px; text-align: left; border-radius: 10px;")
            history_item.clicked.connect(lambda _, item=i: self.load_history_item(item))
            
            history_scroll_layout.addWidget(history_item)
            
        history_layout.addWidget(history_scroll_area)

        # history_layout.addWidget(history_content)

        history_widget.setLayout(history_layout)
        return history_widget
    
    def load_history_item(self, item):
        # Switch to guide window
        self.stacked_widget.setCurrentIndex(0)

        # Load content into guide window
        self.load_content_to_guide(item['content'])

    def load_content_to_guide(self, content):
        # Update the guide window with the content
        self.step_text_widget1.setPlainText(content.get('project_type', ''))
        self.step_text_widget2.setPlainText(content.get('software_description', ''))
        self.step_text_widget3.setPlainText(content.get('response1', ''))
        self.step_text_widget4.setPlainText(content.get('commands', ''))
        self.step_text_widget5.setPlainText(content.get('response2', ''))
        self.step_text_widget6.setPlainText(content.get('response3', ''))
        self.step_text_widget7.setPlainText(content.get('response4', ''))

    def create_settings_widget(self):
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()

        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.light_radio = QRadioButton("Light")
        self.dark_radio = QRadioButton("Dark")
        self.dark_radio.setChecked(True)
        theme_group = QButtonGroup()
        theme_group.addButton(self.light_radio)
        theme_group.addButton(self.dark_radio)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.light_radio)
        theme_layout.addWidget(self.dark_radio)
        
        # Gemini API setting
        api_layout = QHBoxLayout()
        api_label = QLabel("Gemini API Key:")
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Enter your Gemini API key")
        api_save_button = QPushButton("Save")
        api_save_button.clicked.connect(self.save_api_key)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        api_layout.addWidget(api_save_button)

        # Add layouts to main settings layout
        settings_layout.addLayout(theme_layout)
        settings_layout.addLayout(api_layout)
        settings_layout.addStretch()

        # Connect theme change
        self.light_radio.toggled.connect(self.change_theme)
        self.dark_radio.toggled.connect(self.change_theme)

        settings_widget.setLayout(settings_layout)
        return settings_widget

    def change_theme(self):
        global primary_color, secondary_color
        if self.light_radio.isChecked():
            primary_color = "#ffffff"
            secondary_color = "#000000"
        else:
            primary_color = "#0c0c0c"
            secondary_color = "#ffffff"
        self.update_theme()

    def update_theme(self):
        self.setStyleSheet(f"background-color: {primary_color}; color: {secondary_color};")
        # Update other widgets' styles as needed

    def save_api_key(self):
        api_key = self.api_input.text()
        if api_key:
            os.environ['GEMINI_API'] = api_key
            QMessageBox.information(self, "Success", "Gemini API key saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid API key.")

if __name__ == '__main__':
    app = QApplication([])
    PDA_ui = UI()
    PDA_ui.show()
    app.exec_()