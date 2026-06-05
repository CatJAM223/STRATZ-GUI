from PyQt6.QtGui import QFont

FONT_FAMILY = "Bahnschrift"
FONT_FALLBACK = "Segoe UI"


def app_font(size: int = 14, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    font = QFont(FONT_FAMILY)
    if not font.exactMatch():
        font = QFont(FONT_FALLBACK)
    font.setPointSize(size)
    font.setWeight(weight)
    return font


def display_font(size: int = 13, bold: bool = False) -> QFont:
    weight = QFont.Weight.DemiBold if bold else QFont.Weight.Medium
    font = app_font(size, weight)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.2)
    return font


def heading_font(size: int = 26) -> QFont:
    font = app_font(size, QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
    return font


def value_font(size: int = 26) -> QFont:
    font = app_font(size, QFont.Weight.DemiBold)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.5)
    return font
