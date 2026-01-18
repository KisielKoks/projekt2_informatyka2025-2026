from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QSlider
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor

from elementy import Zbiornik, Rura, Pompa


class EkranInstalacji(QWidget):
    def __init__(self, log_callback):
        super().__init__()
        self.log_callback = log_callback

        self.setFixedSize(1150, 760)

        # --- Zbiorniki ---
        self.z1 = Zbiornik(120, 260, nazwa="Zbiornik 1")
        self.z2 = Zbiornik(470, 260, nazwa="Zbiornik 2")
        self.z3 = Zbiornik(930, 120, nazwa="Zbiornik 3")
        self.z4 = Zbiornik(930, 440, nazwa="Zbiornik 4")
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        # start Z1
        self.z1.aktualna_ilosc = 70.0
        self.z1.aktualizuj_poziom()

        # --- Rozdzielacz (miejsce trójnika) ---
        p3 = self.z2.punkt_dol_srodek()
        self.manifold_x = p3[0] + 120
        self.manifold_y = p3[1]

        # --- Pompa w miejscu "czerwonym" (na węźle / pionie) ---
        self.pompa = Pompa(int(self.manifold_x), int(self.manifold_y - 10))

        # --- Rury (kąty 90°) ---
        # Z1 -> Z2
        p1 = self.z1.punkt_dol_srodek()
        p2 = self.z2.punkt_gora_srodek()
        x_mid = (p1[0] + p2[0]) / 2
        self.rura1 = Rura([p1, (x_mid, p1[1]), (x_mid, p2[1]), p2])

        # Z2 -> Z3 (gałąź górna)
        p4 = self.z3.punkt_gora_srodek()
        self.rura2 = Rura([p3, (self.manifold_x, p3[1]), (self.manifold_x, p4[1]), p4])

        # Z2 -> Pompa -> Z4 (gałąź dolna: prosto w prawo, potem prosto w dół do Z4)
        pump_pt = (self.pompa.x, self.pompa.y)
        p5 = self.z4.punkt_gora_srodek()
        self.rura3 = Rura([
            p3,
            (self.manifold_x, p3[1]),
            (self.manifold_x, pump_pt[1]),
            pump_pt,
            (p5[0], pump_pt[1]),   # prosto w prawo
            (p5[0], p5[1]),        # prosto w dół do wejścia Z4
            p5
        ])

        self.rury = [self.rura1, self.rura2, self.rura3]

        # --- Timer / proces ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)
        self.running = False

        self.flow_speed_gravity = 0.6
        self.flow_speed_pump = 1.6

        # --- UI na dole ---
        base_y = 690

        self.btn_start = QPushButton("Start / Stop", self)
        self.btn_start.setGeometry(60, base_y, 150, 44)
        self.btn_start.setStyleSheet("background-color: #444; color: white;")
        self.btn_start.clicked.connect(self.przelacz_symulacje)

        self.btn_pompa = QPushButton("Pompa: OFF", self)
        self.btn_pompa.setGeometry(230, base_y, 150, 44)
        self.btn_pompa.setStyleSheet("background-color: #555; color: white;")
        self.btn_pompa.clicked.connect(self.przelacz_pompe)

        self.lbl_z1 = QLabel("Start Z1: 70%", self)
        self.lbl_z1.setGeometry(410, base_y - 18, 220, 18)
        self.lbl_z1.setStyleSheet("color: white;")

        self.slider_z1 = QSlider(Qt.Horizontal, self)
        self.slider_z1.setGeometry(410, base_y + 10, 260, 22)
        self.slider_z1.setRange(0, 100)
        self.slider_z1.setValue(70)
        self.slider_z1.valueChanged.connect(self.ustaw_start_z1)

        self.lbl_pump = QLabel("Moc pompy: 60%", self)
        self.lbl_pump.setGeometry(700, base_y - 18, 220, 18)
        self.lbl_pump.setStyleSheet("color: white;")

        self.slider_pump = QSlider(Qt.Horizontal, self)
        self.slider_pump.setGeometry(700, base_y + 10, 260, 22)
        self.slider_pump.setRange(10, 100)
        self.slider_pump.setValue(60)
        self.slider_pump.valueChanged.connect(self.ustaw_moc_pompy)

        # logowanie tylko raz
        self._z3_full_logged = False
        self._z4_full_logged = False
        self._z1_empty_logged = False

    def przelacz_symulacje(self):
        if self.running:
            self.timer.stop()
            self.log_callback("Symulacja zatrzymana.")
        else:
            self.timer.start(20)
            self.log_callback("Symulacja uruchomiona.")
        self.running = not self.running

    def przelacz_pompe(self):
        self.pompa.przelacz()
        self.btn_pompa.setText("Pompa: ON" if self.pompa.wlaczona else "Pompa: OFF")
        self.log_callback(f"Pompa {'ON' if self.pompa.wlaczona else 'OFF'}.")

    def ustaw_start_z1(self, value):
        self.lbl_z1.setText(f"Start Z1: {value}%")
        self.z1.aktualna_ilosc = self.z1.pojemnosc * (value / 100.0)
        self.z1.aktualizuj_poziom()
        self.update()

    def ustaw_moc_pompy(self, value):
        self.lbl_pump.setText(f"Moc pompy: {value}%")
        self.flow_speed_pump = 0.6 + (value / 100.0) * 2.0

    def logika_przeplywu(self):
        self.pompa.tick()

        # --- Histereza bufora Z2 ---
        START_OUT = 0.60
        STOP_OUT = 0.20

        if not hasattr(self, "z2_release"):
            self.z2_release = False

        if self.z2.poziom >= START_OUT:
            self.z2_release = True
        elif self.z2.poziom <= STOP_OUT:
            self.z2_release = False

        # Priorytet: najpierw Z4, potem Z3
        THRESHOLD_Z4_FIRST = 0.60

        # Z1 -> Z2
        plynie_1 = False
        if not self.z1.czy_pusty() and not self.z2.czy_pelny():
            ilosc = self.z1.usun_ciecz(self.flow_speed_gravity)
            self.z2.dodaj_ciecz(ilosc)
            plynie_1 = True
        self.rura1.ustaw_przeplyw(plynie_1)

        plynie_2 = False  # do Z3
        plynie_3 = False  # do Z4

        if self.z2_release:
            out_total = self.flow_speed_gravity

            # najpierw Z4 (pompa)
            if self.pompa.wlaczona and not self.z4.czy_pelny() and self.z2.aktualna_ilosc > 0:
                pumped = out_total * (self.flow_speed_pump / max(self.flow_speed_gravity, 0.01))
                pumped = min(pumped, self.z2.aktualna_ilosc)

                ilosc = self.z2.usun_ciecz(pumped)
                self.z4.dodaj_ciecz(ilosc)
                plynie_3 = True

            # dopiero potem Z3
            if self.z4.poziom >= THRESHOLD_Z4_FIRST or self.z4.czy_pelny():
                if not self.z3.czy_pelny() and self.z2.aktualna_ilosc > 0:
                    ilosc = self.z2.usun_ciecz(out_total)
                    self.z3.dodaj_ciecz(ilosc)
                    plynie_2 = True

        self.rura2.ustaw_przeplyw(plynie_2)
        self.rura3.ustaw_przeplyw(plynie_3)

        # logi
        if self.z1.czy_pusty() and not self._z1_empty_logged:
            self.log_callback("ALARM: Z1 pusty.")
            self._z1_empty_logged = True

        if self.z3.czy_pelny() and not self._z3_full_logged:
            self.log_callback("INFO: Z3 pełny.")
            self._z3_full_logged = True

        if self.z4.czy_pelny() and not self._z4_full_logged:
            self.log_callback("INFO: Z4 pełny.")
            self._z4_full_logged = True

        if self.z3.czy_pelny() and self.z4.czy_pelny():
            if self.running:
                self.timer.stop()
                self.running = False
                self.log_callback("Proces zakończony: Z3 i Z4 pełne. (Auto STOP)")

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Wymuszenie tła
        p.fillRect(self.rect(), Qt.black)

        # rury
        for r in self.rury:
            r.draw(p)

        # węzeł rozgałęzienia (trójnik)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(160, 160, 160))
        p.drawRect(int(self.manifold_x - 6), int(self.manifold_y - 6), 12, 12)

        # pompa (bez napisów)
        self.pompa.draw(p)

        # zbiorniki
        for z in self.zbiorniki:
            z.draw(p)