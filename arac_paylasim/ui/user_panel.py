# ============================================================
#   ui/user_panel.py  —  Kullanıcı Paneli (Premium UI v3)
# ============================================================

from PyQt6.QtCore    import Qt, QDateTime, QRectF
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QStackedWidget, QComboBox, QAbstractItemView,
    QScrollArea, QDateTimeEdit, QTextEdit, QGridLayout,
    QGraphicsDropShadowEffect, QLineEdit,
)
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QLinearGradient, QPainterPath
from ui.components import ToastNotification, EmptyStateWidget, gorsel_bul

# ── Renk Paleti ─────────────────────────────────────────────
BG      = "#f4f6ff"
SIDEBAR = "#0f172a"
CARD    = "#ffffff"
PRIMARY = "#6366f1"
PRIM2   = "#8b5cf6"
TEXT    = "#0f172a"
MUTED   = "#64748b"
BORDER  = "#e2e8f0"
SUCCESS = "#10b981"
DANGER  = "#ef4444"
WARN    = "#f59e0b"
ACCENT  = "#eef2ff"

SINIF_RENK = {
    "eco":      "#10b981",
    "standart": "#6366f1",
    "premium":  "#8b5cf6",
    "vip":      "#f59e0b",
}

SINIF_GRAD = {
    "eco":      "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #d1fae5,stop:1 #6ee7b7)",
    "standart": "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #e0e7ff,stop:1 #a5b4fc)",
    "premium":  "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ede9fe,stop:1 #c4b5fd)",
    "vip":      "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #fef3c7,stop:1 #fcd34d)",
}

SAYFA_LISTESI = [
    ("Araçlar",   "araclar"),
    ("Favoriler", "favoriler"),
    ("Kiralamam", "kiralamam"),
    ("Profil",    "profil"),
]

NAV_IKONLAR = {
    "araclar":   "🚗",
    "favoriler": "♥",
    "kiralamam": "📋",
    "profil":    "◎",
}


# ── Yardımcılar ─────────────────────────────────────────────
def _lbl(text, bold=False, size=13, color=TEXT):
    l = QLabel(text)
    f = QFont("Segoe UI", size)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    l.setFont(f)
    l.setStyleSheet(f"color:{color}; background:transparent;")
    return l


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(
        f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f"stop:0 transparent, stop:0.2 {BORDER}, stop:0.8 {BORDER}, stop:1 transparent);"
        f"border:none;"
    )
    return f


def _btn_primary(text, w=None, h=36):
    b = QPushButton(text)
    b.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
    b.setFixedHeight(h)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {PRIMARY}, stop:1 {PRIM2});
            color: #fff; border: none; border-radius: 9px; padding: 0 18px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {PRIM2}, stop:1 {PRIMARY});
        }}
        QPushButton:pressed {{ background: {PRIM2}; }}
    """)
    if w:
        b.setFixedWidth(w)
    return b


def _btn_ghost(text, w=None, h=36):
    b = QPushButton(text)
    b.setFont(QFont("Segoe UI", 10))
    b.setFixedHeight(h)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: #f1f5f9; color: {MUTED};
            border: none; border-radius: 9px; padding: 0 16px;
        }}
        QPushButton:hover {{ background: {BORDER}; color: {TEXT}; }}
    """)
    if w:
        b.setFixedWidth(w)
    return b


