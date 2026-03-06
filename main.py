import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QGroupBox,
    QLineEdit, QPushButton,
    QScrollArea, QSplitter
)
from PySide6.QtCore import Qt


GENERIC_PROTOCOLS = {

    "UART": [
        "Status Register",
        "Control Register",
        "Data Register",
        "Baud Register"
    ],

    "SPI": [
        "Status Register",
        "Control Register",
        "Data Register",
        "Clock Register"
    ],

    "I2C": [
        "Status Register",
        "Control Register",
        "Data Register",
        "Clock Register"
    ]
}


ARCH_REGISTERS = {

    "ARM": {

        "UART": {
            "Status Register": ("SR", ["TXE", "RXNE", "TC"]),
            "Control Register": ("CR1", ["UE", "TE", "RE", "RXNEIE"]),
            "Data Register": ("DR", ["DATA"]),
            "Baud Register": ("BRR", ["DIV_MANTISSA", "DIV_FRACTION"])
        },

        "SPI": {
            "Status Register": ("SR", ["RXNE", "TXE", "BSY"]),
            "Control Register": ("CR1", ["SPE", "MSTR", "CPOL", "CPHA"]),
            "Data Register": ("DR", ["DATA"]),
            "Clock Register": ("CR2", ["SSOE"])
        },

        "I2C": {
            "Status Register": ("SR1", ["TXE", "RXNE", "BTF"]),
            "Control Register": ("CR1", ["PE", "START", "STOP", "ACK"]),
            "Data Register": ("DR", ["DATA"]),
            "Clock Register": ("CCR", ["FREQ"])
        }
    },


    "AVR": {

        "UART": {
            "Status Register": ("UCSRA", ["RXC", "TXC", "UDRE"]),
            "Control Register": ("UCSRB", ["RXEN", "TXEN"]),
            "Data Register": ("UDR", ["DATA"]),
            "Baud Register": ("UBRR", ["BAUD"])
        },

        "SPI": {
            "Status Register": ("SPSR", ["SPIF"]),
            "Control Register": ("SPCR", ["SPE", "MSTR"]),
            "Data Register": ("SPDR", ["DATA"]),
            "Clock Register": ("SPCR", ["SPR0", "SPR1"])
        },

        "I2C": {
            "Status Register": ("TWSR", ["TWS"]),
            "Control Register": ("TWCR", ["TWINT", "TWSTA"]),
            "Data Register": ("TWDR", ["DATA"]),
            "Clock Register": ("TWBR", ["BITRATE"])
        }
    },


    "Espressif": {

        "UART": {
            "Status Register": ("UART_STATUS_REG", ["TXFIFO_CNT", "RXFIFO_CNT"]),
            "Control Register": ("UART_CONF0_REG", ["UART_TX_EN", "UART_RX_EN"]),
            "Data Register": ("UART_FIFO_REG", ["DATA"]),
            "Baud Register": ("UART_CLKDIV_REG", ["CLKDIV"])
        },

        "SPI": {
            "Status Register": ("SPI_CMD_REG", ["USR"]),
            "Control Register": ("SPI_CTRL_REG", ["SPI_ENABLE"]),
            "Data Register": ("SPI_W0_REG", ["DATA"]),
            "Clock Register": ("SPI_CLOCK_REG", ["CLKDIV"])
        },

        "I2C": {
            "Status Register": ("I2C_STATUS_REG", ["BUS_BUSY"]),
            "Control Register": ("I2C_CTR_REG", ["TRANS_START"]),
            "Data Register": ("I2C_DATA_REG", ["DATA"]),
            "Clock Register": ("I2C_CLK_CONF_REG", ["SCL_LOW", "SCL_HIGH"])
        }
    }

}

