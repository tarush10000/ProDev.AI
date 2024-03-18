from multiprocessing import Process, Queue
import sys, os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout, QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from langchain_community.llms import Ollama

# Define the function outside of the class to be compatible with multiprocessing
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

# Your existing Worker, PDA classes, and other code remain largely unchanged

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Example usage:
    # Assuming step_dict is defined somewhere and ready to use
    step_dict = {}  # This should be your actual step dictionary
    code_gen_process = CodeGenerationProcess(step_dict)
    code_gen_process.start()
    codes = code_gen_process.get_codes()
    print(codes)
    # Continue with the rest of your PyQt application setup
    sys.exit(app.exec_())
