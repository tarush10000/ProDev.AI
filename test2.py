from langchain.chains import create_extraction_chain
from langchain_experimental.llms.ollama_functions import OllamaFunctions

# Schema
schema = {
    "properties": {
        "stepNumber": {"type" : "integer"},
        "step": {"type": "string"},
        "category": {"type": "string"}
    }
}

# Input
input = "calculator"

template_string = f"""
Write the steps that a software engineer would use in order to make a software using Python with frontend using PyQt that would be able to create {input} 
each step should be written in a way to classify it into 1 of the following 2 categories 
-1. Shell -> Needs some code to be written in the Command Prompt or Terminal
-2. Code -> That can be directly copied and pasted into VS Code. 
DO NOT PRINT ANY CODES and generate the steps for windows operating system

"""

# Run chain
llm = OllamaFunctions(model="mistral")
chain = create_extraction_chain(schema, llm)

for chunk in chain.stream(template_string):
    print(chunk,end="")