ARCHITECTURES = ["ARM", "AVR", "Espressif"]


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ProtoConfig Studio")
        self.setGeometry(100, 100, 1100, 700)

        self.setStyleSheet("""

        QLabel:hover{ color:blue; }

        QLineEdit:hover{ border:2px solid blue; }

        QGroupBox{
        border:2px solid #4CAF50;
        margin-top:10px;
        font-weight:bold;
        }

        QPushButton{
        padding:6px;
        font-weight:bold;
        }

        QPushButton#exitButton{
        background-color:red;
        color:white;
        }

        QSplitter::handle{
        background-color:black;
        width:4px;
        }

        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # SPLITTER (RESIZABLE PANELS)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # LEFT PANEL

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        self.arch_combo = QComboBox()
        self.arch_combo.addItems(ARCHITECTURES)

        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(GENERIC_PROTOCOLS.keys())

        left_layout.addWidget(QLabel("Architecture"))
        left_layout.addWidget(self.arch_combo)

        left_layout.addSpacing(20)

        left_layout.addWidget(QLabel("Protocol"))
        left_layout.addWidget(self.protocol_combo)

        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # RIGHT PANEL

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        splitter.addWidget(right_widget)

        splitter.setSizes([250, 850])

        # SCROLL AREA

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.register_layout = QVBoxLayout()
        self.container.setLayout(self.register_layout)

        self.scroll.setWidget(self.container)

        right_layout.addWidget(self.scroll)

        # BUTTONS

        btn_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("""
        background-color:#2196F3;
        color:white;
        """)

        self.generate_button = QPushButton("Generate Code")
        self.generate_button.setStyleSheet("""
        background-color:#4CAF50;
        color:white;
        """)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setObjectName("exitButton")

        btn_layout.addWidget(self.refresh_button)
        btn_layout.addWidget(self.generate_button)
        btn_layout.addWidget(self.exit_button)

        right_layout.addLayout(btn_layout)

        # SIGNALS

        self.protocol_combo.currentTextChanged.connect(self.update_registers)
        self.arch_combo.currentTextChanged.connect(self.update_registers)

        self.refresh_button.clicked.connect(self.update_registers)
        self.generate_button.clicked.connect(self.generate_code)

        self.exit_button.clicked.connect(self.close)

        self.update_registers()


    def clear_registers(self):

        while self.register_layout.count():
            item = self.register_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()


    def update_registers(self):

        self.clear_registers()

        arch = self.arch_combo.currentText()
        protocol = self.protocol_combo.currentText()

        protocol_sections = GENERIC_PROTOCOLS[protocol]
        arch_data = ARCH_REGISTERS[arch][protocol]

        for section in protocol_sections:

            reg_real_name, bits = arch_data[section]

            reg_group = QGroupBox(f"{section} ({reg_real_name})")

            reg_layout = QVBoxLayout()

            base_layout = QHBoxLayout()
            base_layout.addWidget(QLabel("Base Address"))

            base_edit = QLineEdit()
            base_edit.setPlaceholderText("0x40000000")

            base_layout.addWidget(base_edit)
            reg_layout.addLayout(base_layout)

            header = QHBoxLayout()
            header.addWidget(QLabel("Bit Name"))
            header.addWidget(QLabel("Position"))
            header.addWidget(QLabel("Length (bits)"))

            reg_layout.addLayout(header)

            for bit_name in bits:

                row = QHBoxLayout()

                row.addWidget(QLabel(bit_name))

                pos_edit = QLineEdit()
                pos_edit.setAlignment(Qt.AlignCenter)
                pos_edit.setPlaceholderText("Pos")

                len_edit = QLineEdit()
                len_edit.setAlignment(Qt.AlignCenter)
                len_edit.setPlaceholderText("bits")

                row.addWidget(pos_edit)
                row.addWidget(len_edit)

                reg_layout.addLayout(row)

            reg_group.setLayout(reg_layout)

            self.register_layout.addWidget(reg_group)


    def generate_code(self):

        arch = self.arch_combo.currentText()
        protocol = self.protocol_combo.currentText()

        print("\n===== GENERATED REGISTER TEMPLATE =====\n")

        data = ARCH_REGISTERS[arch][protocol]

        for section, (reg, bits) in data.items():

            print(f"// {section}")
            print(f"#define {reg}_ADDR   0x00000000")

            for bit in bits:
                print(f"#define {reg}_{bit}")

            print("")


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())