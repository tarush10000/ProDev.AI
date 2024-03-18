import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeView, QVBoxLayout, QPushButton,
                             QWidget, QFileDialog, QMessageBox, QFileSystemModel, QSplitter,
                             QInputDialog)
from PyQt5.QtCore import Qt

class FolderOpener(QMainWindow):
    def __init__(self):
        super().__init__()
        self.currentDirectory = ''
        self.initUI()

    def initUI(self):
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setStyleSheet("background-color: black;")

        self.mainLayout = QVBoxLayout(self.centralWidget)

        # Splitter for the two main areas of the window
        self.splitter = QSplitter(Qt.Horizontal)
        self.mainLayout.addWidget(self.splitter)

        # Initialize the left panel with buttons
        self.initLeftPanel()

        # Initialize the right panel for displaying the folder contents
        self.initRightPanel()

        self.setGeometry(300, 300, 1000, 600)
        self.setWindowTitle('Folder and File Opener')
        self.show()

    def initLeftPanel(self):
        self.leftPanel = QWidget()
        self.leftPanelLayout = QVBoxLayout(self.leftPanel)
        self.leftPanelLayout.addStretch(1)

        # Open Folder Button
        self.openFolderBtn = QPushButton('Open Folder')
        self.openFolderBtn.setStyleSheet("background-color: grey; color: white; font-size: 14px;")
        self.openFolderBtn.clicked.connect(self.openFolder)
        self.leftPanelLayout.addWidget(self.openFolderBtn)

        # Create File Button
        self.createFileBtn = QPushButton('Create File')
        self.createFileBtn.setStyleSheet("background-color: grey; color: white; font-size: 14px;")
        self.createFileBtn.clicked.connect(self.createFile)
        self.createFileBtn.setEnabled(False)
        self.leftPanelLayout.addWidget(self.createFileBtn)

        # Create Folder Button
        self.createFolderBtn = QPushButton('Create Folder')
        self.createFolderBtn.setStyleSheet("background-color: grey; color: white; font-size: 14px;")
        self.createFolderBtn.clicked.connect(self.createFolder)
        self.createFolderBtn.setEnabled(False)
        self.leftPanelLayout.addWidget(self.createFolderBtn)

        self.leftPanelLayout.addStretch(1)
        self.splitter.addWidget(self.leftPanel)

    def initRightPanel(self):
        # TreeView for displaying folder contents
        self.treeView = QTreeView()
        self.treeView.setStyleSheet("background-color: black; color: white;")
        self.splitter.addWidget(self.treeView)

        self.model = QFileSystemModel()
        self.treeView.setModel(self.model)

    def openFolder(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if directory:
            self.currentDirectory = directory
            self.model.setRootPath(directory)
            self.treeView.setRootIndex(self.model.index(directory))
            self.createFileBtn.setEnabled(True)
            self.createFolderBtn.setEnabled(True)

    def createFile(self):
        if self.currentDirectory:
            name, _ = QFileDialog.getSaveFileName(self, "Create File", self.currentDirectory)
            if name:
                with open(name, 'w') as file:
                    pass
                self.model.setRootPath(self.currentDirectory)  # Refresh view
        else:
            QMessageBox.warning(self, "No Folder Selected", "Please select a folder first.")

        # Implementation for creating a new file

    def createFolder(self):
        if self.currentDirectory:
            folderName, ok = QInputDialog.getText(self, "Create Folder", "Folder name:")
            if ok and folderName:
                fullPath = os.path.join(self.currentDirectory, folderName)
                try:
                    os.makedirs(fullPath, exist_ok=True)
                    self.model.setRootPath(self.currentDirectory)  # Refresh view
                    self.treeView.setRootIndex(self.model.index(self.currentDirectory))
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to create folder: {e}")
        else:
            QMessageBox.warning(self, "No Folder Selected", "Please select a folder first.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FolderOpener()
    sys.exit(app.exec_())
