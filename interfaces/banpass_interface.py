from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QCheckBox, QPushButton, QGroupBox, QWidget

class BandpassFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FFT Bandpass Filter")
        
        #Widgets
        self.large_spin = QDoubleSpinBox()
        self.large_spin.setRange(0, 10000)
        self.large_spin.setDecimals(0)
        self.large_spin.setSuffix("px")
        
        self.small_spin = QDoubleSpinBox()
        self.small_spin.setRange(0, 10000)
        self.small_spin.setDecimals(0)
        self.small_spin.setSuffix("px")
        
        self.suppress_stripes = QCheckBox()
        self.tolearance_spin = QDoubleSpinBox()
        self.tolearance_spin.setValue(15)
        self.tolearance_spin.setSuffix("")
        
        self.autoscale_ab = QCheckBox("AutoScale After Filtering")
        self.autoscale_ab.setChecked(True)
        self.saturated_cb = QCheckBox("Saturated image when autoscaling")
        self.display_filter_cb = QCheckBox("Display Filter")
        
        layout = QVBoxLayout()
        params_group = QGroupBox("Filter Parameters")
        params_layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Filter Large Structures down to:"))
        row1.addWidget(self.large_spin)
        params_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Filter Small Structures up to:"))
        row2.addWidget(self.small_spin)
        params_layout.addLayout(row2)
        
        row3=QHBoxLayout()
        row3.addWidget(QLabel("Suppress Stripes:"))
        row3.addWidget(self.suppress_stripes)
        params_layout.addLayout(row3)
        
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Tolerance of direction:"))
        row4.addWidget(self.suppress_stripes)
        params_layout.addLayout(row4)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        options_layout.addWidget(self.autoscale_ab)
        options_layout.addWidget(self.saturated_cb)
        options_layout.addWidget(self.display_filter_cb)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def get_values(self):
        return {
            "large_cutoff":self.large_spin.value(),
            "small_cutoff":self.small_spin.value(),
            "suppress_stripes":self.suppress_stripes.isChecked(),
            "tolerance":self.tolearance_spin.value(),
            "autoscale":self.autoscale_ab.isChecked(),
            'saturate': self.saturated_cb.isChecked(),
            "display_filter":self.display_filter_cb.isChecked()
        }        