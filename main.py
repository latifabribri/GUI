import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QGroupBox,
    QFormLayout, QLineEdit,
    QCheckBox, QPushButton,
    QMessageBox
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ProtoConfig Studio")
        self.setGeometry(100, 100, 1100, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.left_layout = QVBoxLayout()
        main_layout.addLayout(self.left_layout, 1)

        arch_label = QLabel("Architecture")
        self.arch_combo = QComboBox()
        self.arch_combo.addItems(["ARM", "AVR", "PIC", "Espressif"])

        protocol_label = QLabel("Protocol")
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["UART", "I2C", "SPI"])

        self.left_layout.addWidget(arch_label)
        self.left_layout.addWidget(self.arch_combo)
        self.left_layout.addSpacing(20)
        self.left_layout.addWidget(protocol_label)
        self.left_layout.addWidget(self.protocol_combo)
        self.left_layout.addStretch()

        self.right_layout = QVBoxLayout()
        main_layout.addLayout(self.right_layout, 3)

        self.param_group = QGroupBox("Protocol Parameters")
        self.param_layout = QFormLayout()
        self.param_group.setLayout(self.param_layout)
        self.right_layout.addWidget(self.param_group)

        self.register_group = QGroupBox("Register Configuration")
        self.register_layout = QVBoxLayout()
        self.register_group.setLayout(self.register_layout)
        self.right_layout.addWidget(self.register_group)

        self.bit_tx = QCheckBox("TX Enable")
        self.bit_rx = QCheckBox("RX Enable")
        self.bit_interrupt = QCheckBox("Interrupt Enable")

        self.register_layout.addWidget(self.bit_tx)
        self.register_layout.addWidget(self.bit_rx)
        self.register_layout.addWidget(self.bit_interrupt)

        self.generate_button = QPushButton("Generate Code")
        self.generate_button.setMinimumHeight(40)
        self.right_layout.addWidget(self.generate_button)

        self.right_layout.addStretch()

        self.statusBar().showMessage("Ready")

        self.protocol_combo.currentTextChanged.connect(self.update_parameters)
        self.generate_button.clicked.connect(self.generate_code)

        self.update_parameters(self.protocol_combo.currentText())

    def clear_parameters(self):
        while self.param_layout.rowCount() > 0:
            self.param_layout.removeRow(0)

    def update_parameters(self, protocol):
        self.clear_parameters()

        if protocol == "UART":
            self.baudrate = QLineEdit()
            self.databits = QLineEdit()
            self.parity = QLineEdit()

            self.param_layout.addRow("Baud Rate:", self.baudrate)
            self.param_layout.addRow("Data Bits:", self.databits)
            self.param_layout.addRow("Parity:", self.parity)

        elif protocol == "I2C":
            self.clock_speed = QLineEdit()
            self.device_address = QLineEdit()

            self.param_layout.addRow("Clock Speed:", self.clock_speed)
            self.param_layout.addRow("Device Address:", self.device_address)

        elif protocol == "SPI":
            self.clock_speed = QLineEdit()
            self.mode = QLineEdit()
            self.bit_order = QLineEdit()

            self.param_layout.addRow("Clock Speed:", self.clock_speed)
            self.param_layout.addRow("SPI Mode:", self.mode)
            self.param_layout.addRow("Bit Order:", self.bit_order)

        self.statusBar().showMessage(f"{protocol} configuration loaded")

    def generate_code(self):
        architecture = self.arch_combo.currentText()
        protocol = self.protocol_combo.currentText()

        tx = self.bit_tx.isChecked()
        rx = self.bit_rx.isChecked()
        interrupt = self.bit_interrupt.isChecked()

        message = f"""
Architecture: {architecture}
Protocol: {protocol}

Register Settings:
TX Enable: {tx}
RX Enable: {rx}
Interrupt Enable: {interrupt}
"""

        QMessageBox.information(self, "Generated Configuration", message)
        self.statusBar().showMessage("Code Generated Successfully")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())