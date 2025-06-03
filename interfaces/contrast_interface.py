from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider, QDialogButtonBox, QDialog, QVBoxLayout, QCheckBox, QGroupBox, QLabel

class ContrastDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adjust Contrast")
        
        layout = QVBoxLayout()
        
        self.auto_contrast = QCheckBox("Auto Contrast")
        self.auto_contrast.setChecked(True)
        self.auto_contrast.toggled.connect(self.toggle_manual)
        layout.addWidget(self.auto_contrast)
        
        self.manual_group = QGroupBox("Manual Adjustment")
        manual_layout = QVBoxLayout()
        
        #Brightness Slider
        self.brightness_label = QLabel("Brightness: 0")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(
            lambda v:self.brightness_label.setText(f"Brightness: {v}")
        )
        
        #Contrast Slider
        self.contrast_label = QLabel("Contrast: 100%")
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0,200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(
            lambda v:self.contrast_label.setText(f"Contrast: {v}%")
        )
        
        manual_layout.addWidget(self.brightness_label)
        manual_layout.addWidget(self.brightness_slider)
        manual_layout.addWidget(self.contrast_label)
        manual_layout.addWidget(self.contrast_slider)
        
        self.manual_group.setLayout(manual_layout)
        self.manual_group.setEnabled(False)
        layout.addWidget(self.manual_group)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)
    
    def toggle_manual(self, checked):
        self.manual_group.setEnabled(not checked)
        
    def get_value(self):
        return{
            'auto': self.auto_contrast.isChecked(),
            'brightness':self.brightness_slider.value(),
            'contrast':self.contrast_slider.value() / 100.0
        }