from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.chains import create_extraction_chain
from langchain_experimental.llms.ollama_functions import OllamaFunctions

llm = Ollama(model="mistral")

template_string = """
Write the steps that a software engineer would use in order to make a software using Python with frontend using PyQt that would be able to create {input} 
each step should be written in a way to classify it into 1 of the following 2 categories 
-1. Shell -> Needs some code to be written in the Command Prompt or 
Terminal2. Code -> That can be directly copied and pasted into VS Code. 
DO NOT PRINT ANY CODES and generate the steps for windows operating system

"""


prompt_template = ChatPromptTemplate.from_template(template_string)


query = prompt_template.format_messages( input = "calculator" )

print(query)

# response = llm.invoke(query)
# print(response)

category = ResponseSchema(name="category",description="the step belongs to shell / code")

step = ResponseSchema(name="step",description="describe the step")

response_schemas = [step,category]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

format_instructions = output_parser.get_format_instructions()

print(format_instructions)

template_string = """
Write the steps that a software engineer would use in order to make a software using Python with frontend using PyQt that would be able to create {input} 
each step should be written in a way to classify it into 1 of the following 2 categories 
-1. Shell -> Needs some code to be written in the Command Prompt or 
Terminal2. Code -> That can be directly copied and pasted into VS Code. 
DO NOT PRINT ANY CODES and generate the steps for windows operating system
{format_instructions}
"""

prompt = ChatPromptTemplate.from_template(template=template_string)

messages = prompt.format_messages(input = "calculator ",format_instructions=format_instructions)

response = llm.invoke(messages)
print(response)

# prompt = ChatPromptTemplate(
#     messages=[
#         HumanMessagePromptTemplate.from_template(template_string)  
#     ],
#     input_variables=["input"],
#     partial_variables={"format_instructions": format_instructions},
#     output_parser=output_parser 
# )
# chain = LLMChain(llm=llm,prompt=prompt)
# response = chain.predict_and_parse(input = "calculator")

# llm = OllamaFunctions(model="mistral", temperature=0)
# chain = create_extraction_chain(schema, llm)
# chain.run(input)