# src/gui.py: PyQt application entry point, window setup and state wiring

import datetime
import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QFileIconProvider,
    QMainWindow,
    QStyle,
    QTreeWidgetItem,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from src import fft

UI_PATH = os.path.join(os.path.dirname(__file__), "gui.ui")

FILE_LIST_DARK_STYLE = """
QTreeWidget {
    background-color: #1e1e1e;
    color: #cccccc;
    border: none;
}
QTreeWidget::item {
    height: 22px;
}
QTreeWidget::item:selected {
    background-color: #094771;
    color: #ffffff;
}
"""

FILE_LIST_LIGHT_STYLE = """
QTreeWidget {
    background-color: #ffffff;
    color: #1e1e1e;
    border: none;
}
QTreeWidget::item {
    height: 22px;
}
QTreeWidget::item:selected {
    background-color: #cde8ff;
    color: #000000;
}
"""


def _format_size(num_bytes):
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return "%.1f %s" % (size, unit)
        size /= 1024
    return "%.1f GB" % size


def _format_mtime(mtime):
    return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")


def _build_file_tree(root_path, image_paths):
    tree = {}
    for image_path in image_paths:
        relpath = os.path.relpath(image_path, root_path)
        parts = relpath.split(os.sep)
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = image_path
    return tree


class AnalysisState:
    """Holds the root path, discovered image paths and current selections."""

    def __init__(self):
        self.root_path = None
        self.image_paths = []
        self.selected_image_path = None
        self.settings = fft.Settings()
        self.selected_roi = None
        self.selected_direction = "horizontal"


class CanvasView:
    """Owns the Canvas Axes and renders the image and ROI overlays."""

    def __init__(self, placeholder_label, canvas_tab_layout):
        self.placeholder_label = placeholder_label
        self.displayed_image = None
        self.roi_items = []
        self.editing_roi_index = None
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.figure_canvas = FigureCanvasQTAgg(self.figure)
        canvas_tab_layout.addWidget(self.figure_canvas)
        self.figure_canvas.hide()

    def show_empty_state(self, message):
        self.placeholder_label.setText(message)
        self.placeholder_label.show()
        self.figure_canvas.hide()

    def show_image(self, image, rois=None):
        self.displayed_image = image
        fft.draw_image(self.ax, image, roi=rois)
        self.placeholder_label.hide()
        self.figure_canvas.show()
        self.figure_canvas.draw_idle()

    def drag_roi_corner(self, index, corner, position):
        raise NotImplementedError("drag_roi_corner is not implemented yet")


class GuiController:
    """Handles explorer events, updates AnalysisState and calls src.fft APIs."""

    def __init__(self, state, canvas_view):
        self.state = state
        self.canvas_view = canvas_view
        self.is_refreshing = False
        self.source_image = None
        self.rotated_image = None
        self.analysis_cache = {}

    def refresh_image_list(self):
        if not self.state.root_path:
            return
        self.is_refreshing = True
        try:
            self.state.image_paths = fft.find_image_paths(self.state.root_path)
        finally:
            self.is_refreshing = False

    def select_image(self, image_path):
        image = fft.get_image(image_path, rotation=0)
        self.source_image = image
        self.rotated_image = image
        self.state.selected_image_path = image_path
        if not self.state.settings.rois:
            self.state.settings.rois.append(
                {"xmin": 0, "xmax": 1, "ymin": 0, "ymax": 1, "label": "Total", "color": "yellow"}
            )
        self.canvas_view.show_image(image, self.state.settings.rois)

    def set_rotation(self, rotation):
        raise NotImplementedError("set_rotation is not implemented yet")

    def add_roi(self):
        raise NotImplementedError("add_roi is not implemented yet")

    def delete_roi(self, index):
        raise NotImplementedError("delete_roi is not implemented yet")

    def update_roi_bounds(self, index, bounds):
        raise NotImplementedError("update_roi_bounds is not implemented yet")

    def refresh_roi_analysis(self, roi, direction):
        raise NotImplementedError("refresh_roi_analysis is not implemented yet")


class MainWindow(QMainWindow):
    """Loads gui.ui, owns the screen widgets and displays controller state."""

    def __init__(self):
        super().__init__()
        self.load_ui()
        self.icon_provider = QFileIconProvider()
        self.canvas_view = CanvasView(self.canvasPlaceholder, self.canvasTabLayout)
        self.controller = GuiController(AnalysisState(), self.canvas_view)
        self.connect_signals()

    def load_ui(self):
        uic.loadUi(UI_PATH, self)

    def connect_signals(self):
        self.browseButton.setEnabled(True)
        self.refreshButton.setEnabled(True)
        self.fileList.setEnabled(True)
        self.browseButton.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.refreshButton.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.darkThemeButton.setIcon(self.style().standardIcon(QStyle.SP_DesktopIcon))
        self.lightThemeButton.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.set_file_list_theme("dark")
        self.browseButton.clicked.connect(self.browse_root)
        self.refreshButton.clicked.connect(self.refresh_file_list)
        self.darkThemeButton.clicked.connect(lambda: self.set_file_list_theme("dark"))
        self.lightThemeButton.clicked.connect(lambda: self.set_file_list_theme("light"))
        self.fileList.currentItemChanged.connect(self.on_file_selected)

    def set_file_list_theme(self, theme):
        style = FILE_LIST_DARK_STYLE if theme == "dark" else FILE_LIST_LIGHT_STYLE
        self.fileList.setStyleSheet(style)

    def browse_root(self):
        root_path = QFileDialog.getExistingDirectory(self, "Select data root")
        if not root_path:
            return
        self.controller.state.root_path = root_path
        self.dataRootEdit.setText(root_path)
        self.rootTitleLabel.setText(os.path.basename(root_path) or root_path)
        self.refresh_file_list()

    def refresh_file_list(self):
        try:
            self.controller.refresh_image_list()
        except Exception as error:
            self.set_status("Failed to list images: %s" % error)
            return
        self.fileList.clear()
        tree = _build_file_tree(self.controller.state.root_path, self.controller.state.image_paths)
        self._add_tree_nodes(self.fileList, tree)
        self.fileCountLabel.setText("%d files found" % len(self.controller.state.image_paths))

    def _add_tree_nodes(self, parent, tree):
        add_child = parent.addChild if isinstance(parent, QTreeWidgetItem) else parent.addTopLevelItem
        for name, value in sorted(tree.items()):
            if isinstance(value, dict):
                folder_item = QTreeWidgetItem([name])
                folder_item.setIcon(0, self.icon_provider.icon(QFileIconProvider.Folder))
                add_child(folder_item)
                self._add_tree_nodes(folder_item, value)
            else:
                file_item = QTreeWidgetItem([name])
                file_item.setIcon(0, self.icon_provider.icon(QFileInfo(value)))
                file_item.setData(0, Qt.UserRole, value)
                add_child(file_item)

    def on_file_selected(self, current, previous):
        if current is None:
            return
        image_path = current.data(0, Qt.UserRole)
        if image_path is None:
            return
        try:
            self.controller.select_image(image_path)
            size_str = _format_size(os.path.getsize(image_path))
            date_str = _format_mtime(os.path.getmtime(image_path))
            self.set_status("%s | %s | %s" % (image_path, size_str, date_str))
        except Exception as error:
            self.set_status("Failed to load image: %s" % error)
            self.canvas_view.show_empty_state("Failed to load image")

    def set_status(self, message):
        self.statusbar.showMessage(message)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
