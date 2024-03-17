from langchain_community.llms import Ollama


llm = Ollama(model="mistral")


query = "Write the steps that a software engineer would use in order to make a software using Python  with frontend using PyQt that would be able to take in the info of the patients and then save them to a MySQL databaseEach step should be written in a way to classify it into 1 of the following 3 categories -1. Shell -> Needs some code to be written in the Command Prompt or Terminal2. Code -> That can be directly copied and pasted into VS Code3. User Input -> That needs the user to add some info or some relevant image that is needed inside the softwareThe steps should be detailed enough that they could be used as a prompt to instruct some AI to do the next task and not contain any code or additional info as it would be added later by the other AI"
result = ""
for chunks in llm.stream(query):
    result += chunks
    print(chunks)
print (result)  