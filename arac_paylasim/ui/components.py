# ============================================================
#   ui/components.py — Paylaşımlı Premium UI Bileşenleri
# ============================================================

import os

from PyQt6.QtCore    import Qt, QTimer, QRectF
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPixmap

_ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "araclar"
)
_IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def gorsel_bul(arac) -> str | None:
    """
    Araç için görsel dosya yolunu döndürür; bulamazsa None.
    Öncelik sırası:
      1. arac.gorsel alanında kayıtlı yol (mutlak veya assets/araclar/ altı)
      2. assets/araclar/{arac_id}  (.jpg / .jpeg / .png / .webp)
    """
    if arac.gorsel:
        if os.path.isabs(arac.gorsel) and os.path.exists(arac.gorsel):
            return arac.gorsel
        p = os.path.join(_ASSETS_DIR, arac.gorsel)
        if os.path.exists(p):
            return p

    for ext in _IMG_EXTS:
        p = os.path.join(_ASSETS_DIR, f"{arac.arac_id}{ext}")
        if os.path.exists(p):
            return p

    return None

TEXT  = "#0f172a"
MUTED = "#64748b"

# ── Toast / Alert tip konfigürasyonu ────────────────────────
_CFG = {
    "success": {
        "bg":          "#f0fdf4",
        "border":      "#86efac",
        "icon_bg":     "#dcfce7",
        "icon":        "✓",
        "icon_color":  "#16a34a",
        "title_color": "#15803d",
        "text_color":  "#166534",
    },
    "error": {
        "bg":          "#fff1f2",
        "border":      "#fda4af",
        "icon_bg":     "#ffe4e6",
        "icon":        "✕",
        "icon_color":  "#dc2626",
        "title_color": "#b91c1c",
        "text_color":  "#991b1b",
    },
    "warning": {
        "bg":          "#fffbeb",
        "border":      "#fde68a",
        "icon_bg":     "#fef3c7",
        "icon":        "⚠",
        "icon_color":  "#d97706",
        "title_color": "#b45309",
        "text_color":  "#92400e",
    },
    "info": {
        "bg":          "#f0f9ff",
        "border":      "#bae6fd",
        "icon_bg":     "#e0f2fe",
        "icon":        "ℹ",
        "icon_color":  "#0284c7",
        "title_color": "#0369a1",
        "text_color":  "#075985",
    },
}


# ============================================================
#   TOAST BİLDİRİM
# ============================================================
class ToastNotification(QFrame):
    """
    Premium floating toast. Parent widget'ın üstünde konumlanır.
    duration=0 → otomatik kapanmaz.
    """

    WIDTH = 340

    def __init__(self, message: str, kind: str = "info",
                 title: str = None, duration: int = 3500, parent=None):
        super().__init__(parent)
        cfg = _CFG.get(kind, _CFG["info"])

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(self.WIDTH)
        self.setStyleSheet(
            f"QFrame {{ background:{cfg['bg']};"
            f" border:1.5px solid {cfg['border']}; border-radius:14px; }}"
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 6)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 45))
        self.setGraphicsEffect(shadow)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 14, 12, 14)
        lay.setSpacing(12)

        # İkon dairesi
        ico = QLabel(cfg["icon"])
        ico.setFixedSize(36, 36)
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        ico.setStyleSheet(
            f"background:{cfg['icon_bg']}; color:{cfg['icon_color']};"
            f" border-radius:18px; border:none;"
        )
        lay.addWidget(ico, 0, Qt.AlignmentFlag.AlignTop)

        # Metin sütunu
        col = QVBoxLayout()
        col.setSpacing(3)
        col.setContentsMargins(0, 0, 0, 0)
        if title:
            t_lbl = QLabel(title)
            t_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            t_lbl.setStyleSheet(
                f"color:{cfg['title_color']}; background:transparent; border:none;"
            )
            col.addWidget(t_lbl)
        m_lbl = QLabel(message)
        m_lbl.setFont(QFont("Segoe UI", 10))
        m_lbl.setWordWrap(True)
        m_lbl.setStyleSheet(
            f"color:{cfg['text_color']}; background:transparent; border:none;"
        )
        col.addWidget(m_lbl)
        lay.addLayout(col, 1)

        # Kapat butonu
        x_btn = QPushButton("×")
        x_btn.setFixedSize(22, 22)
        x_btn.setFont(QFont("Segoe UI", 16))
        x_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        x_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{cfg['icon_color']};"
            f" border:none; border-radius:11px; line-height:1; }}"
            f"QPushButton:hover {{ background:{cfg['icon_bg']}; }}"
        )
        x_btn.clicked.connect(self._dismiss)
        lay.addWidget(x_btn, 0, Qt.AlignmentFlag.AlignTop)

        self.adjustSize()

        if duration > 0:
            QTimer.singleShot(duration, self._dismiss)

    def _dismiss(self):
        try:
            self.hide()
            self.deleteLater()
        except RuntimeError:
            pass

    def show_at(self, parent_widget, top_offset: int = 24):
        """Parent widget içinde sağ üst köşeye konumlandır ve göster."""
        if parent_widget:
            self.move(parent_widget.width() - self.WIDTH - 24, top_offset)
        self.raise_()
        self.show()


