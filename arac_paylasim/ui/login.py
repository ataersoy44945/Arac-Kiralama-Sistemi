# ============================================================
#   ui/login.py — Giriş & Kayıt Ekranı
# ============================================================

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QStackedWidget, QFrame,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui  import QFont, QColor

# ── Renk Paleti ─────────────────────────────────────────────
BG_DARK  = "#0a0e27"
CARD     = "#1e2847"
BORDER   = "#2d3d6e"
PRIMARY  = "#7c5cff"
PRIM2    = "#5b9fff"
TEXT     = "#f0f4ff"
TEXT2    = "#b4c1e7"
MUTED    = "#8a97c1"
DANGER   = "#ff6b6b"
SUCCESS  = "#34d399"

_BASE_SS = f"""
QMainWindow, QWidget {{
    background-color: {BG_DARK};
    color: {TEXT};
    font-family: 'Segoe UI', Arial;
}}
"""

_INPUT_SS = f"""
QLineEdit {{
    background-color: {CARD};
    color: {TEXT};
    border: 1.5px solid {BORDER};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1.5px solid {PRIMARY};
}}
"""


def _lbl(text, size=13, color=TEXT, bold=False):
    l = QLabel(text)
    f = QFont("Segoe UI", size)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    l.setFont(f)
    l.setStyleSheet(f"color:{color}; background:transparent;")
    return l


def _input(placeholder, echo=False):
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setMinimumHeight(46)
    e.setStyleSheet(_INPUT_SS)
    e.setFont(QFont("Segoe UI", 13))
    if echo:
        e.setEchoMode(QLineEdit.EchoMode.Password)
    return e


def _btn_primary(text, h=48):
    b = QPushButton(text)
    b.setMinimumHeight(h)
    b.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {PRIMARY}, stop:1 {PRIM2});
            color: white; border: none; border-radius: 10px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #6a4aff, stop:1 #4a8fff);
        }}
        QPushButton:pressed {{ background: {PRIMARY}; }}
    """)
    return b


def _btn_ghost(text, h=40):
    b = QPushButton(text)
    b.setMinimumHeight(h)
    b.setFont(QFont("Segoe UI", 12))
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: transparent; color: {MUTED};
            border: 1.5px solid {BORDER}; border-radius: 10px;
        }}
        QPushButton:hover {{ color: {TEXT}; border-color: {PRIMARY}; }}
    """)
    return b


def _sep():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet(f"background:{BORDER}; border:none;")
    return line


