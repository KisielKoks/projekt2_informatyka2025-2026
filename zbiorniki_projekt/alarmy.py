from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PyQt5.QtGui import QColor


class EkranAlarmow(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #111; color: white;")
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Alarmy / Raport zdarzeń")
        title.setStyleSheet("font-size: 18px; color: white;")
        layout.addWidget(title)

        self.lista = QListWidget()
        self.lista.setStyleSheet("background-color: #222; color: white;")
        layout.addWidget(self.lista)

        info = QLabel("Logi pojawiają się automatycznie podczas symulacji.")
        info.setStyleSheet("color: #ccc;")
        layout.addWidget(info)

    def dodaj_log(self, text):
        self.lista.addItem(text)