# ============================================================
#   ui/admin_panel.py  —  Admin Paneli (Premium Dark UI)
# ============================================================

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QStackedWidget, QMessageBox, QComboBox, QLineEdit,
    QFormLayout, QDialog, QAbstractItemView,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient

from ui.dialogs import harita_ac

# ───── Renk Paleti ──────────────────────────────────────────
BG      = "#090d1b"
BG2     = "#0c1120"
SIDEBAR = "#070a16"
CARD    = "#0e1525"
CARD2   = "#111a2e"
PRIMARY = "#3b82f6"
PRIM2   = "#6366f1"
TEXT    = "#e2e8f0"
MUTED   = "#4a6080"
BORDER  = "#1a2540"
SUCCESS = "#22c55e"
SUCC2   = "#16a34a"
DANGER  = "#ef4444"
DANG2   = "#dc2626"
WARN    = "#f59e0b"
WARN2   = "#d97706"
PURPLE  = "#a855f7"
PURP2   = "#9333ea"

SINIF_RENK = {
    "eco":      "#16a34a",
    "standart": "#2563eb",
    "premium":  "#7c3aed",
    "vip":      "#b45309",
}

SAYFA_LISTESI = [
    ("Dashboard",         "dashboard"),
    ("Araç Yönetimi",     "araclar"),
    ("Kiralama Yönetimi", "kiralamalar"),
    ("Kullanıcılar",      "kullanicilar"),
]

_NAV_IKON = {
    "dashboard":    "⬡",
    "araclar":      "◈",
    "kiralamalar":  "≡",
    "kullanicilar": "◎",
}

_INPUT_STYLE = (
    f"QLineEdit {{ background:#111a2e; color:#e2e8f0;"
    f" border:1px solid #1a2540; border-radius:8px; padding:7px 10px; }}"
    f"QLineEdit:focus {{ border:1px solid #3b82f6; }}"
)
_COMBO_STYLE = (
    f"QComboBox {{ background:#111a2e; color:#e2e8f0;"
    f" border:1px solid #1a2540; border-radius:8px; padding:6px 10px; }}"
    f"QComboBox::drop-down {{ border:none; width:20px; }}"
    f"QAbstractItemView {{ background:#111a2e; color:#e2e8f0;"
    f" selection-background-color:#3b82f6; border:1px solid #1a2540; }}"
)


# ───── Yardımcı Fonksiyonlar ────────────────────────────────
def _lbl(text, bold=False, size=13, color=TEXT):
    l = QLabel(text)
    f = QFont("Segoe UI", size)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    l.setFont(f)
    l.setStyleSheet(f"color:{color}; background:transparent;")
    return l