# ============================================================
#   GİRİŞ EKRANI
# ============================================================
class LoginScreen(QMainWindow):

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

        self.setWindowTitle("AraçShare — Giriş")
        self.setFixedSize(500, 720)
        self.setStyleSheet(_BASE_SS)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._giris_sayfasi())   # index 0
        self._stack.addWidget(self._kayit_sayfasi())   # index 1

        self.setCentralWidget(self._stack)
        self.__ekrani_ortala()

    # ── Giriş sayfası ───────────────────────────────────────
    def _giris_sayfasi(self):
        page = QWidget()
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(48, 60, 48, 48)
        lay.setSpacing(0)

        # Logo
        logo = QLabel("AraçShare")
        logo.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        logo.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        lay.addWidget(logo)

        sub = _lbl("Araç Paylaşım Sistemi", 14, TEXT2)
        lay.addWidget(sub)
        lay.addSpacing(36)

        # Kullanıcı adı
        lay.addWidget(_lbl("Kullanıcı Adı", 11, MUTED))
        lay.addSpacing(6)
        self._g_kuladi = _input("Kullanıcı adınızı girin")
        self._g_kuladi.returnPressed.connect(self.__giris_yap)
        lay.addWidget(self._g_kuladi)
        lay.addSpacing(16)

        # Şifre
        lay.addWidget(_lbl("Şifre", 11, MUTED))
        lay.addSpacing(6)
        self._g_sifre = _input("Şifrenizi girin", echo=True)
        self._g_sifre.returnPressed.connect(self.__giris_yap)
        lay.addWidget(self._g_sifre)
        lay.addSpacing(8)

        # Hata mesajı
        self._g_hata = QLabel("")
        self._g_hata.setFont(QFont("Segoe UI", 10))
        self._g_hata.setStyleSheet(f"color:{DANGER}; background:transparent;")
        self._g_hata.setMinimumHeight(20)
        lay.addWidget(self._g_hata)
        lay.addSpacing(8)

        # Giriş butonu
        btn_giris = _btn_primary("Giriş Yap")
        btn_giris.clicked.connect(self.__giris_yap)
        lay.addWidget(btn_giris)
        lay.addSpacing(20)

        # Ayırıcı
        ayirac = QHBoxLayout()
        ayirac.addWidget(_sep())
        ayirac.addWidget(_lbl("  veya  ", 10, MUTED))
        ayirac.addWidget(_sep())
        lay.addLayout(ayirac)
        lay.addSpacing(20)

        # Kayıt ol butonu
        btn_kayit = _btn_ghost("Hesabın yok mu? Kayıt Ol")
        btn_kayit.clicked.connect(lambda: self._stack.setCurrentIndex(1))
        lay.addWidget(btn_kayit)
        lay.addSpacing(24)

        # Demo bilgisi
        demo = _lbl("Demo: admin / ata / cem / beyto / denca  —  şifre: 1234", 10, MUTED)
        demo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        demo.setWordWrap(True)
        lay.addWidget(demo)

        lay.addStretch()
        return page

    # ── Kayıt sayfası ───────────────────────────────────────
    def _kayit_sayfasi(self):
        page = QWidget()
        lay  = QVBoxLayout(page)
        lay.setContentsMargins(48, 44, 48, 40)
        lay.setSpacing(0)

        # Başlık
        baslik = _lbl("Hesap Oluştur", 26, TEXT, bold=True)
        lay.addWidget(baslik)
        sub = _lbl("Tüm alanlar zorunludur", 12, MUTED)
        lay.addWidget(sub)
        lay.addSpacing(28)

        # Ad Soyad
        lay.addWidget(_lbl("Ad Soyad *", 11, MUTED))
        lay.addSpacing(5)
        self._r_ad = _input("Adınız ve soyadınız")
        lay.addWidget(self._r_ad)
        lay.addSpacing(12)

        # Kullanıcı adı
        lay.addWidget(_lbl("Kullanıcı Adı *", 11, MUTED))
        lay.addSpacing(5)
        self._r_kuladi = _input("Kullanıcı adı (benzersiz)")
        lay.addWidget(self._r_kuladi)
        lay.addSpacing(12)

        # Ehliyet No
        lay.addWidget(_lbl("Ehliyet No *", 11, MUTED))
        lay.addSpacing(5)
        self._r_ehl = _input("Ehliyet numaranız")
        lay.addWidget(self._r_ehl)
        lay.addSpacing(12)

        # Telefon
        lay.addWidget(_lbl("Telefon Numarası *", 11, MUTED))
        lay.addSpacing(5)
        self._r_tel = _input("05XX XXX XX XX")
        lay.addWidget(self._r_tel)
        lay.addSpacing(12)

        # Şifre
        lay.addWidget(_lbl("Şifre * (en az 4 karakter)", 11, MUTED))
        lay.addSpacing(5)
        self._r_sifre = _input("Şifre", echo=True)
        lay.addWidget(self._r_sifre)
        lay.addSpacing(12)

        # Şifre tekrar
        lay.addWidget(_lbl("Şifre Tekrar *", 11, MUTED))
        lay.addSpacing(5)
        self._r_sifre2 = _input("Şifrenizi tekrar girin", echo=True)
        self._r_sifre2.returnPressed.connect(self.__kayit_ol)
        lay.addWidget(self._r_sifre2)
        lay.addSpacing(8)

        # Mesaj alanı
        self._r_mesaj = QLabel("")
        self._r_mesaj.setFont(QFont("Segoe UI", 10))
        self._r_mesaj.setWordWrap(True)
        self._r_mesaj.setMinimumHeight(20)
        self._r_mesaj.setStyleSheet("background:transparent;")
        lay.addWidget(self._r_mesaj)
        lay.addSpacing(10)

        # Kayıt ol butonu
        btn_kayit = _btn_primary("Kayıt Ol")
        btn_kayit.clicked.connect(self.__kayit_ol)
        lay.addWidget(btn_kayit)
        lay.addSpacing(12)

        # Geri dön
        btn_geri = _btn_ghost("← Giriş Sayfasına Dön")
        btn_geri.clicked.connect(self.__kayit_sayfasi_temizle)
        lay.addWidget(btn_geri)

        lay.addStretch()
        return page

    # ── İşlemler ────────────────────────────────────────────
    def __giris_yap(self):
        kuladi = self._g_kuladi.text().strip()
        sifre  = self._g_sifre.text()

        if not kuladi or not sifre:
            self._g_hata.setText("Kullanıcı adı ve şifre boş bırakılamaz.")
            return

        ok, sonuc = self.backend.giris_yap(kuladi, sifre)
        if not ok:
            self._g_hata.setText("Kullanıcı adı veya şifre hatalı.")
            self._g_sifre.clear()
            return

        self._g_hata.setText("")
        hesap = sonuc
        if hesap.is_admin():
            self.__admin_panelini_ac(hesap)
        else:
            self.__user_panelini_ac(hesap)

    def __kayit_ol(self):
        ad      = self._r_ad.text().strip()
        kuladi  = self._r_kuladi.text().strip()
        ehl     = self._r_ehl.text().strip()
        tel     = self._r_tel.text().strip()
        sifre   = self._r_sifre.text()
        sifre2  = self._r_sifre2.text()

        # Tüm alanlar dolu mu?
        if not all([ad, kuladi, ehl, tel, sifre, sifre2]):
            self.__r_hata("Tüm alanlar doldurulmalıdır.")
            return

        # Şifreler eşleşiyor mu?
        if sifre != sifre2:
            self.__r_hata("Şifreler eşleşmiyor.")
            self._r_sifre.clear()
            self._r_sifre2.clear()
            return

        ok, sonuc = self.backend.kullanici_kayit(ad, kuladi, ehl, tel, sifre)
        if not ok:
            self.__r_hata(sonuc)
            return

        # Başarı
        yeni_id = sonuc
        self._r_mesaj.setStyleSheet(f"color:{SUCCESS}; background:transparent;")
        self._r_mesaj.setText(
            f"✓ Kayıt başarılı! ID: {yeni_id} — Şimdi giriş yapabilirsiniz."
        )
        for inp in (self._r_ad, self._r_kuladi, self._r_ehl, self._r_tel,
                    self._r_sifre, self._r_sifre2):
            inp.clear()

        QTimer.singleShot(1800, self.__kayit_sayfasi_temizle)

    def __r_hata(self, mesaj):
        self._r_mesaj.setStyleSheet(f"color:{DANGER}; background:transparent;")
        self._r_mesaj.setText(f"✕  {mesaj}")

    def __kayit_sayfasi_temizle(self):
        self._r_mesaj.setText("")
        self._stack.setCurrentIndex(0)

    def __admin_panelini_ac(self, hesap):
        from ui.admin_panel import AdminPanel
        self._panel = AdminPanel(self.backend, hesap)
        self._panel.show()
        self.close()

    def __user_panelini_ac(self, hesap):
        from ui.user_panel import UserPanel
        self._panel = UserPanel(self.backend, hesap)
        self._panel.show()
        self.close()

    def __ekrani_ortala(self):
        fg = self.frameGeometry()
        fg.moveCenter(self.screen().geometry().center())
        self.move(fg.topLeft())
