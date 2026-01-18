from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget

from instalacja import EkranInstalacji
from alarmy import EkranAlarmow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projekt SCADA (PyQt5)")
        self.setFixedSize(1200, 860)

        outer = QVBoxLayout()
        self.setLayout(outer)

        top = QHBoxLayout()
        outer.addLayout(top)

        self.btn_inst = QPushButton("Ekran: Instalacja")
        self.btn_inst.setStyleSheet("background-color: #444; color: white; padding: 8px;")
        top.addWidget(self.btn_inst)

        self.btn_alarm = QPushButton("Ekran: Alarmy/Raport")
        self.btn_alarm.setStyleSheet("background-color: #444; color: white; padding: 8px;")
        top.addWidget(self.btn_alarm)

        self.stack = QStackedWidget()
        outer.addWidget(self.stack)

        self.ekran_alarmow = EkranAlarmow()
        self.ekran_instalacji = EkranInstalacji(log_callback=self.ekran_alarmow.dodaj_log)

        self.stack.addWidget(self.ekran_instalacji)
        self.stack.addWidget(self.ekran_alarmow)

        self.btn_inst.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_alarm.clicked.connect(lambda: self.stack.setCurrentIndex(1))