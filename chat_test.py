import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, QPushButton, QListWidgetItem, QLabel, QCheckBox
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
import google.generativeai as genai
import os
import pyttsx3

gemini_api_key = os.getenv("Gemini_API")

class TTSThread(QThread):
    finished = pyqtSignal()

    def __init__(self, text):
        QThread.__init__(self)
        self.text = text
        self.engine = None

    def run(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')

        female_voice = next((voice for voice in voices if voice.gender == 'female'), None)
        if female_voice:
            self.engine.setProperty('voice', female_voice.id)
        
        self.engine.say(self.text)
        self.engine.runAndWait()
        self.finished.emit()

    def stop(self):
        if self.engine:
            self.engine.stop()
        self.wait()

class ChatbotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.chat_history_file = 'chat_history.json'
        self.initGemini()
        self.clearChatHistory()
        self.sendInitialBotMessage()
        self.tts_enabled = False
        self.tts_thread = None

    def initUI(self):
        self.setWindowTitle('Gemini API Chatbot')
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet("background-color: #121B22;")

        self.layout = QVBoxLayout()

        # Add refresh button and TTS toggle
        top_layout = QHBoxLayout()
        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.refreshChat)
        self.refresh_button.setStyleSheet("background-color: #2A2F32; color: white;")
        top_layout.addWidget(self.refresh_button)

        self.tts_toggle = QCheckBox('Enable TTS', self)
        self.tts_toggle.setStyleSheet("color: white;")
        self.tts_toggle.stateChanged.connect(self.toggleTTS)
        top_layout.addWidget(self.tts_toggle)

        self.layout.addLayout(top_layout)

        self.chat_list = QListWidget(self)
        self.chat_list.setStyleSheet("""
            QListWidget {
                background-color: #121B22;
                border: none;
            }
            QListWidget::item {
                border: none;
                margin-bottom: 10px;
            }
        """)
        self.layout.addWidget(self.chat_list)

        self.input_layout = QHBoxLayout()
        self.input = QLineEdit(self)
        self.input.setStyleSheet("background-color: #2A2F32; color: white; border: none; padding: 5px;")
        self.input.returnPressed.connect(self.sendMessage)
        self.send_button = QPushButton('Send', self)
        self.send_button.clicked.connect(self.sendMessage)
        self.send_button.setStyleSheet("background-color: #00A884; color: white;")
        self.input_layout.addWidget(self.input)
        self.input_layout.addWidget(self.send_button)

        self.layout.addLayout(self.input_layout)
        self.setLayout(self.layout)

    def initGemini(self):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
        
        initial_instructions = """You are Gemma, the ProDev.AI assistant. You are tasked with helping people to learn software development and solve their queries related to code or software development procedure in general. Stay Polite and talk like a real girl. If a question is not related to software development or coding, politely ask the user to stay on track."""
        self.chat.send_message(initial_instructions)

    def sendMessage(self):
        user_input = self.input.text()
        if user_input.strip() == "":
            return
        
        self.addMessage('User', user_input)
        self.input.clear()

        self.addMessage('Bot', '...')
        QApplication.processEvents()

        try:
            response = self.getResponseFromAPI(user_input)
            self.chat_list.takeItem(self.chat_list.count() - 1)
            self.addMessage('Bot', response)
            if self.tts_enabled:
                self.speakText(response)
        except Exception as e:
            self.chat_list.takeItem(self.chat_list.count() - 1)
            error_message = f"An error occurred: {str(e)}. Please try again later or check your internet connection."
            self.addMessage('Bot', error_message)

    def addMessage(self, sender, message):
        item = QListWidgetItem()
        widget = QLabel(message)
        widget.setWordWrap(True)
        widget.setStyleSheet(f"""
            background-color: {'#005C4B' if sender == 'User' else 'white'};
            color: {'white' if sender == 'User' else 'black'};
            border-radius: 10px;
            padding: 10px;
            max-width: 250px;
        """)
        item.setSizeHint(widget.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, widget)

        if sender == 'User':
            item.setTextAlignment(Qt.AlignRight)
            widget.setStyleSheet(widget.styleSheet() + "margin-left: 40px;")
        else:
            item.setTextAlignment(Qt.AlignLeft)
            widget.setStyleSheet(widget.styleSheet() + "margin-right: 40px;")
        
        self.chat_list.scrollToBottom()

    def getResponseFromAPI(self, user_input):
        response = self.chat.send_message(user_input)
        return response.text

    def clearChatHistory(self):
        if os.path.exists(self.chat_history_file):
            os.remove(self.chat_history_file)
        self.chat_list.clear()

    def refreshChat(self):
        self.clearChatHistory()
        self.initGemini()
        self.sendInitialBotMessage()

    def sendInitialBotMessage(self):
        initial_message = "Hey there! I'm Gemma, your personal Software Development teacher. Do you have any doubts?"
        self.addMessage('Bot', initial_message)

    def toggleTTS(self, state):
        self.tts_enabled = state == Qt.Checked

    def speakText(self, text):
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.stop()
        self.tts_thread = TTSThread(text)
        self.tts_thread.finished.connect(self.onTTSFinished)
        self.tts_thread.start()

    def onTTSFinished(self):
        self.tts_thread.deleteLater()
        self.tts_thread = None

    def closeEvent(self, event):
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chatbot = ChatbotApp()
    chatbot.show()
    sys.exit(app.exec_())