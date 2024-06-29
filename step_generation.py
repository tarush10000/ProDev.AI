from langchain_community.llms import Ollama

def run_query_1(self):
        llm = Ollama(model="mistral")
        query = "You are an expert software developer and you have been given a task of teaching development using the project that the user provides. Write the steps that a software engineer would use in order to make a software using Python with frontend using PyQt that would be able to" + self.input + "each step should be written in a way to classify it into 1 of the following 2 categories -1. Shell -> Needs some code to be written in the Command Prompt or Terminal2. Code -> That can be directly copied and pasted into VS Code. DO NOT PRINT ANY CODES and generate the steps for " + self.OS + " operating system format. The steps should be in form of a single list with multiple dictionaries where one step is there in one dictionary with keys being category (Code/Shell) , step (description of the step) for each step. Do not give any other text apart from the list. Make sure that the format of list with dictionaries having steps as its elements is retained. Do not give any code or code snippets.The list should be in the form, [{category,step},{category,step},{category,step}....] and should display all the steps and there should not be nested list because all the steps should be in the single list and each dictionary should have only category and step and there should have no codes."
        print(query)
        result = ""
        for chunks in llm.stream(query):
            result += chunks
            # if chunks is not ['{', '}', '[', ']']:
            self.update_text.emit(chunks)
            global steps
            steps = result
        self.finished.emit()

def check_input(self, user_input):
        llm = Ollama(model="mistral")
        query = "You have to tell if the given prompt is a valid description of a software. Prompt: " + user_input + " .Reply 'Yes' or 'No' only and the result shouldn't exceed 15 words."
        result = ""
        for chunks in llm.stream(query):
            result += chunks
        print(result)
        return result

def add_description(self, code_text_widget, code_description_text_widget):
        llm = Ollama(model = "mistral")
        query = "Explain the given code: " + code_text_widget.toPlainText() + "in a concise manner with the word-count of your response not exceeding 40 words."
        print(query)
        result = ""
        for chunks in llm.stream(query):
            result += chunks
            print(chunks)
        code_description_text_widget.setPlainText(code_description_text_widget.toPlainText() + result)

def next_step(self, step_heading_label, code_heading_label, code_heading_widget, code_text_widget, code_description_heading_widget, code_description_text_widget):
        global count
        global codes
        global max_count
        if count < max_count:
            count += 1
            step_heading_label.setText("Step "+ str(count))
            if len(codes) < count:
                llm = Ollama(model = "codeLlama:13b")
                if category[count - 1].lower() == "shell":
                    query = "Write a terminal code for the following instructions: " + str(coding[count-1]) + " . Don't explain the code or add any comments just write the code provide command for windows only"
                else:
                    prev_code = ""
                    for i in range(count):
                        if count > 1 :
                            prev_code += codes[i-1]
                    query = "Write the relevant python code for the following instructions: " + str(coding[count-1]) + " .The code written till now is: " + str(prev_code) + ". Don't exceed or make any new code not required. Append to the existing code in order to add functionality of the prompt"
                print("1")
                result = llm.invoke(query)
                print(result)
                codes.append(result)
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


def run_code(self, code_text_widget, code_play_button):
        llm = Ollama(model = "mistral")
        query1 = "The following text is based on markdown laguage and provided by CodeLlama. Remove all unnecesary comments along with the text at the top and bottom if present which is explaing the code. Also remove any code that won't work or isn't intended for Windows. If no part of the entire text contains code that is meant for windows, try to make a code that would implement the functionality in terminal (Command Prompt) Text: " + code_text_widget.toPlainText() + "\n ONLY HAVE THE CODE AS OUTPUT AND NO COMMENTS OR EXPLANATION AND MAKE NECESSARY SPACING AND ADJUSTMENTS SO THAT THE CODE CAN BE RUN LATER"
        code = ""
        for chunks in llm.stream(query1):
            code += chunks
        query2 = "Take the following text and reply any 1 of the 3 words that suit it (NOTHING OTHER THAN THE 3 WORDS) - Code -> if the text provided can be directly run in python, Terminal -> if the text provided is a terminal code, None -> if the text provided is just simple steps or instructions and doesn't have any code. Text: " + code + ". YOUR REPLY SHOULD BE JUST A SINGLE WORD"
        check = ""
        for chunks in llm.stream(query2):
            check += chunks
        
        if "terminal" in check.lower():
            code_text_widget.setPlainText(code)
            

        elif "code" in check.lower():
            code_text_widget.setPlainText(code)
            app = QApplication([])
            file_name_prompt = QLineEdit()
            dialog = QDialog()
            dialog.setStyleSheet("background-color: rgb(50,50,50); color: rgb(255,255,255); padding: 10px")
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Enter the name of the file to save the code as:"))
            layout.addWidget(file_name_prompt)
            accept_reject_layout = QHBoxLayout()
            dialog.setLayout(layout)
            file_accept_image = QPixmap(resource_path("images/accept.png"))
            file_accept_image = file_accept_image.scaledToHeight(int(app.desktop().screenGeometry().height() * 0.05))
            file_accept_button = QPushButton()
            file_accept_button.setIcon(QIcon(file_accept_image))
            file_accept_button.setCursor(Qt.PointingHandCursor)
            file_accept_button.setFlat(True)
            file_accept_button.clicked.connect(dialog.accept)
            accept_reject_layout.addWidget(file_accept_button)
            file_cancel_image = QPixmap(resource_path("images/cancel.png"))
            file_cancel_image = file_cancel_image.scaledToHeight(int(app.desktop().screenGeometry().height() * 0.05))
            file_cancel_button = QPushButton()
            file_cancel_button.setIcon(QIcon(file_cancel_image))
            file_cancel_button.setCursor(Qt.PointingHandCursor)
            file_cancel_button.setFlat(True)
            file_cancel_button.clicked.connect(dialog.reject)
            accept_reject_layout.addWidget(file_cancel_button)
            layout.addLayout(accept_reject_layout)
            if dialog.exec_():
                file_name = file_name_prompt.text()
            else:
                file_name = None
            code_text, markdown_detected = self.detect_and_remove_markdown(code)
            print(f"Markdown detected: {markdown_detected}")
            app.quit()
            mode = 'w'
            with open(file_name, mode) as file:
                file.write(code_text)
            # print(f"Your code has been {'appended to' if mode == 'a' else 'written in'} {file_name}.")
        else:
            pass