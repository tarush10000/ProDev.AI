from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout, QLineEdit, QSlider, QComboBox,
                            QMessageBox, QPlainTextEdit, QScrollArea, QToolBox, QGroupBox, QTextEdit, QFrame, QStackedWidget, 
                            QRadioButton, QButtonGroup , QDialog, QListWidgetItem, QListWidget, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
import sys, os, re
from demoHistory import demoData
from code_generation import create_folder , generate_file_structure , generate_strategies , generate_deployment , generate_read_me , save_read_me
import google.generativeai as genai
from edge_tts import Communicate
import tempfile
import pygame
import asyncio
import emoji

query = ""
technology = ""
folder_path = ""
folder_structure = ""
implementation = ""
testing = ""
deployment = ""
documentation = ""
documentationMd = ""

# Theme colors
primary_color = "#0c0c0c"  # Dark mode background
secondary_color = "#ffffff"  # Dark mode text

class TTSThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, text, voice="en-US-EmmaMultilingualNeural", speed="+0%"):
        QThread.__init__(self)
        self.text = self.remove_emojis(text)
        self.voice = voice
        self.speed = speed
        self.is_playing = False

    def remove_emojis(self, text):
        # Remove emojis
        text = emoji.replace_emoji(text, replace='')
        # Remove any leftover unicode characters that might be emojis
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    async def tts_to_file(self):
        communicate = Communicate(self.text, self.voice, rate=self.speed)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            self.temp_filename = temp_file.name
        await communicate.save(self.temp_filename)

    def run(self):
        try:
            asyncio.run(self.tts_to_file())

            pygame.mixer.init()
            try:
                pygame.mixer.music.load(self.temp_filename)
            except pygame.error as e:
                self.error.emit(f"Failed to load audio: {str(e)}")
                return

            pygame.mixer.music.play()
            if not pygame.mixer.music.get_busy():
                self.error.emit("Music isn't playing")
                return

            self.is_playing = True

            while pygame.mixer.music.get_busy() and self.is_playing:
                pygame.time.Clock().tick(10)

        except Exception as e:
            self.error.emit(f"Error in TTS: {str(e)}")
        finally:
            pygame.mixer.quit()
            if os.path.exists(self.temp_filename):
                os.unlink(self.temp_filename)
            self.finished.emit()

    def stop(self):
        self.is_playing = False
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.wait()


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
        self.initGemini()
        self.tts_enabled = False
        self.tts_thread = None
        self.tts_speed = "+0%"
        self.tts_voice = "en-US-EmmaMultilingualNeural"

    def update_tts_speed(self, speed):
        speed_str = f"+{speed}%" if speed >= 0 else f"{speed}%"
        self.tts_speed = speed_str
        print(f"TTS speed updated to: {speed_str}")

    def update_tts_voice(self, voice):
        self.tts_voice = voice
        print(f"TTS voice updated to: {voice}")


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
        edit_button7 = QPushButton("Generate")
        play_button7 = QPushButton("Save ReadMe")
        global folder_path
        play_button7.clicked.connect(lambda: save_read_me(self, folder_path, documentationMd))
        edit_button7.clicked.connect(lambda : self.save_docs(step_text_widget7))

        button_layout7.addWidget(play_button7)
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

        step_heading_label = QLabel("Ask Gemma")
        step_heading_label.setVisible(True)
        step_heading_label.setStyleSheet("color: rgb(255,255,255); font-size: 17px; font: Montserrat; border: 0px; font-weight: 500")
        
        step_description_heading_layout.addWidget(step_heading_label)
        
        step_description_content_layout = QVBoxLayout()
        step_description_content_layout.setSpacing(30)
        step_description_content_widget = QWidget()
        step_description_content_widget.setLayout(step_description_content_layout)
        step_description_content_widget.setStyleSheet("background-color: rgb(50,50,50);padding: 10px; border: 0px")
        step_description_content_layout.setAlignment(Qt.AlignVCenter)
        step_description_content_layout.setContentsMargins(15, 15, 15, 15)

        # Add chatbot components
        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet("""
            QListWidget {
                background-color: #121B22;
                border: none;
            }
            QListWidget::item {
                border: none;
                margin: 5px;
            }
        """)
        step_description_content_layout.addWidget(self.chat_list)

        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setStyleSheet("""
            background-color: #2A2F32;
            color: white;
            border: 1px solid #3A3F41;
            border-radius: 20px;
            padding: 10px 15px;
            font-size: 14px;
        """)
        self.chat_input.setPlaceholderText("Type a message...")
        self.chat_input.returnPressed.connect(self.sendMessage)
        self.chat_send_button = QPushButton('Send')
        self.chat_send_button.clicked.connect(self.sendMessage)
        self.chat_send_button.setStyleSheet("background-color: #00A884; color: white;")
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.chat_send_button)

        step_description_content_layout.addLayout(chat_input_layout)

        # Add TTS toggle
        tts_control_layout = QHBoxLayout()
        tts_control_layout.setAlignment(Qt.AlignCenter)
        tts_control_layout.setContentsMargins(0, 0, 0, 0)
        tts_control_widget = QWidget()
        tts_control_widget.setLayout(tts_control_layout)

        self.tts_toggle = QCheckBox('Enable TTS')
        self.tts_toggle.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #555;
                background: #2A2F32;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #00A884;
                background: #00A884;
            }
        """)
        self.tts_toggle.stateChanged.connect(self.toggleTTS)
        tts_control_layout.addWidget(self.tts_toggle)

        self.stop_tts_button = QPushButton('Stop TTS')
        self.stop_tts_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2F32;
                color: white;
                border: 1px solid #3A3F41;
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3A3F41;
            }
            QPushButton:pressed {
                background-color: #1E2326;
            }
            QPushButton:disabled {
                background-color: #1E2326;
                color: #555;
            }
        """)
        self.stop_tts_button.clicked.connect(self.stopTTS)
        self.stop_tts_button.setEnabled(False)
        tts_control_layout.addWidget(self.stop_tts_button)

        step_description_layout.addWidget(step_description_heading_widget)
        step_description_layout.addWidget(step_description_content_widget)
        step_description_layout.addWidget(tts_control_widget)

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
        global folder_path
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
        print("folderpath function" , folder_path)
        
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
        global folder_path
        print(folder_path)
    def save_docs(self , step_text_widget7):
        read_me , read_meMD = generate_read_me(self , query , technology)
        global documentationMd
        documentationMd = read_meMD
        print(read_me)
        global documentation
        documentation = read_me
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
        
    def initGemini(self):
        genai.configure(api_key=os.getenv("Gemini_API"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.chat = self.model.start_chat(history=[])
        global query, technology, folder_path, folder_structure
        # Collect context from global variables
        initial_context = f"Software Development: {query}\n Technology: {technology}\n Folder Path: {folder_path}\n Folder Structure: {folder_structure}"
        initial_instructions = f"""You are Gemma, the ProDev.AI assistant. You're a friendly, witty, and knowledgeable software development expert. Your task is to help people learn software development and solve their coding queries with a touch of humor and enthusiasm. Stay on topic, but don't be afraid to throw in a pun or a joke now and then. If a question isn't related to software development or coding, gently steer the conversation back on track with a clever quip. Remember, you're not just sharing knowledge - you're making learning fun!\n\nContext:\n{initial_context}"""
        
        self.chat.send_message(initial_instructions)
        self.sendInitialBotMessage()

    def sendMessage(self):
        user_input = self.chat_input.text()
        if user_input.strip() == "":
            return

        self.addMessage('User', user_input)
        self.chat_input.clear()

        self.addMessage('Bot', '...')
        QApplication.processEvents()

        try:
            response = self.getResponseFromAPI(user_input)
            self.chat_list.takeItem(self.chat_list.count() - 1)

            if "Content Safety Violation" in response:
                self.addMessage('Bot', response, is_warning=True)
            else:
                self.addMessage('Bot', response)

            if self.tts_enabled:
                self.speakText(response)
        except Exception as e:
            self.chat_list.takeItem(self.chat_list.count() - 1)
            error_message = f"An error occurred: {str(e)}. Please try again later or check your internet connection."
            self.addMessage('Bot', error_message)

    def addMessage(self, sender, message, is_warning=False):
        item = QListWidgetItem()
        widget = QLabel(message)
        widget.setWordWrap(True)

        if is_warning:
            bg_color = '#FF4136'  # Red background for warnings
        else:
            bg_color = '#005C4B' if sender == 'User' else '#1E1E1E'

        widget.setStyleSheet(f"""
            background-color: {bg_color};
            color: white;
            border-radius: 10px;
            padding: 15px;
            max-width: 700px;
        """)
        widget.adjustSize()
        size = widget.sizeHint()
        size.setHeight(size.height() + 20)  # Add extra height to ensure text is not cut off
        item.setSizeHint(size)

        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, widget)

        if sender == 'User':
            item.setTextAlignment(Qt.AlignRight)
            widget.setStyleSheet(widget.styleSheet() + "margin-left: 180px;")
        else:
            item.setTextAlignment(Qt.AlignLeft)
            widget.setStyleSheet(widget.styleSheet() + "margin-right: 180px;")

        self.chat_list.scrollToBottom()

    def speakText(self, text):
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.stop()
        self.tts_thread = TTSThread(text, voice=self.tts_voice, speed=self.tts_speed)
        self.tts_thread.finished.connect(self.onTTSFinished)
        self.tts_thread.start()
        self.stop_tts_button.setEnabled(True)

    def stopTTS(self):
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.stop()
        self.stop_tts_button.setEnabled(False)

    def onTTSFinished(self):
        self.tts_thread.deleteLater()
        self.tts_thread = None
        self.stop_tts_button.setEnabled(False)

    def closeEvent(self, event):
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.stop()
        event.accept()

    def getResponseFromAPI(self, user_input):
        response = self.chat.send_message(user_input)
        return response.text

    def sendInitialBotMessage(self):
        initial_message = "Hey there! 👋 I'm Gemma, your friendly neighborhood software development guru. Got any burning questions about coding or tech? I'm all ears and ready to help! 💻✨"
        self.addMessage('Bot', initial_message)

    def toggleTTS(self, state):
        self.tts_enabled = state == Qt.Checked

    
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
        
        # Apply stylesheets for a modern look
        settings_widget.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 5px;
                transition-duration: 0.4s;
            }
            QPushButton:hover {
                background-color: white;
                color: black;
                border: 2px solid #4CAF50;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid gray;
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: -5px 0;
            }
        """)

        # API Settings
        api_group = QGroupBox("API Settings")
        api_layout = QVBoxLayout()

        # Gemini API setting
        gemini_layout = QHBoxLayout()
        api_label = QLabel("Gemini API Key:")
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Enter your Gemini API key")
        api_save_button = QPushButton("Save")
        api_save_button.clicked.connect(self.save_api_key)
        gemini_layout.addWidget(api_label)
        gemini_layout.addWidget(self.api_input)
        gemini_layout.addWidget(api_save_button)

        api_layout.addLayout(gemini_layout)
        api_group.setLayout(api_layout)

        # TTS Settings
        tts_group = QGroupBox("TTS Settings")
        tts_layout = QVBoxLayout()

        # TTS Speed
        speed_layout = QHBoxLayout()
        speed_label = QLabel("TTS Speed:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(-50, 100)
        self.speed_slider.setValue(0)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(25)
        self.speed_value_label = QLabel("0%")
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_value_label)

        # TTS Voice
        voice_layout = QHBoxLayout()
        voice_label = QLabel("TTS Voice:")
        self.voice_combo = QComboBox()
        voices = [
            "en-AU-NatashaNeural", "en-AU-WilliamNeural",
            "en-CA-ClaraNeural", "en-CA-LiamNeural",
            "en-HK-SamNeural", "en-HK-YanNeural",
            "en-IN-NeerjaExpressiveNeural", "en-IN-NeerjaNeural", "en-IN-PrabhatNeural",
            "en-IE-ConnorNeural", "en-IE-EmilyNeural",
            "en-KE-AsiliaNeural", "en-KE-ChilembaNeural",
            "en-NZ-MitchellNeural", "en-NZ-MollyNeural",
            "en-NG-AbeoNeural", "en-NG-EzinneNeural",
            "en-PH-JamesNeural", "en-PH-RosaNeural",
            "en-SG-LunaNeural", "en-SG-WayneNeural",
            "en-ZA-LeahNeural", "en-ZA-LukeNeural",
            "en-TZ-ElimuNeural", "en-TZ-ImaniNeural",
            "en-GB-LibbyNeural", "en-GB-MaisieNeural", "en-GB-RyanNeural", "en-GB-SoniaNeural", "en-GB-ThomasNeural",
            "en-US-AvaMultilingualNeural", "en-US-AndrewMultilingualNeural",
            "en-US-EmmaMultilingualNeural", "en-US-BrianMultilingualNeural",
            "en-US-AvaNeural", "en-US-AndrewNeural", "en-US-EmmaNeural", "en-US-BrianNeural",
            "en-US-AnaNeural", "en-US-AriaNeural", "en-US-ChristopherNeural",
            "en-US-EricNeural", "en-US-GuyNeural", "en-US-JennyNeural",
            "en-US-MichelleNeural", "en-US-RogerNeural", "en-US-SteffanNeural"
        ]
        self.voice_combo.addItems(voices)
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.voice_combo)

        # Save TTS Settings button
        save_tts_button = QPushButton("Save TTS Settings")
        save_tts_button.clicked.connect(self.save_tts_settings)

        tts_layout.addLayout(speed_layout)
        tts_layout.addLayout(voice_layout)
        tts_layout.addWidget(save_tts_button)
        tts_group.setLayout(tts_layout)

        # Add groups to main settings layout
        settings_layout.addWidget(api_group)
        settings_layout.addWidget(tts_group)
        settings_layout.addStretch()

        settings_widget.setLayout(settings_layout)
        return settings_widget

    def update_speed_label(self, value):
        self.speed_value_label.setText(f"{value}%")

    def save_api_key(self):
        api_key = self.api_input.text()
        if api_key:
            os.environ['Gemini_API'] = api_key
            QMessageBox.information(self, "Success", "Gemini API key saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid API key.")

    def save_tts_settings(self):
        speed = self.speed_slider.value()
        voice = self.voice_combo.currentText()
        self.update_tts_speed(speed)
        self.update_tts_voice(voice)
        QMessageBox.information(self, "Success", "TTS settings saved successfully!")

    def update_theme(self):
        self.setStyleSheet(f"background-color: {primary_color}; color: {secondary_color};")
        
if __name__ == '__main__':
    app = QApplication([])
    PDA_ui = UI()
    PDA_ui.show()
    app.exec_()