# ============================================================
#   SATIR İÇİ ALERT KARTI
# ============================================================
class AlertCard(QFrame):
    """Sayfa içine yerleştirilebilir renkli alert kartı."""

    def __init__(self, message: str, kind: str = "info",
                 title: str = None, parent=None):
        super().__init__(parent)
        cfg = _CFG.get(kind, _CFG["info"])

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"QFrame {{ background:{cfg['bg']};"
            f" border:1.5px solid {cfg['border']}; border-radius:12px; }}"
        )

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(14)

        ico = QLabel(cfg["icon"])
        ico.setFixedSize(34, 34)
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        ico.setStyleSheet(
            f"background:{cfg['icon_bg']}; color:{cfg['icon_color']};"
            f" border-radius:17px; border:none;"
        )
        lay.addWidget(ico, 0, Qt.AlignmentFlag.AlignVCenter)

        col = QVBoxLayout()
        col.setSpacing(2)
        col.setContentsMargins(0, 0, 0, 0)
        if title:
            t_lbl = QLabel(title)
            t_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            t_lbl.setStyleSheet(
                f"color:{cfg['title_color']}; background:transparent; border:none;"
            )
            col.addWidget(t_lbl)
        m_lbl = QLabel(message)
        m_lbl.setFont(QFont("Segoe UI", 10))
        m_lbl.setWordWrap(True)
        m_lbl.setStyleSheet(
            f"color:{cfg['text_color']}; background:transparent; border:none;"
        )
        col.addWidget(m_lbl)
        lay.addLayout(col, 1)


# ============================================================
#   BOŞ DURUM EKRANİ
# ============================================================
class EmptyStateWidget(QFrame):
    """Premium boş durum ekranı (kart/liste boş olduğunda gösterilir)."""

    def __init__(self, icon: str, title: str,
                 subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QFrame { background:transparent; border:none; }")

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setContentsMargins(40, 64, 40, 64)
        lay.setSpacing(14)

        # İkon dairesi
        ico_lbl = QLabel(icon)
        ico_lbl.setFixedSize(76, 76)
        ico_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico_lbl.setFont(QFont("Segoe UI", 30))
        ico_lbl.setStyleSheet(
            f"background:#f1f5f9; color:{MUTED}; border-radius:38px; border:none;"
        )
        lay.addWidget(ico_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        t_lbl = QLabel(title)
        t_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        t_lbl.setStyleSheet(
            f"color:{TEXT}; background:transparent; border:none;"
        )
        t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t_lbl)

        if subtitle:
            s_lbl = QLabel(subtitle)
            s_lbl.setFont(QFont("Segoe UI", 11))
            s_lbl.setStyleSheet(
                f"color:{MUTED}; background:transparent; border:none;"
            )
            s_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            s_lbl.setWordWrap(True)
            lay.addWidget(s_lbl)


# ============================================================
#   YUVARLAK KÖŞELİ GÖRSEL WİDGET
# ============================================================
class RoundedImageWidget(QWidget):
    """
    Verilen pixmap'ı yuvarlak köşelerle, cover (crop-to-fill) modunda çizer.
    Detay diyaloğunda araç fotoğrafı için kullanılır.
    """

    def __init__(self, pixmap: QPixmap, radius: int = 16,
                 fixed_height: int = 220, parent=None):
        super().__init__(parent)
        self._pixmap = pixmap
        self._radius = radius
        self.setFixedHeight(fixed_height)

    def paintEvent(self, event):
        if not self._pixmap or self._pixmap.isNull():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h, r = self.width(), self.height(), self._radius

        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, w, h), r, r)
        painter.setClipPath(clip)

        scaled = self._pixmap.scaled(
            w, h,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        xo = max(0, (scaled.width()  - w) // 2)
        yo = max(0, (scaled.height() - h) // 2)
        painter.drawPixmap(0, 0, scaled.copy(xo, yo, w, h))
