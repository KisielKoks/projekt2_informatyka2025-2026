import sys
from PyQt5.QtWidgets import QApplication

from glowneokno import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    okno = MainWindow()
    okno.show()
    sys.exit(app.exec_())