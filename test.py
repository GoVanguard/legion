import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtCore import QProcess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a button to start the process
        self.button = QPushButton("Run date")
        self.button.clicked.connect(self.run_date)

        # Create a text edit to display the output
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        # Create a layout and a central widget
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.output)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Create a QProcess object
        self.process = QProcess()
        # Connect the readyReadStandardOutput signal to a slot
        self.process.readyReadStandardOutput.connect(self.read_output)

    def run_date(self):
        # Start the date command as a QProcess
        self.process.start("/sbin/nmap")

    def read_output(self):
        # Read the standard output from the QProcess
        output = self.process.readAllStandardOutput().data().decode()
        output = output + "\n" + self.process.readAllStandardError().data().decode()
        # Append the output to the text edit
        self.output.append(output)

# Create an application and a main window
app = QApplication(sys.argv)
window = MainWindow()
window.show()
# Run the application
sys.exit(app.exec())

