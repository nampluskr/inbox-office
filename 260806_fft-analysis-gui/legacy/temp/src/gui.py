"""PyQt GUI for interactive FFT ROI analysis."""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5 import uic
from PyQt5.QtCore import QObject, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QColorDialog,
    QFileDialog,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from . import fft


ROI_KEYS = ("xmin", "xmax", "ymin", "ymax")
ROI_COLORS = ("#d62728", "#2ca02c", "#1f77b4", "#ff7f0e", "#9467bd")


def default_rois():
    """Return independent ROI dictionaries matching the notebook defaults."""
    return [
        {
            "xmin": 0.1,
            "xmax": 0.9,
            "ymin": 0.1,
            "ymax": 0.45,
            "label": "ROI-1",
            "color": ROI_COLORS[0],
        },
        {
            "xmin": 0.1,
            "xmax": 0.9,
            "ymin": 0.55,
            "ymax": 0.9,
            "label": "ROI-2",
            "color": ROI_COLORS[1],
        },
    ]


@dataclass
class AnalysisState:
    """Keep file discovery, common settings, and API-compatible ROI values."""

    data_root: str | None = None
    file_paths: list[str] = field(default_factory=list)
    data_path: str | None = None
    rotation: int = -90
    direction: str = "horizontal"
    width_mm: float = 1200.0
    height_mm: float = 600.0
    top_k: int = 3
    image_width: int = 0
    image_height: int = 0
    rois: list[dict] = field(default_factory=default_rois)
    selected_roi_index: int | None = 0

    def set_settings(self, rotation, direction, width_mm, height_mm, top_k=3):
        """Validate and store settings shared by every discovered image."""
        if rotation not in (0, 90, -90):
            raise ValueError("rotation must be 0, 90, or -90")
        if direction not in ("horizontal", "vertical"):
            raise ValueError("direction must be horizontal or vertical")
        try:
            width_mm = float(width_mm)
            height_mm = float(height_mm)
        except (TypeError, ValueError) as error:
            raise ValueError("image width and height must be numeric") from error
        if width_mm <= 0 or height_mm <= 0:
            raise ValueError("image width and height must be greater than zero")
        try:
            top_k_value = float(top_k)
        except (TypeError, ValueError) as error:
            raise ValueError("Top-K peaks must be a positive integer") from error
        if isinstance(top_k, bool) or not top_k_value.is_integer() or top_k_value < 1:
            raise ValueError("Top-K peaks must be a positive integer")
        top_k = int(top_k_value)

        self.rotation = rotation
        self.direction = direction
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.top_k = top_k

    def set_image_shape(self, width, height):
        """Store the dimensions of the currently displayed rotated image."""
        if width < 1 or height < 1:
            raise ValueError("image dimensions must be greater than zero")
        self.image_width = int(width)
        self.image_height = int(height)

    def px_to_mm(self):
        """Return the selected direction's scale for the rotated image."""
        if self.image_width < 1 or self.image_height < 1:
            return None
        if self.direction == "horizontal":
            return self.height_mm / self.image_height
        return self.width_mm / self.image_width

    def add_roi(self, roi):
        """Validate, append, and select a newly drawn ROI."""
        index = len(self.rois)
        normalized = self.validate_roi(roi)
        normalized["label"] = f"ROI-{index + 1}"
        normalized["color"] = ROI_COLORS[index % len(ROI_COLORS)]
        self.rois.append(normalized)
        self.selected_roi_index = index
        return normalized

    def update_roi(self, index, roi):
        """Validate and replace one ROI while preserving its metadata."""
        self._validate_index(index)
        current = self.rois[index]
        normalized = self.validate_roi(roi)
        normalized["label"] = current["label"]
        normalized["color"] = current["color"]
        self.rois[index] = normalized
        self.selected_roi_index = index

    def update_roi_metadata(self, index, label, color):
        """Update the user-visible name and color of one ROI."""
        self._validate_index(index)
        label = str(label).strip()
        color = str(color).strip()
        if not label:
            raise ValueError("ROI name must not be empty")
        if not color:
            raise ValueError("ROI color must not be empty")
        self.rois[index]["label"] = label
        self.rois[index]["color"] = color
        self.selected_roi_index = index

    def delete_selected_roi(self):
        """Delete the selected ROI and select the nearest remaining ROI."""
        if self.selected_roi_index is None:
            raise ValueError("Select an ROI before deleting it")
        del self.rois[self.selected_roi_index]
        if not self.rois:
            self.selected_roi_index = None
        else:
            self.selected_roi_index = min(self.selected_roi_index, len(self.rois) - 1)

    def select_roi(self, index):
        """Select an existing ROI by index."""
        self._validate_index(index)
        self.selected_roi_index = index

    def _validate_index(self, index):
        if index < 0 or index >= len(self.rois):
            raise IndexError("ROI index is out of range")

    @staticmethod
    def validate_roi(roi):
        """Return normalized API-compatible coordinates after validation."""
        try:
            normalized = {key: float(roi[key]) for key in ROI_KEYS}
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("ROI requires numeric xmin, xmax, ymin, and ymax") from error

        if not 0 <= normalized["xmin"] < normalized["xmax"] <= 1:
            raise ValueError("ROI must satisfy 0 <= xmin < xmax <= 1")
        if not 0 <= normalized["ymin"] < normalized["ymax"] <= 1:
            raise ValueError("ROI must satisfy 0 <= ymin < ymax <= 1")
        return normalized


