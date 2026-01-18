from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainterPath, QColor, QPen


class Rura:
    def __init__(self, punkty, grubosc=14, kolor=QColor(90, 90, 90)):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    def draw(self, painter):
        if len(self.punkty) < 2:
            return

        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        # OSTRE KATY 90 STOPNI: MiterJoin + SquareCap
        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 6, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)


class Zbiornik:
    def __init__(self, x, y, width=130, height=190, nazwa=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa

        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc if self.pojemnosc > 0 else 0.0

    def czy_pusty(self):
        return self.aktualna_ilosc <= 0.1

    def czy_pelny(self):
        return self.aktualna_ilosc >= self.pojemnosc - 0.1

    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)

    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)

    def draw(self, painter):
        # ciecz
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 210))
            painter.drawRect(int(self.x + 4), int(y_start + 2), int(self.width - 8), int(h_cieczy - 4))

        # obrys
        pen = QPen(QColor(240, 240, 240), 4, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        # podpis + %
        painter.setPen(QColor(240, 240, 240))
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)
        painter.drawText(int(self.x), int(self.y + self.height + 22), f"{int(self.poziom * 100)}%")


class Pompa:
    def __init__(self, x, y, promien=26):
        self.x = x
        self.y = y
        self.promien = promien
        self.wlaczona = False
        self._anim_phase = 0

    def przelacz(self):
        self.wlaczona = not self.wlaczona

    def tick(self):
        if self.wlaczona:
            self._anim_phase = (self._anim_phase + 2) % 40

    def draw(self, painter):
        # obudowa
        pen = QPen(QColor(240, 240, 240), 3)
        painter.setPen(pen)
        painter.setBrush(QColor(50, 50, 50))
        painter.drawEllipse(int(self.x - self.promien), int(self.y - self.promien),
                            int(self.promien * 2), int(self.promien * 2))

        # stan
        painter.setBrush(QColor(0, 200, 120) if self.wlaczona else QColor(200, 60, 60))
        painter.drawEllipse(int(self.x - 7), int(self.y - 7), 14, 14)

        # łopatki (prosta animacja)
        if self.wlaczona:
            painter.setPen(QPen(QColor(0, 180, 255), 3))
            a = self._anim_phase
            painter.drawLine(int(self.x), int(self.y), int(self.x + 18), int(self.y - 10 + (a % 10)))
            painter.drawLine(int(self.x), int(self.y), int(self.x - 16 + (a % 8)), int(self.y + 14))