def _btn_danger(text, w=None, h=36):
    b = QPushButton(text)
    b.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
    b.setFixedHeight(h)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {DANGER}; color: #fff;
            border: none; border-radius: 9px; padding: 0 18px;
        }}
        QPushButton:hover {{ background: #dc2626; }}
    """)
    if w:
        b.setFixedWidth(w)
    return b


def _tablo(sutunlar):
    t = QTableWidget()
    t.setColumnCount(len(sutunlar))
    t.setHorizontalHeaderLabels(sutunlar)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.verticalHeader().setVisible(False)
    t.setAlternatingRowColors(True)
    t.setShowGrid(False)
    t.verticalHeader().setDefaultSectionSize(44)
    t.setStyleSheet(f"""
        QTableWidget {{
            background: {CARD}; color: {TEXT};
            border: 1px solid {BORDER}; border-radius: 12px;
            font-size: 13px; outline: none;
        }}
        QTableWidget::item {{ padding: 10px 14px; border-bottom: 1px solid {BORDER}; }}
        QTableWidget::item:selected {{ background: {ACCENT}; color: {PRIMARY}; }}
        QTableWidget::item:hover {{ background: #f8faff; }}
        QTableWidget::item:alternate {{ background: #f9fafb; }}
        QHeaderView::section {{
            background: #f8fafc; color: {MUTED}; font-size: 10px; font-weight: 700;
            padding: 10px 14px; border: none; border-bottom: 1px solid {BORDER};
            text-transform: uppercase;
        }}
        QScrollBar:vertical {{ background: #f1f5f9; width: 5px; border-radius: 3px; }}
        QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 3px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return t


def _scroll_style():
    return f"""
        QScrollArea {{ background: {BG}; border: none; }}
        QScrollBar:vertical {{
            background: #eef0f5; width: 5px; border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: #c7d2e0; border-radius: 3px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """


# ============================================================
#   BANNER WİDGET — Görsel + gradient overlay + yuvarlatılmış köşe
# ============================================================
class BannerWidget(QWidget):
    RADIUS = 24

    def __init__(self, pixmap, sinif, renk, durum_ok, parent=None):
        super().__init__(parent)
        self._pixmap  = pixmap
        self._zoom    = 1.0
        self.setFixedHeight(175)

        if pixmap and not pixmap.isNull():
            # Sınıf badge — sol alt
            sinif_badge = QLabel(f"  {sinif.upper()}  ", self)
            sinif_badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            sinif_badge.setStyleSheet(
                f"background:{renk}; color:#fff; border-radius:5px; padding:2px 6px;"
            )
            sinif_badge.adjustSize()
            sinif_badge.move(12, 175 - sinif_badge.height() - 12)
            sinif_badge.raise_()

            # Durum badge — sağ üst
            durum_text  = "  MÜSAİT  " if durum_ok else "  KİRADA  "
            durum_color = SUCCESS if durum_ok else DANGER
            durum_badge = QLabel(durum_text, self)
            durum_badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            durum_badge.setStyleSheet(
                f"background:{durum_color}; color:#fff; border-radius:5px; padding:2px 6px;"
            )
            durum_badge.adjustSize()
            durum_badge.move(self.width() - durum_badge.width() - 12, 12)
            durum_badge.raise_()
            self._durum_badge = durum_badge

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_durum_badge"):
            self._durum_badge.move(self.width() - self._durum_badge.width() - 12, 12)

    def set_zoom(self, z):
        self._zoom = z
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        r = self.RADIUS

        clip = QPainterPath()
        clip.moveTo(r, 0)
        clip.lineTo(w - r, 0)
        clip.arcTo(QRectF(w - 2 * r, 0, 2 * r, 2 * r), 90, -90)
        clip.lineTo(w, h)
        clip.lineTo(0, h)
        clip.lineTo(0, r)
        clip.arcTo(QRectF(0, 0, 2 * r, 2 * r), 180, -90)
        clip.closeSubpath()
        painter.setClipPath(clip)

        if self._pixmap and not self._pixmap.isNull():
            tw = int(w * self._zoom)
            th = int(h * self._zoom)
            scaled = self._pixmap.scaled(
                tw, th,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            xo = max(0, (scaled.width()  - w) // 2)
            yo = max(0, (scaled.height() - h) // 2)
            painter.drawPixmap(0, 0, scaled.copy(xo, yo, w, h))

            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0,  QColor(0, 0, 0, 0))
            grad.setColorAt(0.55, QColor(0, 0, 0, 0))
            grad.setColorAt(1.0,  QColor(0, 0, 0, 145))
            painter.fillRect(0, 0, w, h, grad)


# ============================================================
#   ARAÇ KARTI WİDGET'İ
# ============================================================
class AracKartiWidget(QFrame):
    def __init__(self, arac, on_detay=None, on_kirala=None,
                 on_fav=None, on_cikar=None, parent=None):
        super().__init__(parent)
        self.arac = arac
        self.setFixedSize(290, 385)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        sinif    = arac.sinif.lower()
        renk     = SINIF_RENK.get(sinif, PRIMARY)
        grad_bg  = SINIF_GRAD.get(sinif, f"qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {ACCENT},stop:1 #ddd6fe)")
        durum_ok = arac.musait_mi

        self.setObjectName("AracKarti")
        self.setStyleSheet(f"""
            QFrame#AracKarti {{
                background: {CARD};
                border: none;
                border-radius: {BannerWidget.RADIUS}px;
            }}
        """)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 3)
        self._shadow.setBlurRadius(14)
        self._shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(self._shadow)

        kok = QVBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        # ── Banner ──────────────────────────────────────────
        _p     = gorsel_bul(arac)
        pixmap = QPixmap(_p) if _p else None

        if pixmap and not pixmap.isNull():
            self._banner = BannerWidget(pixmap, sinif, renk, durum_ok)
            kok.addWidget(self._banner)
        else:
            self._banner = None
            banner = QFrame()
            banner.setFixedHeight(175)
            banner.setStyleSheet(
                f"background:{grad_bg}; border:none;"
                f"border-top-left-radius:{BannerWidget.RADIUS}px;"
                f"border-top-right-radius:{BannerWidget.RADIUS}px;"
            )
            b_lay = QVBoxLayout(banner)
            b_lay.setContentsMargins(18, 16, 18, 14)
            b_lay.setSpacing(4)

            nm = QLabel(f"{arac.marka} {arac.model}")
            nm.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            nm.setStyleSheet(f"color:{TEXT}; background:transparent;")
            b_lay.addWidget(nm)
            b_lay.addStretch()

            roz = QHBoxLayout()
            roz.setSpacing(6)
            sl = QLabel(f"  {arac.sinif.upper()}  ")
            sl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            sl.setStyleSheet(f"background:{renk}; color:#fff; border-radius:5px; padding:2px 6px;")
            sl.setFixedHeight(20)
            roz.addWidget(sl)
            dl = QLabel("  MÜSAİT  " if durum_ok else "  KİRADA  ")
            dl.setStyleSheet(
                f"background:{SUCCESS if durum_ok else DANGER}; color:#fff;"
                f" border-radius:5px; padding:2px 6px; font-size:9px;"
            )
            dl.setFixedHeight(20)
            roz.addWidget(dl)
            roz.addStretch()
            b_lay.addLayout(roz)
            kok.addWidget(banner)

        # ── İçerik ──────────────────────────────────────────
        icerik = QWidget()
        icerik.setStyleSheet("background:transparent;")
        ic = QVBoxLayout(icerik)
        ic.setContentsMargins(16, 12, 16, 14)
        ic.setSpacing(6)

        # Satır 1: araç adı (sol) + puan (sağ)
        r1 = QHBoxLayout()
        nm_lbl = QLabel(f"{arac.marka} {arac.model}")
        nm_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        nm_lbl.setStyleSheet(f"color:{TEXT}; background:transparent;")
        stars = "★" * round(arac.puan) + "☆" * (5 - round(arac.puan))
        puan_lbl = QLabel(f"{stars} {arac.puan:.1f}")
        puan_lbl.setFont(QFont("Segoe UI", 10))
        puan_lbl.setStyleSheet("color:#f59e0b; background:transparent;")
        r1.addWidget(nm_lbl)
        r1.addStretch()
        r1.addWidget(puan_lbl)
        ic.addLayout(r1)

        # Satır 2: chip'ler + km
        r2 = QHBoxLayout()
        r2.setSpacing(5)

        def chip(text, icon=""):
            lbl = QLabel(f"{icon} {text}" if icon else text)
            lbl.setFont(QFont("Segoe UI", 9))
            lbl.setStyleSheet(
                f"background:#f1f5f9; color:{MUTED}; border-radius:5px; padding:2px 7px;"
            )
            return lbl

        r2.addWidget(chip(arac.vites, "⚙"))
        r2.addWidget(chip(arac.yakit, "⛽"))
        r2.addStretch()
        km_lbl = QLabel(f"{arac.kilometre:,} km")
        km_lbl.setFont(QFont("Segoe UI", 9))
        km_lbl.setStyleSheet(f"color:{MUTED}; background:transparent;")
        r2.addWidget(km_lbl)
        ic.addLayout(r2)

        # Çizgi
        ic.addWidget(_sep())

        # Satır 3: fiyat (sağ hizalı, büyük)
        fiyat_row = QHBoxLayout()
        fiyat_row.addStretch()
        fiyat_l = QLabel(f"{arac.gunluk_fiyat:,.0f} TL")
        fiyat_l.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        fiyat_l.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        gun_l = QLabel("/gün")
        gun_l.setFont(QFont("Segoe UI", 10))
        gun_l.setStyleSheet(f"color:{MUTED}; background:transparent;")
        gun_l.setAlignment(Qt.AlignmentFlag.AlignBottom)
        fiyat_row.addWidget(fiyat_l)
        fiyat_row.addWidget(gun_l)
        ic.addLayout(fiyat_row)

        # Satır 4: butonlar
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        btn_detay = QPushButton("Detay")
        btn_detay.setFont(QFont("Segoe UI", 10))
        btn_detay.setFixedHeight(34)
        btn_detay.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detay.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {PRIMARY};
                border: 1.5px solid {PRIMARY}; border-radius: 8px; padding: 0 12px;
            }}
            QPushButton:hover {{ background: {ACCENT}; }}
        """)
        if on_detay:
            btn_detay.clicked.connect(lambda: on_detay(arac))
        btn_row.addWidget(btn_detay)

        if durum_ok and on_kirala:
            btn_kirala = QPushButton("Kirala")
            btn_kirala.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            btn_kirala.setFixedHeight(34)
            btn_kirala.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_kirala.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {PRIMARY}, stop:1 {PRIM2});
                    color: #fff; border: none; border-radius: 8px; padding: 0 14px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {PRIM2}, stop:1 {PRIMARY});
                }}
            """)
            btn_kirala.clicked.connect(lambda: on_kirala(arac))
            btn_row.addWidget(btn_kirala)

        # Favoriden çıkar butonu (favoriler sayfasında)
        if on_cikar:
            btn_cikar = QPushButton("✕")
            btn_cikar.setFont(QFont("Segoe UI", 11))
            btn_cikar.setFixedSize(34, 34)
            btn_cikar.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_cikar.setStyleSheet(f"""
                QPushButton {{
                    background: #fff0f0; color: {DANGER};
                    border: 1.5px solid #fecaca; border-radius: 8px;
                }}
                QPushButton:hover {{
                    background: {DANGER}; color: #fff;
                }}
            """)
            btn_cikar.setToolTip("Favoriden Çıkar")
            btn_cikar.clicked.connect(lambda: on_cikar(arac))
            btn_row.addWidget(btn_cikar)
        elif on_fav:
            btn_fav = QPushButton("♥")
            btn_fav.setFont(QFont("Segoe UI", 12))
            btn_fav.setFixedSize(34, 34)
            btn_fav.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_fav.setStyleSheet(f"""
                QPushButton {{
                    background: #fff0f0; color: {DANGER};
                    border: 1.5px solid #fecaca; border-radius: 8px;
                }}
                QPushButton:hover {{
                    background: #fee2e2; border-color: {DANGER};
                }}
            """)
            btn_fav.clicked.connect(lambda: on_fav(arac))
            btn_row.addWidget(btn_fav)

        ic.addLayout(btn_row)
        kok.addWidget(icerik)

    def enterEvent(self, event):
        self._shadow.setOffset(0, 7)
        self._shadow.setBlurRadius(26)
        self._shadow.setColor(QColor(99, 102, 241, 50))
        if self._banner:
            self._banner.set_zoom(1.06)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._shadow.setOffset(0, 3)
        self._shadow.setBlurRadius(14)
        self._shadow.setColor(QColor(0, 0, 0, 30))
        if self._banner:
            self._banner.set_zoom(1.0)
        super().leaveEvent(event)


# ============================================================
#   KULLANICI PANELİ
# ============================================================
class UserPanel(QWidget):
    def __init__(self, backend, hesap, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.hesap   = hesap

        self.kullanici = next(
            (k for k in backend.kullanicilari_getir()
             if k.kullanici_id == hesap.kullanici_id),
            None
        )

        self.setWindowTitle(f"AraçShare — {hesap.ad}")
        self.resize(1200, 760)
        self.setStyleSheet(f"background:{BG}; color:{TEXT};")

        kok = QHBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        kok.addWidget(self.__sidebar_olustur())

        self._stack = QStackedWidget()
        for _, anahtar in SAYFA_LISTESI:
            self._stack.addWidget(self.__sayfa_olustur(anahtar))

        self._kiralama_araci = None
        self._kiralama_sayfasi_widget = self.__kiralama_sayfasi_olustur()
        self._stack.addWidget(self._kiralama_sayfasi_widget)

        kok.addWidget(self._stack)
        self.__sayfa_gec("araclar")

    # ── Sidebar ─────────────────────────────────────────────
    def __sidebar_olustur(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 #111827, stop:1 #0d1220);"
            "border: none;"
        )
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(0)

        # Logo
        logo_w = QFrame()
        logo_w.setFixedHeight(66)
        logo_w.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {PRIMARY}, stop:1 {PRIM2});"
        )
        logo_lay = QHBoxLayout(logo_w)
        logo_lay.setContentsMargins(20, 0, 20, 0)
        logo_lbl = QLabel("AraçShare")
        logo_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo_lbl.setStyleSheet("color:#fff; background:transparent;")
        logo_lay.addWidget(logo_lbl)
        sb_lay.addWidget(logo_w)

        # Kullanıcı alanı
        av_w = QFrame()
        av_w.setFixedHeight(78)
        av_w.setStyleSheet("background: transparent; border: none;")
        av_lay = QHBoxLayout(av_w)
        av_lay.setContentsMargins(18, 14, 18, 14)
        av_lay.setSpacing(12)

        initials = "".join(w[0].upper() for w in self.hesap.ad.split()[:2])
        av_circle = QLabel(initials)
        av_circle.setFixedSize(38, 38)
        av_circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av_circle.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        av_circle.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {PRIMARY}, stop:1 {PRIM2});"
            f"color:#fff; border-radius:19px;"
        )
        av_lay.addWidget(av_circle)

        info_w = QWidget()
        info_w.setStyleSheet("background:transparent;")
        info_v = QVBoxLayout(info_w)
        info_v.setContentsMargins(0, 0, 0, 0)
        info_v.setSpacing(1)
        ad_lbl = QLabel(self.hesap.ad)
        ad_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        ad_lbl.setStyleSheet("color:#f1f5f9; background:transparent;")
        rol_lbl = QLabel("Kullanıcı")
        rol_lbl.setFont(QFont("Segoe UI", 9))
        rol_lbl.setStyleSheet("color:#475569; background:transparent;")
        info_v.addWidget(ad_lbl)
        info_v.addWidget(rol_lbl)
        av_lay.addWidget(info_w)
        av_lay.addStretch()
        sb_lay.addWidget(av_w)

        pad = QWidget()
        pad.setFixedHeight(8)
        pad.setStyleSheet("background:transparent;")
        sb_lay.addWidget(pad)

        # Nav butonlar
        self._nav_butonlar = []
        for baslik, anahtar in SAYFA_LISTESI:
            ikon = NAV_IKONLAR.get(anahtar, "·")
            btn  = QPushButton(f"  {ikon}   {baslik}")
            btn.setFont(QFont("Segoe UI", 11))
            btn.setFixedHeight(48)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self.__nav_style(False))
            btn.clicked.connect(lambda checked, k=anahtar: self.__sayfa_gec(k))
            self._nav_butonlar.append((anahtar, btn))
            sb_lay.addWidget(btn)

        sb_lay.addStretch()

        cikis_wrap = QWidget()
        cikis_wrap.setStyleSheet("background:transparent;")
        cw = QVBoxLayout(cikis_wrap)
        cw.setContentsMargins(14, 8, 14, 20)
        cikis_btn = QPushButton("→  Çıkış Yap")
        cikis_btn.setFont(QFont("Segoe UI", 10))
        cikis_btn.setFixedHeight(38)
        cikis_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cikis_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1e293b; color: #64748b;
                border: 1px solid #334155; border-radius: 8px;
                text-align: left; padding-left: 14px;
            }}
            QPushButton:hover {{
                background: {DANGER}; color: #fff; border-color: {DANGER};
            }}
        """)
        cikis_btn.clicked.connect(self.__cikis)
        cw.addWidget(cikis_btn)
        sb_lay.addWidget(cikis_wrap)
        return sidebar

    def __nav_style(self, aktif):
        if aktif:
            return (
                f"QPushButton {{"
                f"  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"    stop:0 rgba(99,102,241,0.20), stop:1 transparent);"
                f"  color: #e2e8f0; border: none;"
                f"  border-left: 3px solid {PRIMARY};"
                f"  text-align: left; padding-left: 18px; border-radius: 0px;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"    stop:0 rgba(99,102,241,0.28), stop:1 transparent);"
                f"}}"
            )
        return (
            f"QPushButton {{"
            f"  background: transparent; color: #475569; border: none;"
            f"  border-left: 3px solid transparent;"
            f"  text-align: left; padding-left: 18px; border-radius: 0px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background: rgba(255,255,255,0.05); color: #94a3b8;"
            f"  border-left: 3px solid rgba(99,102,241,0.35);"
            f"}}"
        )

    def __sayfa_gec(self, anahtar):
        if anahtar == "kiralama":
            self._stack.setCurrentIndex(4)
            for _, btn in self._nav_butonlar:
                btn.setChecked(False)
                btn.setStyleSheet(self.__nav_style(False))
            return
        sirasi = [k for _, k in SAYFA_LISTESI]
        idx = sirasi.index(anahtar)
        self._stack.setCurrentIndex(idx)
        for i, (k, btn) in enumerate(self._nav_butonlar):
            btn.setChecked(i == idx)
            btn.setStyleSheet(self.__nav_style(i == idx))
        self.__sayfalari_yenile(anahtar)

    def __sayfa_olustur(self, anahtar):
        if anahtar == "araclar":
            return self.__araclar_sayfasi()
        if anahtar == "favoriler":
            return self.__favoriler_sayfasi()
        if anahtar == "kiralamam":
            return self.__kiralamam_sayfasi()
        if anahtar == "profil":
            return self.__profil_sayfasi()
        return QWidget()

    def __sayfalari_yenile(self, anahtar):
        if anahtar == "araclar":
            self.__kart_grid_yenile()
        elif anahtar == "favoriler":
            self.__favori_grid_yenile()
        elif anahtar == "kiralamam":
            self.__kiralama_tablosu_doldur()

    def __sayfa_baslik(self, lay, baslik, alt=""):
        b = QLabel(baslik)
        b.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        b.setStyleSheet(f"color:{TEXT}; background:transparent;")
        lay.addWidget(b)
        if alt:
            a = QLabel(alt)
            a.setFont(QFont("Segoe UI", 11))
            a.setStyleSheet(f"color:{MUTED}; background:transparent;")
            lay.addWidget(a)

    # ────────────────────────────────────────────────────────
    # ARAÇLAR — HERO + FİLTRE + KART GRİDİ
    # ────────────────────────────────────────────────────────
    def __araclar_sayfasi(self):
        self._arac_page = QWidget()
        self._arac_page.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(self._arac_page)
        lay.setContentsMargins(30, 24, 30, 16)
        lay.setSpacing(16)

        # ── Hero (sade, kutu yok) ────────────────────────────
        hero = QFrame()
        hero.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #eef2ff, stop:1 #faf5ff);"
            f"border: none; border-radius: 18px;"
        )
        hero_lay = QHBoxLayout(hero)
        hero_lay.setContentsMargins(28, 22, 28, 22)
        hero_lay.setSpacing(0)

        # Sol: başlık + açıklama
        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        h_title = QLabel("Araçlar")
        h_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        h_title.setStyleSheet(f"color:{TEXT}; background:transparent;")
        h_sub = QLabel("Size en uygun aracı keşfedin ve hemen kiralayın.")
        h_sub.setFont(QFont("Segoe UI", 11))
        h_sub.setStyleSheet(f"color:{MUTED}; background:transparent;")
        left_col.addWidget(h_title)
        left_col.addWidget(h_sub)
        hero_lay.addLayout(left_col, 1)

        # Dikey ayraç
        vdiv = QFrame()
        vdiv.setFrameShape(QFrame.Shape.VLine)
        vdiv.setFixedWidth(1)
        vdiv.setStyleSheet("background:#ddd6fe; border:none;")
        hero_lay.addSpacing(24)
        hero_lay.addWidget(vdiv)
        hero_lay.addSpacing(24)

        # Sağ: istatistikler (kutu yok, sadece sayı + etiket)
        stats_lay = QHBoxLayout()
        stats_lay.setSpacing(32)

        def stat_item(number_placeholder, label):
            col = QVBoxLayout()
            col.setSpacing(1)
            num_lbl = QLabel(number_placeholder)
            num_lbl.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
            num_lbl.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
            num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cap_lbl = QLabel(label)
            cap_lbl.setFont(QFont("Segoe UI", 10))
            cap_lbl.setStyleSheet(f"color:{MUTED}; background:transparent;")
            cap_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(num_lbl)
            col.addWidget(cap_lbl)
            return col, num_lbl

        col1, self._stat_toplam  = stat_item("—", "Toplam Araç")
        col2, self._stat_musait  = stat_item("—", "Müsait")
        col3, self._stat_premium = stat_item("—", "Premium")

        # stat sütunları arasına ince çizgi
        def mini_div():
            d = QFrame()
            d.setFrameShape(QFrame.Shape.VLine)
            d.setStyleSheet("background:#ddd6fe; border:none;")
            d.setFixedWidth(1)
            d.setFixedHeight(36)
            w = QWidget()
            wl = QHBoxLayout(w)
            wl.setContentsMargins(0, 0, 0, 0)
            wl.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            wl.addWidget(d)
            return w

        stats_lay.addLayout(col1)
        stats_lay.addWidget(mini_div())
        stats_lay.addLayout(col2)
        stats_lay.addWidget(mini_div())
        stats_lay.addLayout(col3)
        hero_lay.addLayout(stats_lay)

        lay.addWidget(hero)

        # ── Filtre Bar ──────────────────────────────────────
        filtre = QFrame()
        filtre.setStyleSheet(
            f"background:{CARD}; border: none; border-radius: 14px;"
        )
        f_lay = QHBoxLayout(filtre)
        f_lay.setContentsMargins(18, 11, 18, 11)
        f_lay.setSpacing(10)

        _cs = (
            f"QComboBox {{ background:#f8fafc; color:{TEXT};"
            f" border: 1px solid {BORDER}; border-radius: 10px;"
            f" padding: 6px 12px; min-width: 115px; }}"
            f"QComboBox:focus {{ border-color: {PRIMARY}; }}"
            f"QComboBox::drop-down {{ border: none; width: 16px; }}"
            f"QAbstractItemView {{ background:{CARD}; color:{TEXT};"
            f" selection-background-color:{ACCENT}; border: 1px solid {BORDER}; }}"
        )

        def combo_f(items, ph):
            c = QComboBox()
            c.addItem(ph)
            c.addItems(items)
            c.setFont(QFont("Segoe UI", 10))
            c.setStyleSheet(_cs)
            return c

        self._f_sinif  = combo_f(["eco", "standart", "premium", "vip"], "Tüm Sınıflar")
        self._f_vites  = combo_f(["Manuel", "Otomatik"], "Tüm Vitesler")
        self._f_yakit  = combo_f(["Benzin", "Dizel", "Hibrit", "Elektrik"], "Tüm Yakıtlar")
        self._f_sadece = QComboBox()
        self._f_sadece.addItems(["Sadece Müsait", "Tüm Araçlar"])
        self._f_sadece.setFont(QFont("Segoe UI", 10))
        self._f_sadece.setStyleSheet(_cs)

        btn_filtrele = _btn_primary("Filtrele", h=36)
        btn_filtrele.clicked.connect(self.__kart_grid_yenile)
        btn_sifirla  = _btn_ghost("Sıfırla", h=36)
        btn_sifirla.clicked.connect(self.__filtre_sifirla)

        f_lay.addWidget(self._f_sinif)
        f_lay.addWidget(self._f_vites)
        f_lay.addWidget(self._f_yakit)
        f_lay.addWidget(self._f_sadece)
        f_lay.addWidget(btn_filtrele)
        f_lay.addWidget(btn_sifirla)
        f_lay.addStretch()
        lay.addWidget(filtre)

        # ── Scroll + Grid ───────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(_scroll_style())

        self._kart_konteyner = QWidget()
        self._kart_konteyner.setStyleSheet(f"background:{BG};")
        self._kart_grid = QGridLayout(self._kart_konteyner)
        self._kart_grid.setContentsMargins(2, 8, 2, 8)
        self._kart_grid.setSpacing(20)

        scroll.setWidget(self._kart_konteyner)
        lay.addWidget(scroll)
        return self._arac_page

    def __filtre_sifirla(self):
        self._f_sinif.setCurrentIndex(0)
        self._f_vites.setCurrentIndex(0)
        self._f_yakit.setCurrentIndex(0)
        self._f_sadece.setCurrentIndex(0)
        self.__kart_grid_yenile()

    def __kart_grid_yenile(self):
        sinif  = self._f_sinif.currentText()  if self._f_sinif.currentIndex()  > 0 else None
        vites  = self._f_vites.currentText()  if self._f_vites.currentIndex()  > 0 else None
        yakit  = self._f_yakit.currentText()  if self._f_yakit.currentIndex()  > 0 else None
        sadece = self._f_sadece.currentIndex() == 0

        araclar = self.backend.araclari_filtrele(
            sinif=sinif, vites=vites, yakit=yakit, sadece_musait=sadece
        )

        # Hero istatistikleri güncelle (kutu yok, sadece label)
        tum = self.backend.araclari_getir()
        self._stat_toplam.setText(str(len(tum)))
        self._stat_musait.setText(str(len([a for a in tum if a.musait_mi])))
        self._stat_premium.setText(str(len([a for a in tum if a.sinif in ("premium", "vip")])))

        while self._kart_grid.count():
            item = self._kart_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = 3
        for i, arac in enumerate(araclar):
            kart = AracKartiWidget(
                arac,
                on_detay=self.__arac_detay_ac_dogrudan,
                on_kirala=self.__kiralamayi_ac,
                on_fav=self.__hizli_favori_toggle,
            )
            self._kart_grid.addWidget(kart, i // cols, i % cols)

        if not araclar:
            bos = EmptyStateWidget(
                "🔍", "Araç Bulunamadı",
                "Filtre kriterlerinizi değiştirin veya sıfırlayın."
            )
            self._kart_grid.addWidget(bos, 0, 0, 1, cols)

    def __arac_detay_ac_dogrudan(self, arac):
        from ui.dialogs import AracDetayDiyalogu
        dlg = AracDetayDiyalogu(arac, self.backend, self.hesap, self)
        sonuc = dlg.exec()
        if sonuc == AracDetayDiyalogu.KIRALA_CODE:
            self.__kiralamayi_ac(arac)
        else:
            self.__kart_grid_yenile()

    def __hizli_favori_toggle(self, arac):
        ok, msg = self.backend.favori_toggle(self.hesap.kullanici_id, arac.arac_id)
        kind = "success" if ok else "error"
        self._toast(msg, kind=kind)

    def __arac_harita(self, arac):
        from ui.dialogs import harita_ac
        if arac.enlem:
            harita_ac(arac)
        else:
            self._toast("Bu araç için konum bilgisi bulunmamaktadır.", kind="info")

    # ────────────────────────────────────────────────────────
    # FAVORİLER — Kart grid (tablo değil)
    # ────────────────────────────────────────────────────────
    def __favoriler_sayfasi(self):
        self._fav_page = QWidget()
        self._fav_page.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(self._fav_page)
        lay.setContentsMargins(30, 24, 30, 16)
        lay.setSpacing(16)

        self.__sayfa_baslik(lay, "Favorilerim", "Kaydettiğiniz araçlar")
        lay.addWidget(_sep())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(_scroll_style())

        self._fav_konteyner = QWidget()
        self._fav_konteyner.setStyleSheet(f"background:{BG};")
        self._fav_grid = QGridLayout(self._fav_konteyner)
        self._fav_grid.setContentsMargins(2, 4, 2, 8)
        self._fav_grid.setSpacing(20)

        scroll.setWidget(self._fav_konteyner)
        lay.addWidget(scroll)
        return self._fav_page

    def __favori_grid_yenile(self):
        """Favoriler kart gridini DB'den çekilen verilerle doldurur."""
        while self._fav_grid.count():
            item = self._fav_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        araclar = self.backend.kullanici_favorileri(self.hesap.kullanici_id)

        if not araclar:
            bos = EmptyStateWidget(
                "♥", "Henüz Favori Yok",
                "Araç kartlarında ♥ butonuna tıklayarak favorilerinize ekleyebilirsiniz."
            )
            self._fav_grid.addWidget(bos, 0, 0, 1, 3)
            return

        cols = 3
        for i, arac in enumerate(araclar):
            kart = AracKartiWidget(
                arac,
                on_detay=self.__arac_detay_ac_dogrudan,
                on_kirala=self.__kiralamayi_ac,
                on_cikar=self.__favori_kaldir_ve_yenile,
            )
            self._fav_grid.addWidget(kart, i // cols, i % cols)

    def __favori_kaldir_ve_yenile(self, arac):
        self.backend.favori_kaldir(self.hesap.kullanici_id, arac.arac_id)
        self.__favori_grid_yenile()

    # ────────────────────────────────────────────────────────
    # KİRALAMAM
    # ────────────────────────────────────────────────────────
    def __kiralamam_sayfasi(self):
        self._kira_page = QWidget()
        self._kira_page.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(self._kira_page)
        lay.setContentsMargins(30, 24, 30, 16)
        lay.setSpacing(16)

        self.__sayfa_baslik(lay, "Kiralamalarım", "Geçmiş ve aktif kiralamalarınız")
        lay.addWidget(_sep())

        self._kira_tbl = _tablo(
            ["#", "Araç", "Başlangıç", "Bitiş", "Durum", "Ücret (TL)"]
        )
        lay.addWidget(self._kira_tbl)

        islem_row = QHBoxLayout()
        btn_bitir = _btn_primary("✓  Aktif Kiralamayı Bitir", h=40)
        btn_bitir.clicked.connect(self.__kiralama_bitir)
        islem_row.addWidget(btn_bitir)
        islem_row.addStretch()
        lay.addLayout(islem_row)
        return self._kira_page

    def __kiralama_tablosu_doldur(self):
        if not self.kullanici:
            return
        ok, sonuc = self.backend.kullanici_kiralama_gecmisi(self.kullanici.kullanici_id)
        if not ok:
            return
        kiralamalar = sonuc["kiralamalar"]
        tbl = self._kira_tbl
        tbl.setRowCount(len(kiralamalar))
        for r, k in enumerate(kiralamalar):
            durum = "Aktif" if k.aktif_mi else "Tamamlandı"
            renk  = QColor(SUCCESS) if k.aktif_mi else QColor(MUTED)
            ucret = f"{k.toplam_fiyat:,.2f}" if k.toplam_fiyat else "-"
            for c, val in enumerate([
                str(k.kiralama_id), k.arac_bilgisi,
                k.baslangic_saati, k.bitis_saati or "-",
                durum, ucret
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if c == 4:
                    item.setForeground(renk)
                tbl.setItem(r, c, item)

    def __kiralama_bitir(self):
        if not self.kullanici:
            return
        aktifler = self.backend.aktif_kiralamalar()
        benim = [k for k in aktifler if k.kullanici_id == self.kullanici.kullanici_id]
        if not benim:
            self._toast(
                "Aktif bir kiralamanız bulunmamaktadır.",
                kind="info", title="Bilgi"
            )
            return
        k = benim[0]
        ok, bilgi = self.backend.kiralama_bitir(k.arac_id, ek_km=0)
        if ok:
            fiyat = bilgi.get("toplam_fiyat")
            if fiyat:
                self._toast(
                    f"{bilgi['arac']} · {bilgi['dakika']} dk · {fiyat:,.2f} TL",
                    kind="success", title="Kiralama Tamamlandı"
                )
            else:
                self._toast("Kiralama başarıyla tamamlandı.", kind="success")
            self.__kiralama_tablosu_doldur()
        else:
            self._toast(str(bilgi), kind="error", title="İşlem Başarısız")

    # ────────────────────────────────────────────────────────
    # PROFİL
    # ────────────────────────────────────────────────────────
    def __profil_sayfasi(self):
        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(30, 24, 30, 16)
        lay.setSpacing(16)

        self.__sayfa_baslik(lay, "Profilim")
        lay.addWidget(_sep())

        kart = QFrame()
        kart.setStyleSheet(
            f"background:{CARD}; border: none; border-radius: 18px;"
        )
        k_lay = QVBoxLayout(kart)
        k_lay.setContentsMargins(36, 32, 36, 32)
        k_lay.setSpacing(12)

        if self.kullanici:
            def satir(anahtar, deger):
                row = QFrame()
                row.setStyleSheet(
                    f"background:#f8fafc; border-radius:10px; border:1px solid {BORDER};"
                )
                r_lay = QHBoxLayout(row)
                r_lay.setContentsMargins(16, 12, 16, 12)
                k_lbl = QLabel(anahtar)
                k_lbl.setFont(QFont("Segoe UI", 10))
                k_lbl.setStyleSheet(f"color:{MUTED}; background:transparent;")
                k_lbl.setFixedWidth(140)
                v_lbl = QLabel(deger)
                v_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                v_lbl.setStyleSheet(f"color:{TEXT}; background:transparent;")
                r_lay.addWidget(k_lbl)
                r_lay.addWidget(v_lbl)
                r_lay.addStretch()
                k_lay.addWidget(row)

            satir("Ad Soyad:",      self.kullanici.ad)
            satir("Kullanıcı ID:",  self.kullanici.kullanici_id)
            satir("Ehliyet No:",    self.kullanici.ehliyet_no)
            satir("Kullanıcı Adı:", self.hesap.kullanici_adi)
            satir("Rol:",           self.hesap.rol.capitalize())

            # Telefon — düzenlenebilir satır
            tel_row = QFrame()
            tel_row.setStyleSheet(
                f"background:#f8fafc; border-radius:10px; border:1px solid {BORDER};"
            )
            tel_r_lay = QHBoxLayout(tel_row)
            tel_r_lay.setContentsMargins(16, 8, 8, 8)
            tel_r_lay.setSpacing(8)

            tel_k_lbl = QLabel("Telefon:")
            tel_k_lbl.setFont(QFont("Segoe UI", 10))
            tel_k_lbl.setStyleSheet(f"color:{MUTED}; background:transparent;")
            tel_k_lbl.setFixedWidth(140)

            self._tel_input = QLineEdit(self.kullanici.telefon or "")
            self._tel_input.setPlaceholderText("05XX XXX XX XX")
            self._tel_input.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            self._tel_input.setStyleSheet(
                f"background:transparent; border:none; color:{TEXT}; padding:4px 0;"
            )
            self._tel_input.returnPressed.connect(self.__telefon_guncelle)

            btn_tel = _btn_primary("Güncelle", w=90, h=32)
            btn_tel.clicked.connect(self.__telefon_guncelle)

            tel_r_lay.addWidget(tel_k_lbl)
            tel_r_lay.addWidget(self._tel_input, 1)
            tel_r_lay.addWidget(btn_tel)
            k_lay.addWidget(tel_row)

        lay.addWidget(kart)
        lay.addStretch()
        return page

    # ────────────────────────────────────────────────────────
    # KİRALAMA SAYFASI (Stack index 4)
    # ────────────────────────────────────────────────────────
    def __kiralamayi_ac(self, arac):
        self._kiralama_araci = arac
        self.__kiralama_sayfasi_doldur(arac)
        self.__sayfa_gec("kiralama")

    def __kiralama_sayfasi_olustur(self):
        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(16)

        geri_btn = _btn_ghost("← Geri", w=90, h=34)
        geri_btn.clicked.connect(lambda: self.__sayfa_gec("araclar"))
        lay.addWidget(geri_btn)

        self._kira_bilgi_kart = QFrame()
        self._kira_bilgi_kart.setStyleSheet(
            f"background:{CARD}; border: none; border-radius: 16px;"
        )
        self._kira_bilgi_lay = QVBoxLayout(self._kira_bilgi_kart)
        self._kira_bilgi_lay.setContentsMargins(28, 22, 28, 22)
        self._kira_bilgi_lay.setSpacing(12)
        lay.addWidget(self._kira_bilgi_kart)

        alt_row = QHBoxLayout()
        alt_row.setSpacing(16)

        tarih_kart = QFrame()
        tarih_kart.setStyleSheet(
            f"background:{CARD}; border: none; border-radius: 16px;"
        )
        tarih_lay = QVBoxLayout(tarih_kart)
        tarih_lay.setContentsMargins(22, 18, 22, 18)
        tarih_lay.setSpacing(12)

        t_baslik = QLabel("Kiralama Zamanı")
        t_baslik.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        t_baslik.setStyleSheet(f"color:{TEXT}; background:transparent;")
        tarih_lay.addWidget(t_baslik)
        tarih_lay.addWidget(_sep())

        _dt_style = (
            f"QDateTimeEdit {{ background:{BG}; border: 1px solid {BORDER};"
            f" border-radius: 10px; padding: 7px 12px; font-size: 12px; color:{TEXT}; }}"
            f"QDateTimeEdit:focus {{ border-color: {PRIMARY}; }}"
        )

        tarih_lay.addWidget(_lbl("Başlangıç:", size=11, color=MUTED))
        self._kira_bas_dt = QDateTimeEdit(QDateTime.currentDateTime())
        self._kira_bas_dt.setDisplayFormat("dd.MM.yyyy  HH:mm")
        self._kira_bas_dt.setCalendarPopup(True)
        self._kira_bas_dt.setMinimumDateTime(QDateTime.currentDateTime())
        self._kira_bas_dt.setFont(QFont("Segoe UI", 12))
        self._kira_bas_dt.setStyleSheet(_dt_style)
        self._kira_bas_dt.dateTimeChanged.connect(self.__kira_fiyat_guncelle)
        tarih_lay.addWidget(self._kira_bas_dt)

        tarih_lay.addWidget(_lbl("Bitiş:", size=11, color=MUTED))
        self._kira_bit_dt = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))
        self._kira_bit_dt.setDisplayFormat("dd.MM.yyyy  HH:mm")
        self._kira_bit_dt.setCalendarPopup(True)
        self._kira_bit_dt.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))
        self._kira_bit_dt.setFont(QFont("Segoe UI", 12))
        self._kira_bit_dt.setStyleSheet(_dt_style)
        self._kira_bit_dt.dateTimeChanged.connect(self.__kira_fiyat_guncelle)
        tarih_lay.addWidget(self._kira_bit_dt)
        alt_row.addWidget(tarih_kart, 1)

        fiyat_kart = QFrame()
        fiyat_kart.setStyleSheet(
            f"background:{CARD}; border: none; border-radius: 16px;"
        )
        fiyat_lay = QVBoxLayout(fiyat_kart)
        fiyat_lay.setContentsMargins(22, 18, 22, 18)
        fiyat_lay.setSpacing(12)

        f_baslik = QLabel("Fiyat Özeti")
        f_baslik.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        f_baslik.setStyleSheet(f"color:{TEXT}; background:transparent;")
        fiyat_lay.addWidget(f_baslik)
        fiyat_lay.addWidget(_sep())

        self._kira_fiyat_txt = QTextEdit()
        self._kira_fiyat_txt.setReadOnly(True)
        self._kira_fiyat_txt.setFont(QFont("Consolas", 11))
        self._kira_fiyat_txt.setMinimumHeight(160)
        self._kira_fiyat_txt.setStyleSheet(
            f"background:{ACCENT}; border: none;"
            f" border-radius: 10px; padding: 12px; color:{TEXT};"
        )
        fiyat_lay.addWidget(self._kira_fiyat_txt)
        alt_row.addWidget(fiyat_kart, 1)
        lay.addLayout(alt_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.setSpacing(12)

        vazgec_btn = _btn_ghost("Vazgeç", w=110, h=42)
        vazgec_btn.clicked.connect(lambda: self.__sayfa_gec("araclar"))

        self._kira_onayla_btn = _btn_primary("Kiralamayı Onayla", h=42)
        self._kira_onayla_btn.setFixedWidth(190)
        self._kira_onayla_btn.clicked.connect(self.__kiralama_onayla)

        btn_row.addWidget(vazgec_btn)
        btn_row.addWidget(self._kira_onayla_btn)
        lay.addLayout(btn_row)
        lay.addStretch()
        return page

    def __kiralama_sayfasi_doldur(self, arac):
        while self._kira_bilgi_lay.count():
            item = self._kira_bilgi_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sinif_renk = SINIF_RENK.get(arac.sinif, PRIMARY)
        from pricing import SINIF_FIYAT

        baslik_row = QHBoxLayout()
        baslik_lbl = QLabel(f"{arac.marka} {arac.model}")
        baslik_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        baslik_lbl.setStyleSheet(f"color:{TEXT}; background:transparent;")
        sinif_lbl = QLabel(f"  {arac.sinif.upper()}  ")
        sinif_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        sinif_lbl.setStyleSheet(
            f"background:{sinif_renk}; color:#fff; border-radius:8px; padding:2px 8px;"
        )
        sinif_lbl.setFixedHeight(26)
        baslik_row.addWidget(baslik_lbl)
        baslik_row.addWidget(sinif_lbl)
        baslik_row.addStretch()
        self._kira_bilgi_lay.addLayout(baslik_row)

        grid_lay = QHBoxLayout()
        grid_lay.setSpacing(28)

        def bilgi_blok(anahtar, deger, renk=TEXT):
            w = QWidget()
            v = QVBoxLayout(w)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(2)
            k = QLabel(anahtar)
            k.setFont(QFont("Segoe UI", 10))
            k.setStyleSheet(f"color:{MUTED}; background:transparent;")
            d = QLabel(deger)
            d.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            d.setStyleSheet(f"color:{renk}; background:transparent;")
            v.addWidget(k)
            v.addWidget(d)
            return w

        saatlik = SINIF_FIYAT.get(arac.sinif, 0)
        gunluk  = saatlik * 24
        grid_lay.addWidget(bilgi_blok("Tür",       arac.tur))
        grid_lay.addWidget(bilgi_blok("Vites",     arac.vites))
        grid_lay.addWidget(bilgi_blok("Yakıt",     arac.yakit))
        grid_lay.addWidget(bilgi_blok("Koltuk",    str(arac.koltuk)))
        grid_lay.addWidget(bilgi_blok("Kilometre", f"{arac.kilometre:,} km"))
        grid_lay.addWidget(bilgi_blok("Saatlik",   f"{saatlik:,} TL", renk=PRIMARY))
        grid_lay.addWidget(bilgi_blok("Günlük",    f"{gunluk:,} TL",  renk=PRIMARY))
        grid_lay.addStretch()
        self._kira_bilgi_lay.addLayout(grid_lay)

        now = QDateTime.currentDateTime()
        self._kira_bas_dt.setDateTime(now)
        self._kira_bit_dt.setDateTime(now.addSecs(3600))
        self._kira_bas_dt.setMinimumDateTime(now)
        self._kira_bit_dt.setMinimumDateTime(now.addSecs(60))
        self.__kira_fiyat_guncelle()

    def __kira_fiyat_guncelle(self):
        if not self._kiralama_araci:
            return
        bas = self._kira_bas_dt.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        bit = self._kira_bit_dt.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        ok, sonuc = self.backend.fiyat_on_izle(self._kiralama_araci.sinif, bas, bit)
        if ok:
            from pricing import fiyat_ozeti
            self._kira_fiyat_txt.setPlainText(fiyat_ozeti(sonuc))
            self._kira_onayla_btn.setEnabled(True)
        else:
            self._kira_fiyat_txt.setPlainText(f"Hata: {sonuc}")
            self._kira_onayla_btn.setEnabled(False)

    def __kiralama_onayla(self):
        arac = self._kiralama_araci
        if not arac:
            return
        bas_dt = self._kira_bas_dt.dateTime()
        bit_dt = self._kira_bit_dt.dateTime()
        if bit_dt <= bas_dt:
            self._toast(
                "Bitiş zamanı başlangıçtan önce olamaz.",
                kind="warning", title="Geçersiz Tarih"
            )
            return
        sure_saat = bas_dt.secsTo(bit_dt) / 3600
        if arac.sinif == "vip" and sure_saat < 3:
            self._toast(
                f"VIP araçlar için minimum 3 saat gereklidir. "
                f"Seçilen süre: {sure_saat:.1f} saat.",
                kind="warning", title="VIP Minimum Süre"
            )
            return
        ok, bilgi = self.backend.kiralama_baslat(arac.arac_id, self.hesap.kullanici_id)
        if ok:
            self._toast(
                f"{bilgi['arac']} · {bilgi['sinif'].upper()} — İyi yolculuklar!",
                kind="success", title="Kiralama Başlatıldı",
                duration=5000
            )
            self._kiralama_araci = None
            self.__kart_grid_yenile()
            self.__kiralama_tablosu_doldur()
            self.__sayfa_gec("kiralamam")
        else:
            self._toast(str(bilgi), kind="error", title="Kiralama Başarısız")

    # ────────────────────────────────────────────────────────
    # TELEFON GÜNCELLE
    # ────────────────────────────────────────────────────────
    def __telefon_guncelle(self):
        if not self.kullanici:
            return
        yeni_tel = self._tel_input.text().strip()
        ok, mesaj = self.backend.kullanici_telefon_guncelle(
            self.kullanici.kullanici_id, yeni_tel
        )
        if ok:
            self.kullanici = next(
                (k for k in self.backend.kullanicilari_getir()
                 if k.kullanici_id == self.hesap.kullanici_id),
                self.kullanici
            )
            self._tel_input.setText(self.kullanici.telefon or "")
            self._toast(mesaj, kind="success", title="Profil Güncellendi")
        else:
            self._toast(mesaj, kind="error", title="Güncelleme Başarısız")

    # ────────────────────────────────────────────────────────
    # TOAST BİLDİRİM
    # ────────────────────────────────────────────────────────
    def _toast(self, message: str, kind: str = "info",
               title: str = None, duration: int = 3500):
        """Sağ üst köşede premium toast bildirimi gösterir."""
        if hasattr(self, "_active_toast") and self._active_toast:
            try:
                self._active_toast._dismiss()
            except RuntimeError:
                pass
        t = ToastNotification(
            message, kind=kind, title=title,
            duration=duration, parent=self
        )
        self._active_toast = t
        t.move(self.width() - ToastNotification.WIDTH - 24, 24)
        t.raise_()
        t.show()

    # ────────────────────────────────────────────────────────
    # ÇIKIŞ
    # ────────────────────────────────────────────────────────
    def __cikis(self):
        from ui.login import LoginScreen
        self._panel = LoginScreen(self.backend)
        self._panel.show()
        self.close()