class AnalysisPlot(QWidget):
    """Render multiple ROI curves on one shared set of axes."""

    def __init__(self, result_kind, parent=None):
        super().__init__(parent)
        self.result_kind = result_kind
        self.figure = Figure(figsize=(7, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.clear_results()

    def set_results(self, results, rois, direction, unit, peak_results=None):
        """Draw one color-coded line for every ROI result."""
        self.axes.clear()
        for index, (points, roi) in enumerate(zip(results, rois)):
            if not points:
                continue
            x_values, y_values = zip(*points)
            line, = self.axes.plot(
                x_values,
                y_values,
                color=roi.get("color"),
                label=roi.get("label"),
            )
            if peak_results is not None and index < len(peak_results) and peak_results[index]:
                peak_x, peak_y = zip(*peak_results[index])
                self.axes.scatter(peak_x, peak_y, color=line.get_color(), marker="x", zorder=3)

        direction_label = "Horizontal Lines" if direction == "horizontal" else "Vertical Lines"
        if self.result_kind == "profile":
            self.axes.set_xlabel(f"Position ({unit})")
            self.axes.set_ylabel("Mean intensity")
            self.axes.set_title(f"{direction_label} - Profile")
        else:
            frequency_unit = "cycles/mm" if unit == "mm" else "cycles/px"
            self.axes.set_xlabel(f"Frequency ({frequency_unit})")
            self.axes.set_ylabel("Amplitude")
            self.axes.set_title(f"{direction_label} - FFT Intensity")
        if self.axes.lines:
            self.axes.legend()
        self.axes.grid(True, alpha=0.25)
        self.canvas.draw_idle()

    def clear_results(self, message="Select a file to view analysis results."):
        """Clear stale curves and display a centered empty-state message."""
        self.axes.clear()
        self.axes.text(0.5, 0.5, message, ha="center", va="center", transform=self.axes.transAxes)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.canvas.draw_idle()


class RoiItem(QGraphicsRectItem):
    """Selectable ROI rectangle with four corner resize handles."""

    HANDLE_SIZE = 10.0
    MIN_SIZE = 2.0

    def __init__(self, index, scene_rect, image_size, label, color, changed_callback):
        super().__init__(0.0, 0.0, scene_rect.width(), scene_rect.height())
        self.index = index
        self.image_width, self.image_height = image_size
        self.label = label
        self.color = QColor(color)
        self.changed_callback = changed_callback
        self._resize_corner = None
        self._resize_start_rect = None
        self.setPos(scene_rect.topLeft())
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable
            | QGraphicsRectItem.ItemIsSelectable
            | QGraphicsRectItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.setPen(QPen(self.color, 2.0))
        self.setZValue(2.0)

    def boundingRect(self):
        """Include resize handles and the ROI label in the paint area."""
        margin = self.HANDLE_SIZE
        return super().boundingRect().adjusted(-margin, -margin, margin, margin)

    def paint(self, painter, option, widget=None):
        """Draw the rectangle, label, and selected resize handles."""
        painter.setPen(QPen(self.color, 2.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.rect())
        painter.drawText(self.rect().adjusted(4.0, 4.0, -4.0, -4.0), Qt.AlignLeft | Qt.AlignTop, self.label)
        if self.isSelected():
            painter.setPen(QPen(self.color, 1.0))
            painter.setBrush(QColor("white"))
            for handle in self._handle_rects().values():
                painter.drawRect(handle)

    def itemChange(self, change, value):
        """Keep normal drag movement inside the source image."""
        if change == QGraphicsRectItem.ItemPositionChange and self._resize_corner is None:
            rect = self.rect()
            x = min(max(value.x(), 0.0), max(0.0, self.image_width - rect.width()))
            y = min(max(value.y(), 0.0), max(0.0, self.image_height - rect.height()))
            return QPointF(x, y)
        return super().itemChange(change, value)

    def hoverMoveEvent(self, event):
        """Show a resize cursor over a selected corner handle."""
        corner = self._handle_at(event.pos()) if self.isSelected() else None
        if corner in ("nw", "se"):
            self.setCursor(Qt.SizeFDiagCursor)
        elif corner in ("ne", "sw"):
            self.setCursor(Qt.SizeBDiagCursor)
        else:
            self.setCursor(Qt.SizeAllCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        """Begin corner resizing or normal item movement."""
        self.setSelected(True)
        self._resize_corner = self._handle_at(event.pos())
        if self._resize_corner is not None:
            self._resize_start_rect = self.scene_rect()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Resize the selected corner while keeping the ROI in bounds."""
        if self._resize_corner is None:
            super().mouseMoveEvent(event)
            return
        self._resize_to(event.scenePos())
        event.accept()

    def mouseReleaseEvent(self, event):
        """Emit one geometry update after a move or resize is complete."""
        if self._resize_corner is not None:
            self._resize_to(event.scenePos())
            self._resize_corner = None
            self._resize_start_rect = None
            self.unsetCursor()
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        self.changed_callback(self.index, self.scene_rect())

    def scene_rect(self):
        """Return the ROI rectangle in source-image coordinates."""
        return QRectF(self.pos().x(), self.pos().y(), self.rect().width(), self.rect().height())

    def _handle_rects(self):
        half = self.HANDLE_SIZE / 2.0
        rect = self.rect()
        return {
            "nw": QRectF(rect.left() - half, rect.top() - half, self.HANDLE_SIZE, self.HANDLE_SIZE),
            "ne": QRectF(rect.right() - half, rect.top() - half, self.HANDLE_SIZE, self.HANDLE_SIZE),
            "sw": QRectF(rect.left() - half, rect.bottom() - half, self.HANDLE_SIZE, self.HANDLE_SIZE),
            "se": QRectF(rect.right() - half, rect.bottom() - half, self.HANDLE_SIZE, self.HANDLE_SIZE),
        }

    def _handle_at(self, position):
        for corner, handle in self._handle_rects().items():
            if handle.contains(position):
                return corner
        return None

    def _resize_to(self, scene_position):
        start = self._resize_start_rect
        if start is None:
            return
        x = min(max(scene_position.x(), 0.0), self.image_width)
        y = min(max(scene_position.y(), 0.0), self.image_height)
        if self._resize_corner == "nw":
            left = min(x, start.right() - self.MIN_SIZE)
            top = min(y, start.bottom() - self.MIN_SIZE)
            rect = QRectF(left, top, start.right() - left, start.bottom() - top)
        elif self._resize_corner == "ne":
            right = max(x, start.left() + self.MIN_SIZE)
            top = min(y, start.bottom() - self.MIN_SIZE)
            rect = QRectF(start.left(), top, right - start.left(), start.bottom() - top)
        elif self._resize_corner == "sw":
            left = min(x, start.right() - self.MIN_SIZE)
            bottom = max(y, start.top() + self.MIN_SIZE)
            rect = QRectF(left, start.top(), start.right() - left, bottom - start.top())
        else:
            right = max(x, start.left() + self.MIN_SIZE)
            bottom = max(y, start.top() + self.MIN_SIZE)
            rect = QRectF(start.left(), start.top(), right - start.left(), bottom - start.top())
        self.prepareGeometryChange()
        self.setPos(rect.topLeft())
        self.setRect(0.0, 0.0, rect.width(), rect.height())
        self.update()


class ImageView(QGraphicsView):
    """Display a grayscale image and edit normalized common ROI overlays."""

    roi_created = pyqtSignal(dict)
    roi_geometry_changed = pyqtSignal(int, dict)
    roi_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap_item = None
        self._image_width = 0
        self._image_height = 0
        self._roi_items = []
        self._updating_rois = False
        self._draw_mode = False
        self._draw_origin = None
        self._draw_item = None
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setBackgroundBrush(QColor("#202020"))
        self._scene.selectionChanged.connect(self._emit_selected_roi)

    def set_image(self, data, rois, selected_index=None):
        """Replace the source image and recreate all ROI overlays."""
        image = self._to_qimage(data)
        self._image_width = image.width()
        self._image_height = image.height()
        self._updating_rois = True
        self._roi_items = []
        self._scene.clear()
        self._pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(image))
        self._pixmap_item.setZValue(0.0)
        self._scene.addItem(self._pixmap_item)
        self._scene.setSceneRect(0.0, 0.0, self._image_width, self._image_height)
        self._updating_rois = False
        self.set_rois(rois, selected_index)
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def clear_image(self):
        """Remove a stale image and its ROI overlays."""
        self._updating_rois = True
        self._roi_items = []
        self._scene.clear()
        self._pixmap_item = None
        self._image_width = 0
        self._image_height = 0
        self._draw_mode = False
        self._updating_rois = False
        self.unsetCursor()

    def set_rois(self, rois, selected_index=None):
        """Render API-compatible ROI dictionaries on the current image."""
        self._updating_rois = True
        for item in self._roi_items:
            if item.scene() is self._scene:
                self._scene.removeItem(item)
        self._roi_items = []
        if self._image_width and self._image_height:
            for index, roi in enumerate(rois):
                scene_rect = QRectF(
                    roi["xmin"] * self._image_width,
                    roi["ymin"] * self._image_height,
                    (roi["xmax"] - roi["xmin"]) * self._image_width,
                    (roi["ymax"] - roi["ymin"]) * self._image_height,
                )
                item = RoiItem(
                    index,
                    scene_rect,
                    (self._image_width, self._image_height),
                    roi.get("label", f"ROI-{index + 1}"),
                    roi.get("color", "#d62728"),
                    self._on_geometry_changed,
                )
                self._scene.addItem(item)
                self._roi_items.append(item)
            if selected_index is not None and 0 <= selected_index < len(self._roi_items):
                self._roi_items[selected_index].setSelected(True)
        self._updating_rois = False

    def select_roi(self, index):
        """Select one ROI item without modifying its geometry."""
        if 0 <= index < len(self._roi_items):
            self._updating_rois = True
            self._scene.clearSelection()
            self._roi_items[index].setSelected(True)
            self._updating_rois = False

    def begin_roi_creation(self):
        """Enter one-shot click-drag ROI drawing mode."""
        if not self._image_width or not self._image_height:
            return
        self._draw_mode = True
        self.setCursor(Qt.CrossCursor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._image_width and self._image_height:
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        if self._draw_mode and event.button() == Qt.LeftButton:
            self._draw_origin = self._bounded_scene_point(self.mapToScene(event.pos()))
            self._draw_item = QGraphicsRectItem(QRectF(self._draw_origin, self._draw_origin))
            self._draw_item.setPen(QPen(QColor("white"), 1.5, Qt.DashLine))
            self._draw_item.setZValue(3.0)
            self._scene.addItem(self._draw_item)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._draw_mode and self._draw_item is not None:
            current = self._bounded_scene_point(self.mapToScene(event.pos()))
            self._draw_item.setRect(QRectF(self._draw_origin, current).normalized())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._draw_mode and self._draw_item is not None and event.button() == Qt.LeftButton:
            current = self._bounded_scene_point(self.mapToScene(event.pos()))
            rect = QRectF(self._draw_origin, current).normalized()
            self._scene.removeItem(self._draw_item)
            self._draw_item = None
            self._draw_origin = None
            self._draw_mode = False
            self.unsetCursor()
            if rect.width() >= RoiItem.MIN_SIZE and rect.height() >= RoiItem.MIN_SIZE:
                self.roi_created.emit(self._normalized_roi(rect))
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _on_geometry_changed(self, index, rect):
        self.roi_geometry_changed.emit(index, self._normalized_roi(rect))

    def _normalized_roi(self, rect):
        return {
            "xmin": rect.left() / self._image_width,
            "xmax": rect.right() / self._image_width,
            "ymin": rect.top() / self._image_height,
            "ymax": rect.bottom() / self._image_height,
        }

    def _emit_selected_roi(self):
        if self._updating_rois:
            return
        for item in self._roi_items:
            if item.isSelected():
                self.roi_selected.emit(item.index)
                return

    def _bounded_scene_point(self, point):
        return QPointF(
            min(max(point.x(), 0.0), self._image_width),
            min(max(point.y(), 0.0), self._image_height),
        )

    @staticmethod
    def _to_qimage(data):
        array = np.asarray(data)
        if array.ndim != 2:
            raise ValueError("The selected .mim image must be two-dimensional")
        minimum = float(array.min())
        maximum = float(array.max())
        if maximum == minimum:
            image_data = np.zeros(array.shape, dtype=np.uint8)
        else:
            image_data = np.clip((array - minimum) * 255.0 / (maximum - minimum), 0, 255).astype(np.uint8)
        image_data = np.ascontiguousarray(image_data)
        height, width = image_data.shape
        image_bytes = image_data.tobytes()
        return QImage(image_bytes, width, height, width, QImage.Format_Grayscale8).copy()


class MainWindow(QMainWindow):
    """Collect user input and expose rendering methods to the controller."""

    root_selected = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    file_selected = pyqtSignal(str)
    settings_changed = pyqtSignal(int, str, float, float, int)
    roi_draw_requested = pyqtSignal()
    roi_created = pyqtSignal(dict)
    roi_geometry_changed = pyqtSignal(int, dict)
    roi_delete_requested = pyqtSignal()
    roi_selected = pyqtSignal(int)
    roi_metadata_changed = pyqtSignal(int, str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFT ROI Analysis GUI")
        self.resize(1440, 900)
        self.setMinimumSize(960, 640)
        self._updating_settings = False
        self._updating_rois = False
        self._current_rois = []
        self._current_color = "#d62728"
        self._build_ui()

    def set_data_root(self, data_root):
        """Show the active recursive search root."""
        self._root_path.setText(data_root or "")

    def set_files(self, paths, data_root, current_path=None):
        """Populate the single-selection list with sorted relative paths."""
        self._file_list.blockSignals(True)
        self._file_list.clear()
        current_item = None
        for path in paths:
            relative_path = os.path.relpath(path, data_root) if data_root else path
            item = QListWidgetItem(relative_path)
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            self._file_list.addItem(item)
            if path == current_path:
                current_item = item
        if current_item is not None:
            self._file_list.setCurrentItem(current_item)
        else:
            self._file_list.clearSelection()
            self._file_list.setCurrentRow(-1)
        self._file_list.blockSignals(False)
        self._file_count.setText(f"{len(paths)} file(s)")

    def set_image(self, data, rois, selected_index):
        """Display the rotated source image and all ROI overlays."""
        self._image_view.set_image(data, rois, selected_index)

    def set_rois(self, rois, selected_index):
        """Synchronize the ROI list, metadata fields, and image selection."""
        self._current_rois = [roi.copy() for roi in rois]
        self._updating_rois = True
        self._roi_list.clear()
        for index, roi in enumerate(rois):
            item = QListWidgetItem(roi.get("label", f"ROI-{index + 1}"))
            item.setData(Qt.UserRole, index)
            item.setForeground(QColor(roi.get("color", "#d62728")))
            self._roi_list.addItem(item)
        if selected_index is not None and 0 <= selected_index < len(rois):
            self._roi_list.setCurrentRow(selected_index)
            self._set_roi_fields(rois[selected_index])
        else:
            self._roi_list.setCurrentRow(-1)
            self._clear_roi_fields()
        self._updating_rois = False
        self._image_view.set_rois(rois, selected_index)

    def set_settings(self, state):
        """Show validated common settings and derived image information."""
        self._updating_settings = True
        rotation_index = self._rotation.findData(state.rotation)
        direction_index = self._direction.findData(state.direction)
        self._rotation.setCurrentIndex(rotation_index)
        self._direction.setCurrentIndex(direction_index)
        self._width_mm.setValue(state.width_mm)
        self._height_mm.setValue(state.height_mm)
        self._top_k.setValue(state.top_k)
        if state.image_width and state.image_height:
            self._pixel_size.setText(f"{state.image_width} x {state.image_height} px")
            self._px_to_mm.setText(f"{state.px_to_mm():.8g} mm/px")
        else:
            self._pixel_size.setText("-")
            self._px_to_mm.setText("-")
        self._updating_settings = False

    def set_profile_results(self, results, rois, direction, unit):
        """Render all ROI profiles in the Profile tab."""
        self._profile_plot.set_results(results, rois, direction, unit)

    def set_fft_results(self, results, rois, direction, unit):
        """Render all ROI spectra in the FFT Intensity tab."""
        self._fft_plot.set_results(results, rois, direction, unit)

    def set_selected_analysis(self, crop, profile, spectrum, peaks, roi, direction, unit):
        """Render detailed crop, profile, and FFT results for one selected ROI."""
        self._analysis_image_view.set_image(crop, [], None)
        self._analysis_profile_plot.set_results([profile], [roi], direction, unit)
        self._analysis_fft_plot.set_results([spectrum], [roi], direction, unit, [peaks])

    def clear_selected_analysis(self, message="Select an ROI to view detailed analysis."):
        """Clear every visual component in the selected ROI Analysis tab."""
        self._analysis_image_view.clear_image()
        self._analysis_profile_plot.clear_results(message)
        self._analysis_fft_plot.clear_results(message)

    def clear_plots(self, message="Select a file to view analysis results."):
        """Clear both result plots with the same empty-state message."""
        self._profile_plot.clear_results(message)
        self._fft_plot.clear_results(message)

    def clear_analysis(self):
        """Clear stale image, plot, and derived pixel information."""
        self._image_view.clear_image()
        self.clear_plots()
        self.clear_selected_analysis()
        self._pixel_size.setText("-")
        self._px_to_mm.setText("-")

    def begin_roi_creation(self):
        """Open the image tab and enter one-shot ROI drawing mode."""
        self._tabs.setCurrentIndex(0)
        self._image_view.begin_roi_creation()

    def set_status(self, message):
        """Show a status or error message to the user."""
        self.statusBar().showMessage(message)

    def _build_ui(self):
        """Load the Qt Designer layout and connect its named widgets."""
        uic.loadUi(str(Path(__file__).with_suffix(".ui")), self)

        self._root_path = self.rootPathEdit
        self._file_count = self.fileCountLabel
        self._file_list = self.fileList
        self._tabs = self.analysisTabs
        self._rotation = self.rotationCombo
        self._direction = self.directionCombo
        self._width_mm = self.widthSpinBox
        self._height_mm = self.heightSpinBox
        self._top_k = self.topKSpinBox
        self._pixel_size = self.pixelSizeValueLabel
        self._px_to_mm = self.scaleValueLabel
        self._roi_list = self.roiList
        self._roi_name = self.roiNameEdit
        self._color_button = self.roiColorButton
        self._roi_coordinates = {
            "xmin": self.xminEdit,
            "xmax": self.xmaxEdit,
            "ymin": self.yminEdit,
            "ymax": self.ymaxEdit,
        }

        self._rotation.setItemData(0, 0)
        self._rotation.setItemData(1, 90)
        self._rotation.setItemData(2, -90)
        self._direction.setItemData(0, "horizontal")
        self._direction.setItemData(1, "vertical")

        self._image_view = ImageView()
        self._analysis_image_view = ImageView()
        self._analysis_profile_plot = AnalysisPlot("profile")
        self._analysis_fft_plot = AnalysisPlot("fft")
        self._profile_plot = AnalysisPlot("profile")
        self._fft_plot = AnalysisPlot("fft")
        self._replace_placeholder(self.canvasView, self._image_view)
        self._replace_placeholder(self.cropView, self._analysis_image_view)
        self._replace_placeholder(self.analysisProfilePlaceholder, self._analysis_profile_plot)
        self._replace_placeholder(self.analysisFftPlaceholder, self._analysis_fft_plot)
        self._replace_placeholder(self.profilePlotPlaceholder, self._profile_plot)
        self._replace_placeholder(self.fftPlotPlaceholder, self._fft_plot)

        self.browseButton.clicked.connect(self._browse_root)
        self.refreshButton.clicked.connect(self.refresh_requested)
        self._file_list.currentItemChanged.connect(self._on_file_changed)
        self._image_view.roi_created.connect(self.roi_created)
        self._image_view.roi_geometry_changed.connect(self.roi_geometry_changed)
        self._image_view.roi_selected.connect(self._on_image_roi_selected)
        self._rotation.currentIndexChanged.connect(self._emit_settings)
        self._direction.currentIndexChanged.connect(self._emit_settings)
        self._width_mm.editingFinished.connect(self._emit_settings)
        self._height_mm.editingFinished.connect(self._emit_settings)
        self._top_k.valueChanged.connect(self._emit_settings)
        self._roi_list.currentRowChanged.connect(self._on_roi_row_changed)
        self.drawRoiButton.clicked.connect(self.roi_draw_requested)
        self.deleteRoiButton.clicked.connect(self.roi_delete_requested)
        self._roi_name.editingFinished.connect(self._emit_roi_metadata)
        self._color_button.clicked.connect(self._choose_roi_color)

    @staticmethod
    def _replace_placeholder(placeholder, replacement):
        """Replace a Designer placeholder with a runtime custom widget."""
        parent = placeholder.parentWidget()
        if isinstance(parent, QSplitter):
            parent.replaceWidget(parent.indexOf(placeholder), replacement)
        else:
            parent.layout().replaceWidget(placeholder, replacement)
        placeholder.deleteLater()

    def _browse_root(self):
        data_root = QFileDialog.getExistingDirectory(self, "Select data root", self._root_path.text())
        if data_root:
            self.root_selected.emit(data_root)

    def _on_file_changed(self, current, previous):
        if current is not None:
            self.file_selected.emit(current.data(Qt.UserRole))

    def _emit_settings(self):
        if self._updating_settings:
            return
        self.settings_changed.emit(
            self._rotation.currentData(),
            self._direction.currentData(),
            self._width_mm.value(),
            self._height_mm.value(),
            self._top_k.value(),
        )

    def _on_roi_row_changed(self, row):
        if self._updating_rois or row < 0 or row >= len(self._current_rois):
            return
        self._set_roi_fields(self._current_rois[row])
        self._image_view.select_roi(row)
        self.roi_selected.emit(row)

    def _on_image_roi_selected(self, index):
        if 0 <= index < self._roi_list.count() and self._roi_list.currentRow() != index:
            self._roi_list.setCurrentRow(index)

    def _set_roi_fields(self, roi):
        self._roi_name.setEnabled(True)
        self._color_button.setEnabled(True)
        self._roi_name.setText(roi.get("label", ""))
        self._current_color = roi.get("color", "#d62728")
        self._set_color_button(self._current_color)
        for key, field in self._roi_coordinates.items():
            field.setText(f"{roi[key]:.6f}")

    def _clear_roi_fields(self):
        self._roi_name.clear()
        self._roi_name.setEnabled(False)
        self._color_button.setEnabled(False)
        self._current_color = "#d62728"
        self._set_color_button(self._current_color)
        for field in self._roi_coordinates.values():
            field.clear()

    def _choose_roi_color(self):
        color = QColorDialog.getColor(QColor(self._current_color), self, "Select ROI color")
        if color.isValid():
            self._current_color = color.name()
            self._set_color_button(self._current_color)
            self._emit_roi_metadata()

    def _set_color_button(self, color):
        self._color_button.setText(color)
        self._color_button.setStyleSheet(f"background-color: {color};")

    def _emit_roi_metadata(self):
        if self._updating_rois:
            return
        index = self._roi_list.currentRow()
        if index >= 0:
            self.roi_metadata_changed.emit(index, self._roi_name.text(), self._current_color)


class GuiController(QObject):
    """Coordinate common state, automatic analysis, and view updates."""

    def __init__(self, view):
        super().__init__(view)
        self.view = view
        self.state = AnalysisState(data_root=self._default_data_root())
        self.profiles = []
        self.spectra = []
        self.selected_fft_peaks = []
        view.root_selected.connect(self.set_data_root)
        view.refresh_requested.connect(self.refresh_files)
        view.file_selected.connect(self.load_file)
        view.settings_changed.connect(self.update_settings)
        view.roi_draw_requested.connect(self.begin_roi_creation)
        view.roi_created.connect(self.add_roi)
        view.roi_geometry_changed.connect(self.update_roi_geometry)
        view.roi_delete_requested.connect(self.delete_selected_roi)
        view.roi_selected.connect(self.select_roi)
        view.roi_metadata_changed.connect(self.update_roi_metadata)
        self.view.set_settings(self.state)
        self._render_rois()
        self.view.set_data_root(self.state.data_root)
        self.refresh_files()

    def set_data_root(self, data_root):
        """Select a discovery root and refresh its MIM file list."""
        data_root = os.path.abspath(data_root)
        if not os.path.isdir(data_root):
            self.view.set_status(f"Data root does not exist: {data_root}")
            return
        self.state.data_root = data_root
        self.state.data_path = None
        self.state.image_width = 0
        self.state.image_height = 0
        self.view.set_data_root(data_root)
        self.view.clear_analysis()
        self.refresh_files()

    def refresh_files(self):
        """Recursively discover and sort MIM files under the current root."""
        try:
            if not self.state.data_root or not os.path.isdir(self.state.data_root):
                raise ValueError("Select an existing data root")
            paths = [os.path.abspath(path) for path in fft.get_paths(self.state.data_root)]
            paths.sort(key=lambda path: os.path.relpath(path, self.state.data_root).lower())
            self.state.file_paths = paths
            if self.state.data_path not in paths:
                self.state.data_path = None
                self.state.image_width = 0
                self.state.image_height = 0
                self.view.clear_analysis()
            self.view.set_files(paths, self.state.data_root, self.state.data_path)
            self.view.set_status(f"Found {len(paths)} .mim file(s).")
        except (OSError, ValueError) as error:
            self.state.file_paths = []
            self.state.data_path = None
            self.state.image_width = 0
            self.state.image_height = 0
            self.view.set_files([], self.state.data_root, None)
            self.view.clear_analysis()
            self.view.set_status(f"File search failed: {error}")

    def load_file(self, data_path):
        """Load and automatically analyze one file selected in the list."""
        if data_path not in self.state.file_paths:
            self.view.set_status(f"File is not in the current list: {data_path}")
            return
        self.state.data_path = data_path
        self.refresh_analysis()

    def update_settings(self, rotation, direction, width_mm, height_mm, top_k=3):
        """Store common settings and refresh the current file."""
        try:
            self.state.set_settings(rotation, direction, width_mm, height_mm, top_k)
            self.view.set_settings(self.state)
            if self.state.data_path:
                self.refresh_analysis()
            else:
                self.view.set_status("Analysis settings updated. Select a file to analyze.")
        except (TypeError, ValueError) as error:
            self.view.set_settings(self.state)
            self.view.set_status(f"Invalid analysis settings: {error}")

    def begin_roi_creation(self):
        """Put the image view into one-shot ROI drawing mode."""
        if not self.state.data_path:
            self.view.set_status("Select a file before drawing an ROI.")
            return
        self.view.begin_roi_creation()
        self.view.set_status("Drag on the image to create an ROI.")

    def add_roi(self, roi):
        """Append a newly drawn common ROI and refresh all results."""
        try:
            self.state.add_roi(roi)
            self._render_rois()
            self.refresh_analysis()
        except (TypeError, ValueError) as error:
            self.view.set_status(f"Invalid ROI: {error}")

    def update_roi_geometry(self, index, roi):
        """Apply a completed ROI move or resize operation."""
        try:
            self.state.update_roi(index, roi)
            self._render_rois()
            self.refresh_analysis()
        except (IndexError, TypeError, ValueError) as error:
            self._render_rois()
            self.view.set_status(f"Invalid ROI: {error}")

    def delete_selected_roi(self):
        """Delete the common ROI selected in either ROI view."""
        try:
            self.state.delete_selected_roi()
            self._render_rois()
            self.refresh_analysis()
        except ValueError as error:
            self.view.set_status(str(error))

    def select_roi(self, index):
        """Synchronize ROI selection without recomputing analysis."""
        try:
            self.state.select_roi(index)
            self._refresh_selected_analysis()
        except IndexError as error:
            self.view.set_status(str(error))

    def update_roi_metadata(self, index, label, color):
        """Update an ROI legend label and color, then redraw results."""
        try:
            self.state.update_roi_metadata(index, label, color)
            self._render_rois()
            self._render_plots()
            self._refresh_selected_analysis()
            self.view.set_status("ROI name and color updated.")
        except (IndexError, ValueError) as error:
            self._render_rois()
            self.view.set_status(f"Invalid ROI metadata: {error}")

    def refresh_analysis(self):
        """Reload the image and compute profile and FFT for every common ROI."""
        image_displayed = False
        try:
            if not self.state.data_path:
                self.view.clear_analysis()
                self.view.set_status("Select a file to analyze.")
                return
            data = fft.get_data(self.state.data_path, rotation=self.state.rotation)
            if data.ndim != 2 or data.size == 0:
                raise ValueError("the selected file must contain a non-empty 2D image")
            height, width = data.shape
            self.state.set_image_shape(width, height)
            self.view.set_image(data, self.state.rois, self.state.selected_roi_index)
            self.view.set_settings(self.state)
            image_displayed = True
            self._validate_crop_sizes()

            if not self.state.rois:
                self.profiles = []
                self.spectra = []
                self.selected_fft_peaks = []
                self.view.clear_plots("Draw an ROI to view analysis results.")
                self.view.clear_selected_analysis("Draw an ROI to view detailed analysis.")
                self.view.set_status(f"Loaded: {self.state.data_path}")
                return

            arguments = {
                "data_path": self.state.data_path,
                "rotation": self.state.rotation,
                "roi": self.state.rois,
                "direction": self.state.direction,
                "px_to_mm": self.state.px_to_mm(),
            }
            self.profiles = fft.get_profile(**arguments)
            self.spectra = fft.get_fft(**arguments)
            self._render_plots()
            self._refresh_selected_analysis()
            self.view.set_status(f"Analysis updated: {self.state.data_path}")
        except Exception as error:
            self.profiles = []
            self.spectra = []
            self.selected_fft_peaks = []
            if image_displayed:
                self.view.clear_plots("Correct the invalid settings or ROI to view results.")
                self.view.clear_selected_analysis("Correct the invalid settings or ROI to view detailed analysis.")
            else:
                self.state.image_width = 0
                self.state.image_height = 0
                self.view.clear_analysis()
            path = self.state.data_path or "no file"
            self.view.set_status(f"Analysis failed for {path}: {error}")

    def _render_rois(self):
        self.view.set_rois(self.state.rois, self.state.selected_roi_index)

    def _render_plots(self):
        if not self.profiles or not self.spectra:
            self.view.clear_plots("Select a file and draw at least one ROI.")
            return
        unit = "mm" if self.state.px_to_mm() is not None else "px"
        self.view.set_profile_results(self.profiles, self.state.rois, self.state.direction, unit)
        self.view.set_fft_results(self.spectra, self.state.rois, self.state.direction, unit)

    def _refresh_selected_analysis(self):
        """Render the selected ROI crop, profile, FFT, and Top-K peak markers."""
        if not self.state.data_path or self.state.selected_roi_index is None:
            self.selected_fft_peaks = []
            self.view.clear_selected_analysis("Select an ROI to view detailed analysis.")
            return
        index = self.state.selected_roi_index
        if index >= len(self.state.rois) or index >= len(self.profiles) or index >= len(self.spectra):
            self.selected_fft_peaks = []
            self.view.clear_selected_analysis("Select an ROI to view detailed analysis.")
            return
        roi = self.state.rois[index]
        crop = fft.get_data(self.state.data_path, rotation=self.state.rotation, roi=roi)
        self.selected_fft_peaks = fft.get_fft_peaks(
            data_path=self.state.data_path,
            rotation=self.state.rotation,
            roi=roi,
            direction=self.state.direction,
            num_peaks=self.state.top_k,
            px_to_mm=self.state.px_to_mm(),
        )
        unit = "mm" if self.state.px_to_mm() is not None else "px"
        self.view.set_selected_analysis(
            crop,
            self.profiles[index],
            self.spectra[index],
            self.selected_fft_peaks,
            roi,
            self.state.direction,
            unit,
        )

    def _validate_crop_sizes(self):
        for index, roi in enumerate(self.state.rois):
            crop = fft.get_data(self.state.data_path, rotation=self.state.rotation, roi=roi)
            if crop.ndim != 2 or min(crop.shape) < 2:
                label = roi.get("label", f"ROI-{index + 1}")
                raise ValueError(f"{label} must contain at least two pixels in each dimension")

    @staticmethod
    def _default_data_root():
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "synthetic"))


def main():
    """Create and run the GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    GuiController(window)
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
