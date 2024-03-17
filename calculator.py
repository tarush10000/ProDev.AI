from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt

class CalculatorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Calculator')
        self.setGeometry(300, 300, 350, 450)

        # Create display label
        self.display = QLabel('', alignment=Qt.AlignRight)

        # Create number and operator buttons
        self.button_0 = QPushButton('0')
        self.button_1 = QPushButton('1')
        self.button_2 = QPushButton('2')
        self.button_3 = QPushButton('3')
        self.button_4 = QPushButton('4')
        self.button_5 = QPushButton('5')
        self.button_6 = QPushButton('6')
        self.button_7 = QPushButton('7')
        self.button_8 = QPushButton('8')
        self.button_9 = QPushButton('9')
        self.add = QPushButton('+')
        self.subtract = QPushButton('-')
        self.multiply = QPushButton('*')
        self.divide = QPushButton('/')
        self.equal = QPushButton('=')

        # Create layouts and arrange UI components
        self.button_layout = QGridLayout()
        self.button_layout.addWidget(self.button_0, 3, 0)
        self.button_layout.addWidget(self.button_1, 2, 0)
        self.button_layout.addWidget(self.button_2, 2, 1)
        self.button_layout.addWidget(self.button_3, 2, 2)
        self.button_layout.addWidget(self.button_4, 1, 0)
        self.button_layout.addWidget(self.button_5, 1, 1)
        self.button_layout.addWidget(self.button_6, 1, 2)
        self.button_layout.addWidget(self.button_7, 0, 0)
        self.button_layout.addWidget(self.button_8, 0, 1)
        self.button_layout.addWidget(self.button_9, 0, 2)
        self.button_layout.addWidget(self.add, 0, 3)
        self.button_layout.addWidget(self.subtract, 1, 3)
        self.button_layout.addWidget(self.multiply, 2, 3)
        self.button_layout.addWidget(self.divide, 3, 3)
        self.button_layout.addWidget(self.equal, 3, 2)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addLayout(self.button_layout)
        hbox.addStretch()

        vbox = QVBoxLayout()
        vbox.addWidget(self.display)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        # Connect buttons to slots
        self.button_0.clicked.connect(self.on_button_clicked)
        self.button_1.clicked.connect(self.on_button_clicked)
        self.button_2.clicked.connect(self.on_button_clicked)
        self.button_3.clicked.connect(self.on_button_clicked)
        self.button_4.clicked.connect(self.on_button_clicked)
        self.button_5.clicked.connect(self.on_button_clicked)
        self.button_6.clicked.connect(self.on_button_clicked)
        self.button_7.clicked.connect(self.on_button_clicked)
        self.button_8.clicked.connect(self.on_button_clicked)
        self.button_9.clicked.connect(self.on_button_clicked)
        self.add.clicked.connect(self.on_operator_clicked)
        self.subtract.clicked.connect(self.on_operator_clicked)
        self.multiply.clicked.connect(self.on_operator_clicked)
        self.divide.clicked.connect(self.on_operator_clicked)
        self.equal.clicked.connect(self.on_equal_clicked)

        self.show()

    def on_button_clicked(self):
        button = self.sender()
        value = button.text()
        self.append_to_display(value)

    def on_operator_clicked(self):
        operator = self.sender()
        self.append_to_display(operator.text())

    def append_to_display(self, value):
        current_value = self.display.text()
        new_value = current_value + value
        self.display.setText(new_value)

    def on_equal_clicked(self):
        expression = self.display.text().replace('×', '*').replace('÷', '/')
        try:
            result = eval(expression)
            self.display.setText(str(result))
        except ZeroDivisionError:
            self.display.setText("Error!")

if __name__ == "__main__":
    app = QApplication([])
    calculator_app = CalculatorApp()
    app.exec_()
