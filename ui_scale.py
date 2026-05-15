"""Масштабирование интерфейса с фиксированной вёрсткой (база 800x600)."""

from PyQt6.QtCore import QRect, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QSizePolicy, QWidget

BASE_WIDTH = 800
BASE_HEIGHT = 600


class _WidgetSnapshot:
    __slots__ = ("geometry", "minimum_size", "maximum_size", "font")

    def __init__(self, widget: QWidget):
        self.geometry = QRect(widget.geometry())
        self.minimum_size = QSize(widget.minimumSize())
        self.maximum_size = QSize(widget.maximumSize())
        self.font = QFont(widget.font())


def _is_layout_managed(widget: QWidget) -> bool:
    parent = widget.parentWidget()
    if parent is None:
        return False
    layout = parent.layout()
    if layout is None:
        return False
    return layout.indexOf(widget) >= 0


class ScalableViewport(QWidget):
    """Сохраняет макет 800x600 и равномерно масштабирует при изменении размера окна."""

    def __init__(
        self,
        content: QWidget,
        base_width: int = BASE_WIDTH,
        base_height: int = BASE_HEIGHT,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._base_width = base_width
        self._base_height = base_height
        self._content = content
        self._content.setParent(self)
        self._content.resize(base_width, base_height)
        self._snapshots: dict[int, _WidgetSnapshot] = {}
        self.refresh_snapshots()

    def content(self) -> QWidget:
        return self._content

    def refresh_snapshots(self) -> None:
        self._snapshots.clear()
        for child in self._content.findChildren(QWidget):
            if child is self._content or _is_layout_managed(child):
                continue
            self._snapshots[id(child)] = _WidgetSnapshot(child)

    def relayout(self) -> None:
        self._apply_scale()

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_scale()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_scale()

    def _apply_scale(self) -> None:
        available_w = max(1, self.width())
        available_h = max(1, self.height())
        scale = min(available_w / self._base_width, available_h / self._base_height)

        content_w = max(1, int(self._base_width * scale))
        content_h = max(1, int(self._base_height * scale))
        offset_x = (available_w - content_w) // 2
        offset_y = (available_h - content_h) // 2

        self._content.setGeometry(offset_x, offset_y, content_w, content_h)

        for child in self._content.findChildren(QWidget):
            if child is self._content or _is_layout_managed(child):
                continue

            snap = self._snapshots.get(id(child))
            if snap is None:
                continue

            geom = snap.geometry
            child.setGeometry(
                int(geom.x() * scale),
                int(geom.y() * scale),
                max(1, int(geom.width() * scale)),
                max(1, int(geom.height() * scale)),
            )

            min_w, min_h = snap.minimum_size.width(), snap.minimum_size.height()
            if min_w > 0 or min_h > 0:
                child.setMinimumSize(
                    int(min_w * scale) if min_w > 0 else 0,
                    int(min_h * scale) if min_h > 0 else 0,
                )

            max_w, max_h = snap.maximum_size.width(), snap.maximum_size.height()
            if max_w < 16777215 or max_h < 16777215:
                child.setMaximumSize(
                    int(max_w * scale) if max_w < 16777215 else 16777215,
                    int(max_h * scale) if max_h < 16777215 else 16777215,
                )

            if snap.font.pointSizeF() > 0:
                font = QFont(snap.font)
                font.setPointSizeF(max(6.0, snap.font.pointSizeF() * scale))
                child.setFont(font)

        self._activate_layouts(self._content)
        self._content.updateGeometry()

    @staticmethod
    def _activate_layouts(root: QWidget) -> None:
        for widget in [root, *root.findChildren(QWidget)]:
            layout = widget.layout()
            if layout is not None:
                layout.activate()


def wrap_scalable(content: QWidget) -> ScalableViewport:
    viewport = ScalableViewport(content)
    viewport.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return viewport
