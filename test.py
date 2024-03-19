from langchain_community.llms import Ollama

llm = Ollama(model = "codellama:13b")

query = "given that the following code is already writen "

for chunk in  llm.stream("Import the necessary PyQt5 modules: QtWidgets, QtCore, and QtGui (syntax: import sys; import QtWidgets as qw, QtCore as qc, QtGui as qg)")

print(response)