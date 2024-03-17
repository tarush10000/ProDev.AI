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

def shell(self, query):
    llm = Ollama(model="mistral")
    result = ""
    for chunks in llm.stream(query):
        result += chunks
    return result

def categorize_text(self , input_text):
    parts = input_text.split('Category:')[1:] 
    output = []
    
    for part in parts:
        lines = part.strip().split('\n', 1)
        category_name = lines[0].strip()
        text = lines[1].strip() if len(lines) > 1 else ''
        output.append({category_name: text})
    
    return output
def runQuery(json_data):            #expects data from categorize_text function
    for i in json_data:
        print(i.keys())
        print(i.values())
        print("=============================================")
        if("Shell" in list(i.keys())[0]):
            query = list(i.values())[0]     #query for shell command generation
            print(">>>>>>>>>>>running shell function <<<<<<<<<<<<")
        else:
            query = list(i.values())[0]     #query for code generation
            print(">>>>>>>>>>>>running code function <<<<<<<<<<<")
        result = ""
        for chunks in llm.stream(query):
            result += chunks
            print(chunks ,end="")