def _btn(text, renk=PRIMARY, renk2=None, metin_renk="#fff", w=None):
    r2 = renk2 or renk
    b  = QPushButton(text)
    b.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
    b.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {renk}, stop:1 {r2});
            color: {metin_renk};
            border-radius: 8px;
            padding: 7px 18px;
            border: none;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {r2}, stop:1 {renk});
        }}
        QPushButton:pressed {{
            background: {r2};
        }}
    """)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    if w:
        b.setFixedWidth(w)
    return b


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


def _tablo(sutunlar):
    t = QTableWidget()
    t.setColumnCount(len(sutunlar))
    t.setHorizontalHeaderLabels(sutunlar)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.verticalHeader().setVisible(False)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setDefaultSectionSize(46)
    t.setShowGrid(False)
    t.setStyleSheet(f"""
        QTableWidget {{
            background: {CARD};
            color: {TEXT};
            border: none;
            font-size: 13px;
            outline: none;
        }}
        QTableWidget::item {{
            padding: 10px 16px;
            border-bottom: 1px solid {BORDER};
        }}
        QTableWidget::item:selected {{
            background: rgba(59,130,246,0.15);
            color: {TEXT};
        }}
        QTableWidget::item:hover {{
            background: rgba(255,255,255,0.04);
        }}
        QTableWidget::item:alternate {{
            background: {CARD2};
        }}
        QHeaderView::section {{
            background: {BG2};
            color: {MUTED};
            font-size: 10px;
            font-weight: 700;
            padding: 12px 16px;
            border: none;
            border-bottom: 1px solid {BORDER};
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        QScrollBar:vertical {{
            background: {CARD};
            width: 5px;
            border-radius: 3px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {BORDER};
            border-radius: 3px;
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{ height: 0; }}
    """)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return t


def _tablo_wrap(t):
    frame = QFrame()
    frame.setStyleSheet(
        f"QFrame {{ background:{CARD}; border-radius:14px;"
        f" border:1px solid {BORDER}; }}"
    )
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)
    lay.addWidget(t)
    return frame


# ───── Glow Kart ────────────────────────────────────────────
class GlowKart(QFrame):
    def __init__(self, glow_color, parent=None):
        super().__init__(parent)
        self._glow_color = glow_color
        eff = QGraphicsDropShadowEffect(self)
        eff.setOffset(0, 0)
        eff.setBlurRadius(14)
        eff.setColor(QColor(glow_color + "70"))
        self.setGraphicsEffect(eff)
        self._eff = eff

    def enterEvent(self, e):
        self._eff.setBlurRadius(28)
        self._eff.setColor(QColor(self._glow_color + "bb"))
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._eff.setBlurRadius(14)
        self._eff.setColor(QColor(self._glow_color + "70"))
        super().leaveEvent(e)


# ───── Admin Panel ───────────────────────────────────────────
class AdminPanel(QWidget):
    def __init__(self, backend, hesap, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.hesap   = hesap
        self.setWindowTitle("Admin Paneli")
        self.resize(1200, 760)
        self.setStyleSheet(f"color:{TEXT};")

        kok = QHBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 #07091c, stop:1 #060a13);"
            f"border-right: 1px solid {BORDER};"
        )
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(0)

        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedHeight(72)
        logo_frame.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 #0e1d42, stop:1 #070a16);"
            f"border-bottom: 1px solid {BORDER};"
        )
        logo_lay = QVBoxLayout(logo_frame)
        logo_lay.setContentsMargins(20, 0, 16, 0)
        logo_lay.setSpacing(3)
        logo_lay.addWidget(_lbl("Admin Panel", bold=True, size=14, color=TEXT))
        logo_lay.addWidget(_lbl(f"◈  {hesap.ad}", size=10, color=MUTED))
        sb_lay.addWidget(logo_frame)

        pad_top = QWidget()
        pad_top.setFixedHeight(12)
        pad_top.setStyleSheet("background:transparent;")
        sb_lay.addWidget(pad_top)

        self._nav_butonlar = []
        self._stack = QStackedWidget()
        self._stack.setAutoFillBackground(False)

        for baslik, anahtar in SAYFA_LISTESI:
            ikon = _NAV_IKON.get(anahtar, "·")
            btn  = QPushButton(f"  {ikon}   {baslik}")
            btn.setFont(QFont("Segoe UI", 12))
            btn.setFixedHeight(50)
            btn.setCheckable(True)
            btn.setStyleSheet(self.__nav_style(False))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=anahtar: self.__sayfa_gec(k))
            self._nav_butonlar.append((anahtar, btn))
            sb_lay.addWidget(btn)

            sayfa = self.__sayfa_olustur(anahtar)
            self._stack.addWidget(sayfa)

        sb_lay.addStretch()

        cikis_wrap = QWidget()
        cikis_wrap.setStyleSheet("background:transparent;")
        cw = QVBoxLayout(cikis_wrap)
        cw.setContentsMargins(16, 8, 16, 20)
        cikis_btn = _btn("→  Çıkış Yap", renk=DANGER, renk2=DANG2)
        cikis_btn.setFixedHeight(40)
        cikis_btn.clicked.connect(self.__cikis)
        cw.addWidget(cikis_btn)
        sb_lay.addWidget(cikis_wrap)

        kok.addWidget(sidebar)
        kok.addWidget(self._stack)

        self.__sayfa_gec("dashboard")

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0,  QColor("#07091b"))
        gradient.setColorAt(0.5,  QColor("#090d1c"))
        gradient.setColorAt(1.0,  QColor("#0d091a"))
        painter.fillRect(self.rect(), gradient)

    # ── Sidebar stil ─────────────────────────────────────────
    def __nav_style(self, aktif):
        if aktif:
            return (
                f"QPushButton {{"
                f"  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"    stop:0 rgba(59,130,246,0.20), stop:1 transparent);"
                f"  color: {TEXT};"
                f"  border: none;"
                f"  border-left: 3px solid {PRIMARY};"
                f"  text-align: left;"
                f"  padding-left: 20px;"
                f"  border-radius: 0px;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"    stop:0 rgba(59,130,246,0.28), stop:1 transparent);"
                f"}}"
            )
        return (
            f"QPushButton {{"
            f"  background: transparent;"
            f"  color: {MUTED};"
            f"  border: none;"
            f"  border-left: 3px solid transparent;"
            f"  text-align: left;"
            f"  padding-left: 20px;"
            f"  border-radius: 0px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background: rgba(255,255,255,0.04);"
            f"  color: {TEXT};"
            f"  border-left: 3px solid rgba(59,130,246,0.35);"
            f"}}"
        )

    def __sayfa_gec(self, anahtar):
        sayfa_sirasi = [k for _, k in SAYFA_LISTESI]
        idx = sayfa_sirasi.index(anahtar)
        self._stack.setCurrentIndex(idx)
        for i, (k, btn) in enumerate(self._nav_butonlar):
            btn.setChecked(i == idx)
            btn.setStyleSheet(self.__nav_style(i == idx))
        self.__sayfalari_yenile(anahtar)

    def __sayfa_olustur(self, anahtar):
        if anahtar == "dashboard":
            return self.__dashboard_sayfasi()
        if anahtar == "araclar":
            return self.__araclar_sayfasi()
        if anahtar == "kiralamalar":
            return self.__kiralamalar_sayfasi()
        if anahtar == "kullanicilar":
            return self.__kullanicilar_sayfasi()
        return QWidget()

    def __sayfalari_yenile(self, anahtar):
        if anahtar == "dashboard":
            self.__dashboard_yenile()
        elif anahtar == "araclar":
            self.__arac_tablosu_doldur()
        elif anahtar == "kiralamalar":
            self.__kiralama_tablosu_doldur()
        elif anahtar == "kullanicilar":
            self.__kullanici_tablosu_doldur()

    # ────────────────────────────────────────────────────────
    # DASHBOARD
    # ────────────────────────────────────────────────────────
    def __dashboard_sayfasi(self):
        self._dash_page = QWidget()
        self._dash_page.setAutoFillBackground(False)
        lay = QVBoxLayout(self._dash_page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(24)

        baslik_col = QVBoxLayout()
        baslik_col.setSpacing(3)
        baslik_col.addWidget(_lbl("Dashboard", bold=True, size=22))
        baslik_col.addWidget(_lbl("Sistem genel bakışı", size=11, color=MUTED))
        lay.addLayout(baslik_col)
        lay.addWidget(_sep())

        self._kart_satiri = QHBoxLayout()
        self._kart_satiri.setSpacing(16)
        lay.addLayout(self._kart_satiri)

        lay.addWidget(_lbl("Son Kiralamalar", bold=True, size=15))
        self._son_kirala_tbl = _tablo(
            ["#", "Araç", "Kullanıcı", "Başlangıç", "Durum", "Ücret (TL)"]
        )
        self._son_kirala_tbl.setMaximumHeight(240)
        lay.addWidget(_tablo_wrap(self._son_kirala_tbl))
        lay.addStretch()
        return self._dash_page

    def __istatistik_karti(self, baslik, deger, renk=PRIMARY, ikon="◈"):
        kart = GlowKart(renk)
        kart.setFixedHeight(124)
        kart.setStyleSheet(
            f"GlowKart {{"
            f"  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"    stop:0 {CARD}, stop:1 {CARD2});"
            f"  border-radius: 16px;"
            f"  border: 1px solid {BORDER};"
            f"}}"
            f"GlowKart:hover {{"
            f"  border: 1px solid {renk}55;"
            f"}}"
        )
        k_lay = QVBoxLayout(kart)
        k_lay.setContentsMargins(20, 16, 20, 16)
        k_lay.setSpacing(4)

        top_row = QHBoxLayout()
        top_row.addWidget(_lbl(ikon, size=17, color=renk))
        top_row.addStretch()
        k_lay.addLayout(top_row)

        k_lay.addWidget(_lbl(str(deger), bold=True, size=30, color=TEXT))
        k_lay.addWidget(_lbl(baslik, size=10, color=MUTED))
        return kart

    def __dashboard_yenile(self):
        ozet = self.backend.dashboard_verileri()

        while self._kart_satiri.count():
            item = self._kart_satiri.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        kartlar = [
            ("Toplam Araç",       ozet["toplam_arac"],              PRIMARY, "🚗"),
            ("Müsait Araç",       ozet["musait_arac"],              SUCCESS, "✓"),
            ("Kirada",            ozet["kirada_arac"],              DANGER,  "🔑"),
            ("Kullanıcılar",      ozet["toplam_kullanici"],         WARN,    "👤"),
            ("Aktif Kiralama",    ozet["aktif_kiralama"],           PURPLE,  "⚡"),
            ("Toplam Gelir (TL)", f"{ozet['toplam_gelir']:,.0f}",   SUCCESS, "₺"),
        ]
        for baslik, deger, renk, ikon in kartlar:
            self._kart_satiri.addWidget(
                self.__istatistik_karti(baslik, deger, renk, ikon)
            )

        kiralamalar = self.backend.tum_kiralamalar()[:10]
        tbl = self._son_kirala_tbl
        tbl.setRowCount(len(kiralamalar))
        for r, k in enumerate(kiralamalar):
            durum = "Aktif" if k.aktif_mi else "Tamamlandı"
            renk  = QColor(SUCCESS) if k.aktif_mi else QColor(MUTED)
            ucret = f"{k.toplam_fiyat:,.2f}" if k.toplam_fiyat else "-"
            for c, val in enumerate([
                str(k.kiralama_id), k.arac_bilgisi, k.kullanici_adi,
                k.baslangic_saati, durum, ucret
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if c == 4:
                    item.setForeground(renk)
                tbl.setItem(r, c, item)

    # ────────────────────────────────────────────────────────
    # ARAÇ YÖNETİMİ
    # ────────────────────────────────────────────────────────
    def __araclar_sayfasi(self):
        self._arac_page = QWidget()
        self._arac_page.setAutoFillBackground(False)
        lay = QVBoxLayout(self._arac_page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(20)

        baslik_row = QHBoxLayout()
        baslik_col = QVBoxLayout()
        baslik_col.setSpacing(3)
        baslik_col.addWidget(_lbl("Araç Yönetimi", bold=True, size=22))
        baslik_col.addWidget(_lbl("Filonuzu yönetin", size=11, color=MUTED))
        baslik_row.addLayout(baslik_col)
        baslik_row.addStretch()
        btn_ekle = _btn("＋  Yeni Araç", renk=SUCCESS, renk2=SUCC2)
        btn_ekle.clicked.connect(self.__arac_ekle_diyalog)
        baslik_row.addWidget(btn_ekle)
        lay.addLayout(baslik_row)
        lay.addWidget(_sep())

        self._arac_tbl = _tablo(
            ["ID", "Tür", "Marka", "Model", "Km", "Sınıf", "Vites", "Yakıt", "Puan", "Durum"]
        )
        self._arac_tbl.itemDoubleClicked.connect(self.__arac_detay_ac)
        lay.addWidget(_tablo_wrap(self._arac_tbl))

        islem_row = QHBoxLayout()
        islem_row.setSpacing(10)
        btn_durum  = _btn("⟳  Durum Değiştir",   renk=WARN,      renk2=WARN2)
        btn_sil    = _btn("✕  Sil",               renk=DANGER,    renk2=DANG2)
        btn_harita = _btn("⊕  Haritada Göster",   renk="#0f766e", renk2="#0d6460")
        btn_durum.clicked.connect(self.__arac_durum_degistir)
        btn_sil.clicked.connect(self.__arac_sil)
        btn_harita.clicked.connect(self.__arac_harita)
        islem_row.addWidget(btn_durum)
        islem_row.addWidget(btn_sil)
        islem_row.addWidget(btn_harita)
        islem_row.addStretch()
        lay.addLayout(islem_row)
        return self._arac_page

    def __arac_tablosu_doldur(self):
        araclar = self.backend.araclari_getir()
        tbl = self._arac_tbl
        tbl.setRowCount(len(araclar))
        durum_map  = {"musait": "Müsait", "kirada": "Kirada", "bakim": "Bakımda"}
        durum_renk = {"musait": SUCCESS,  "kirada": DANGER,   "bakim": WARN}
        for r, a in enumerate(araclar):
            d_str = durum_map.get(a.durum_arac, a.durum_arac)
            s_clr = SINIF_RENK.get(a.sinif, PRIMARY)
            for c, val in enumerate([
                a.arac_id, a.tur, a.marka, a.model, f"{a.kilometre:,}",
                a.sinif.upper(), a.vites, a.yakit, f"{a.puan:.1f}", d_str
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if c == 5:
                    item.setForeground(QColor(s_clr))
                if c == 9:
                    item.setForeground(QColor(durum_renk.get(a.durum_arac, TEXT)))
                tbl.setItem(r, c, item)

    def __secili_arac_id(self):
        row = self._arac_tbl.currentRow()
        return self._arac_tbl.item(row, 0).text() if row >= 0 else None

    def __arac_detay_ac(self):
        arac_id = self.__secili_arac_id()
        if not arac_id:
            return
        from ui.dialogs import AracDetayDiyalogu
        arac = next((a for a in self.backend.araclari_getir() if a.arac_id == arac_id), None)
        if arac:
            dlg = AracDetayDiyalogu(arac, self.backend, self.hesap, self)
            dlg.exec()
            self.__arac_tablosu_doldur()

    def __arac_harita(self):
        arac_id = self.__secili_arac_id()
        if not arac_id:
            QMessageBox.warning(self, "Seçim", "Bir araç seçin.")
            return
        arac = next((a for a in self.backend.araclari_getir() if a.arac_id == arac_id), None)
        if arac and arac.enlem:
            harita_ac(arac)
        else:
            QMessageBox.information(self, "Harita", "Bu araç için konum bilgisi yok.")

    def __arac_durum_degistir(self):
        arac_id = self.__secili_arac_id()
        if not arac_id:
            QMessageBox.warning(self, "Seçim", "Bir araç seçin.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Durum Değiştir")
        dlg.setMinimumWidth(280)
        dlg.setStyleSheet(f"background:{CARD}; color:{TEXT};")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)
        lay.addWidget(_lbl(f"Araç: {arac_id}", bold=True, size=13))
        combo = QComboBox()
        combo.addItems(["musait", "kirada", "bakim"])
        combo.setStyleSheet(_COMBO_STYLE)
        lay.addWidget(combo)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        ok_btn = _btn("Uygula", renk=SUCCESS, renk2=SUCC2)
        ip_btn = _btn("İptal",  renk=DANGER,  renk2=DANG2)
        ok_btn.clicked.connect(dlg.accept)
        ip_btn.clicked.connect(dlg.reject)
        btn_row.addWidget(ip_btn)
        btn_row.addWidget(ok_btn)
        lay.addLayout(btn_row)
        if dlg.exec():
            ok, msg = self.backend.arac_durum_degistir(arac_id, combo.currentText())
            if ok:
                self.__arac_tablosu_doldur()
            QMessageBox.information(self, "Sonuç", msg)

    def __arac_sil(self):
        arac_id = self.__secili_arac_id()
        if not arac_id:
            QMessageBox.warning(self, "Seçim", "Bir araç seçin.")
            return
        cevap = QMessageBox.question(
            self, "Sil", f"'{arac_id}' aracını silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if cevap == QMessageBox.StandardButton.Yes:
            ok, msg = self.backend.arac_sil(arac_id)
            if ok:
                self.__arac_tablosu_doldur()
            QMessageBox.information(self, "Sonuç", msg)

    def __arac_ekle_diyalog(self):
        from pricing import SINIF_LISTESI
        dlg = QDialog(self)
        dlg.setWindowTitle("Yeni Araç Ekle")
        dlg.setMinimumWidth(400)
        dlg.setStyleSheet(f"background:{CARD}; color:{TEXT};")
        lay = QFormLayout(dlg)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(12)
        lay.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def girdi(ph=""):
            e = QLineEdit()
            e.setPlaceholderText(ph)
            e.setStyleSheet(_INPUT_STYLE)
            return e

        def combo_w(secenekler):
            c = QComboBox()
            c.addItems(secenekler)
            c.setStyleSheet(_COMBO_STYLE)
            return c

        f_id     = girdi("A99")
        f_tur    = combo_w(["Otomobil", "SUV"])
        f_marka  = girdi("Toyota")
        f_model  = girdi("Corolla")
        f_km     = girdi("0")
        f_sinif  = combo_w(SINIF_LISTESI)
        f_vites  = combo_w(["Manuel", "Otomatik"])
        f_yakit  = combo_w(["Benzin", "Dizel", "Hibrit", "Elektrik"])
        f_koltuk = combo_w(["2", "4", "5", "7", "8"])
        f_enlem  = girdi("41.0082")
        f_boylam = girdi("28.9784")
        f_gorsel = girdi("A1.jpg  (assets/araclar/ altındaki dosya adı)")

        lay.addRow("Araç ID:",  f_id)
        lay.addRow("Tür:",      f_tur)
        lay.addRow("Marka:",    f_marka)
        lay.addRow("Model:",    f_model)
        lay.addRow("Km:",       f_km)
        lay.addRow("Sınıf:",    f_sinif)
        lay.addRow("Vites:",    f_vites)
        lay.addRow("Yakıt:",    f_yakit)
        lay.addRow("Koltuk:",   f_koltuk)
        lay.addRow("Enlem:",    f_enlem)
        lay.addRow("Boylam:",   f_boylam)
        lay.addRow("Görsel:",   f_gorsel)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        ok_btn  = _btn("Ekle",  renk=SUCCESS, renk2=SUCC2)
        ip_btn  = _btn("İptal", renk=DANGER,  renk2=DANG2)
        ok_btn.clicked.connect(dlg.accept)
        ip_btn.clicked.connect(dlg.reject)
        btn_row.addWidget(ip_btn)
        btn_row.addWidget(ok_btn)
        lay.addRow(btn_row)

        if dlg.exec():
            try:
                km = int(f_km.text() or 0)
            except ValueError:
                km = 0
            try:
                enlem = float(f_enlem.text()) if f_enlem.text().strip() else None
            except ValueError:
                enlem = None
            try:
                boylam = float(f_boylam.text()) if f_boylam.text().strip() else None
            except ValueError:
                boylam = None

            ok, msg = self.backend.arac_ekle(
                f_id.text().strip(), f_tur.currentText(),
                f_marka.text().strip(), f_model.text().strip(),
                km, f_sinif.currentText(),
                vites=f_vites.currentText(), yakit=f_yakit.currentText(),
                koltuk=int(f_koltuk.currentText()),
                enlem=enlem, boylam=boylam,
                gorsel=f_gorsel.text().strip(),
            )
            if ok:
                self.__arac_tablosu_doldur()
            QMessageBox.information(self, "Sonuç", msg)

    # ────────────────────────────────────────────────────────
    # KİRALAMA YÖNETİMİ
    # ────────────────────────────────────────────────────────
    def __kiralamalar_sayfasi(self):
        self._kira_page = QWidget()
        self._kira_page.setAutoFillBackground(False)
        lay = QVBoxLayout(self._kira_page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(20)

        baslik_row = QHBoxLayout()
        baslik_col = QVBoxLayout()
        baslik_col.setSpacing(3)
        baslik_col.addWidget(_lbl("Kiralama Yönetimi", bold=True, size=22))
        baslik_col.addWidget(_lbl("Aktif ve geçmiş kiralamalar", size=11, color=MUTED))
        baslik_row.addLayout(baslik_col)
        baslik_row.addStretch()

        self._kira_filtre = QComboBox()
        self._kira_filtre.addItems(["Tümü", "Sadece Aktif", "Sadece Geçmiş"])
        self._kira_filtre.setStyleSheet(_COMBO_STYLE)
        self._kira_filtre.currentIndexChanged.connect(self.__kiralama_tablosu_doldur)
        baslik_row.addWidget(self._kira_filtre)
        lay.addLayout(baslik_row)
        lay.addWidget(_sep())

        self._kira_tbl = _tablo(
            ["#", "Araç", "Kullanıcı", "Başlangıç", "Bitiş", "Durum", "Ücret (TL)"]
        )
        lay.addWidget(_tablo_wrap(self._kira_tbl))

        islem_row = QHBoxLayout()
        islem_row.setSpacing(10)
        btn_bitir = _btn("✓  Kiralamayi Bitir", renk=SUCCESS, renk2=SUCC2)
        btn_iptal = _btn("✕  İptal Et",          renk=DANGER,  renk2=DANG2)
        btn_bitir.clicked.connect(self.__kiralama_bitir)
        btn_iptal.clicked.connect(self.__kiralama_iptal)
        islem_row.addWidget(btn_bitir)
        islem_row.addWidget(btn_iptal)
        islem_row.addStretch()
        lay.addLayout(islem_row)
        return self._kira_page

    def __kiralama_tablosu_doldur(self):
        secim = self._kira_filtre.currentIndex()
        if secim == 1:
            liste = self.backend.aktif_kiralamalar()
        else:
            liste = self.backend.tum_kiralamalar()
            if secim == 2:
                liste = [k for k in liste if not k.aktif_mi]

        tbl = self._kira_tbl
        tbl.setRowCount(len(liste))
        for r, k in enumerate(liste):
            durum = "Aktif" if k.aktif_mi else "Tamamlandı"
            renk  = QColor(SUCCESS) if k.aktif_mi else QColor(MUTED)
            ucret = f"{k.toplam_fiyat:,.2f}" if k.toplam_fiyat else "-"
            for c, val in enumerate([
                str(k.kiralama_id), k.arac_bilgisi, k.kullanici_adi,
                k.baslangic_saati, k.bitis_saati or "-", durum, ucret
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if c == 5:
                    item.setForeground(renk)
                tbl.setItem(r, c, item)

    def __secili_kiralama(self):
        row = self._kira_tbl.currentRow()
        if row < 0:
            return None, None
        kid   = int(self._kira_tbl.item(row, 0).text())
        durum = self._kira_tbl.item(row, 5).text()
        return kid, durum

    def __kiralama_bitir(self):
        kid, durum = self.__secili_kiralama()
        if kid is None:
            QMessageBox.warning(self, "Seçim", "Bir kiralama seçin.")
            return
        if durum != "Aktif":
            QMessageBox.warning(self, "Hata", "Sadece aktif kiralamalar bitirilebilir.")
            return
        arac_id = None
        for k in self.backend.aktif_kiralamalar():
            if k.kiralama_id == kid:
                arac_id = k.arac_id
                break
        if not arac_id:
            QMessageBox.warning(self, "Hata", "Aktif kiralama bulunamadı.")
            return
        ok, bilgi = self.backend.kiralama_bitir(arac_id, ek_km=0)
        if ok:
            fiyat = bilgi.get("toplam_fiyat")
            mesaj = (
                f"Kiralama tamamlandı.\nAraç: {bilgi['arac']}\n"
                f"Süre: {bilgi['dakika']} dakika\n"
                f"Ücret: {fiyat:,.2f} TL" if fiyat else "Kiralama tamamlandı."
            )
            QMessageBox.information(self, "Tamamlandı", mesaj)
            self.__kiralama_tablosu_doldur()
        else:
            QMessageBox.warning(self, "Hata", str(bilgi))

    def __kiralama_iptal(self):
        kid, _ = self.__secili_kiralama()
        if kid is None:
            QMessageBox.warning(self, "Seçim", "Bir kiralama seçin.")
            return
        cevap = QMessageBox.question(
            self, "İptal", f"#{kid} no'lu kiralamayi iptal etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if cevap == QMessageBox.StandardButton.Yes:
            ok, msg = self.backend.kiralama_iptal(kid)
            QMessageBox.information(self, "Sonuç", msg)
            if ok:
                self.__kiralama_tablosu_doldur()

    # ────────────────────────────────────────────────────────
    # KULLANICILAR
    # ────────────────────────────────────────────────────────
    def __kullanicilar_sayfasi(self):
        self._kull_page = QWidget()
        self._kull_page.setAutoFillBackground(False)
        lay = QVBoxLayout(self._kull_page)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(20)

        baslik_col = QVBoxLayout()
        baslik_col.setSpacing(3)
        baslik_col.addWidget(_lbl("Kullanıcılar", bold=True, size=22))
        baslik_col.addWidget(_lbl("Kayıtlı kullanıcı listesi", size=11, color=MUTED))
        lay.addLayout(baslik_col)
        lay.addWidget(_sep())

        # ── Kullanıcı Ekle Formu ─────────────────────────────
        form_kart = QFrame()
        form_kart.setStyleSheet(
            f"QFrame {{ background:{CARD2}; border-radius:14px; border:none; }}"
        )
        form_lay = QVBoxLayout(form_kart)
        form_lay.setContentsMargins(22, 18, 22, 18)
        form_lay.setSpacing(14)

        form_lay.addWidget(_lbl("Yeni Kullanıcı Ekle", bold=True, size=13))

        satirlar = QHBoxLayout()
        satirlar.setSpacing(12)

        def _inp(placeholder):
            e = QLineEdit()
            e.setPlaceholderText(placeholder)
            e.setStyleSheet(_INPUT_STYLE)
            e.setFixedHeight(36)
            e.setFont(QFont("Segoe UI", 11))
            return e

        self._kull_inp_id    = _inp("ID  (örn. K5)")
        self._kull_inp_ad    = _inp("Ad Soyad")
        self._kull_inp_ehl   = _inp("Ehliyet No")
        self._kull_inp_kulad = _inp("Kullanıcı Adı")
        self._kull_inp_sifre = _inp("Şifre")
        self._kull_inp_sifre.setEchoMode(QLineEdit.EchoMode.Password)

        satirlar.addWidget(self._kull_inp_id,    1)
        satirlar.addWidget(self._kull_inp_ad,    2)
        satirlar.addWidget(self._kull_inp_ehl,   1)
        satirlar.addWidget(self._kull_inp_kulad, 1)
        satirlar.addWidget(self._kull_inp_sifre, 1)

        btn_ekle = _btn("+ Ekle", renk=SUCCESS, renk2=SUCC2, w=100)
        btn_ekle.clicked.connect(self.__kullanici_ekle)
        satirlar.addWidget(btn_ekle)

        form_lay.addLayout(satirlar)

        self._kull_mesaj = QLabel("")
        self._kull_mesaj.setFont(QFont("Segoe UI", 10))
        self._kull_mesaj.setStyleSheet("background:transparent;")
        form_lay.addWidget(self._kull_mesaj)

        lay.addWidget(form_kart)

        # ── Tablo ────────────────────────────────────────────
        self._kull_tbl = _tablo(["Kullanıcı ID", "Ad Soyad", "Ehliyet No", "Telefon", "Toplam Harcama"])
        lay.addWidget(_tablo_wrap(self._kull_tbl))
        return self._kull_page

    def __kullanici_ekle(self):
        kid    = self._kull_inp_id.text().strip()
        ad     = self._kull_inp_ad.text().strip()
        ehl    = self._kull_inp_ehl.text().strip()
        kulad  = self._kull_inp_kulad.text().strip()
        sifre  = self._kull_inp_sifre.text()

        if not all([kid, ad, ehl, kulad, sifre]):
            self._kull_mesaj.setStyleSheet(f"color:{DANGER}; background:transparent;")
            self._kull_mesaj.setText("✕  Tüm alanlar doldurulmalıdır.")
            return

        ok, mesaj = self.backend.kullanici_ekle(kid, ad, ehl, kulad, sifre)
        if ok:
            self._kull_mesaj.setStyleSheet(f"color:{SUCCESS}; background:transparent;")
            self._kull_mesaj.setText(f"✓  {mesaj}")
            for inp in (self._kull_inp_id, self._kull_inp_ad,
                        self._kull_inp_ehl, self._kull_inp_kulad, self._kull_inp_sifre):
                inp.clear()
            self.__kullanici_tablosu_doldur()
        else:
            self._kull_mesaj.setStyleSheet(f"color:{DANGER}; background:transparent;")
            self._kull_mesaj.setText(f"✕  {mesaj}")

    def __kullanici_tablosu_doldur(self):
        kullanicilar = self.backend.kullanicilari_getir()
        harcamalar   = self.backend.kullanici_harcama_toplamlari()
        tbl = self._kull_tbl
        tbl.setRowCount(len(kullanicilar))
        for r, k in enumerate(kullanicilar):
            toplam = harcamalar.get(k.kullanici_id, 0)
            harcama_str = f"{toplam:,.2f} TL" if toplam else "—"
            degerler = [k.kullanici_id, k.ad, k.ehliyet_no,
                        k.telefon or "—", harcama_str]
            for c, val in enumerate(degerler):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if c == 4 and toplam:
                    item.setForeground(QColor("#10b981"))
                tbl.setItem(r, c, item)

    # ────────────────────────────────────────────────────────
    # ÇIKIŞ
    # ────────────────────────────────────────────────────────
    def __cikis(self):
        from ui.login import LoginScreen
        self._panel = LoginScreen(self.backend)
        self._panel.show()
        self.close()
