from langchain_community.llms import Ollama


llm = Ollama(model="mistral")


# query = "Write the steps that a software engineer would use in order to make a software using Python  with frontend using PyQt that would be able to take in the info of the patients and then save them to a MySQL databaseEach step should be written in a way to classify it into 1 of the following 3 categories -1. Shell -> Needs some code to be written in the Command Prompt or Terminal2. Code -> That can be directly copied and pasted into VS Code3. User Input -> That needs the user to add some info or some relevant image that is needed inside the softwareThe steps should be detailed enough that they could be used as a prompt to instruct some AI to do the next task and not contain any code or additional info as it would be added later by the other AI"
# result = ""
# for chunks in llm.stream(query):
#     result += chunks
#     print(chunks)
# print (result)  

def ask_operating_system(self,input,):
    print("Which operating system are you targeting? (Windows, macOS, Linux, etc.)")
    operating_system = input("Enter your choice: ")
    return operating_system

def Initial_Response(input, Oper_Sys):
    llm = Ollama(model="mistral")
    query = "Enter the steps for a Software that " + input + " in " + Oper_Sys + " Operating System."
    print(query)
    result = ""
    for chunks in llm.stream(query):
        result += chunks
    return result

class MistralGuardrails:
    def _init_(self):
        self.llm = Ollama(model="mistral")

    def generate_steps(self, input_text):
        result = ""
        for chunks in self.llm.stream(input_text):
            if chunks.startswith("Step"):
                result += chunks + "\n"  
        return result
    
def Terminal_Response(self, input, Oper_Sys):
    llm = Ollama(model="mistral")
    result = "For the steps provided generate the terminal commands for  "+input+" in "+Oper_Sys+" Operating System."
    for chunks in llm.stream(input):
        result += chunks
    return result

def Code_Response(self, input, Oper_Sys):
    llm = Ollama(model="mistral")
    result = "Generate the code for " + input + " in " + Oper_Sys + " Operating System."
    for chunks in llm.stream(input):
        result += chunks
    return result

def Explanation_Response(self, input, Oper_Sys):
    llm = Ollama(model="mistral")
    result = "Generate the explanation for " + input +" in " + Oper_Sys + " Operating System."
    for chunks in llm.stream(input):
        result += chunks
    return result

def Detailed_Explain_Response(self, input, Oper_Sys):
    llm = Ollama(model="mistral")
    result = "Here is the detailed explanation for  " + input +" in " + Oper_Sys + " Operating System."
    for chunks in llm.stream(input):
        result += chunks
    return result