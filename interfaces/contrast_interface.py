from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider, QDialogButtonBox, QDialog, QVBoxLayout, QCheckBox

class ContrastDialog(QDialog):
    def __init__(self, parent: None):
        super().__init__(parent)
        self.setWindowTitle("Adjust Contrast")
        
        layout = QVBoxLayout()
        
        self.auto_contrast = QCheckBox("Auto Contrast")
        self.auto_contrast = 
    