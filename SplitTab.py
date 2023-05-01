from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QGraphicsView, QTableWidgetItem, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QFile
from PyQt5.QtWidgets import QGraphicsScene
from pdf2image import convert_from_path
from Pipeline import extract
import os
import csv

POPPLER_PATH = "C:\Program Files\poppler-0.68.0_x86\bin"


class ZoomView(QGraphicsView):

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                scale = 1.25
            else:
                scale = 0.85
            self.scale(scale, scale)


class PageTab(QWidget):
    def __init__(self):
        super().__init__()

        tab = QWidget(self)

        self.file_name = None
        self.file_path = None

        # Create the horizontal layout for the tab widget
        self.layout = QHBoxLayout(tab)

        # Create the graphics view and add it to the layout
        self.graphics_view = ZoomView(tab)

        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self.layout.addWidget(self.graphics_view)

        # Create the table widget and add it to the layout
        self.table_widget = QTableWidget(tab)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setShowGrid(True)

        self.layout.addWidget(self.table_widget)

        toolBarLayout = QVBoxLayout()
        self.layout.addLayout(toolBarLayout)

        # Add the "Add File" button to the tab
        add_file_button = QPushButton("Add File", tab)
        add_file_button.clicked.connect(
            lambda: self.add_file_to_tab(self.graphics_view))
        toolBarLayout.addWidget(add_file_button)

        # Add the "Extract" button to the tab
        extract_table_button = QPushButton("Extract", tab)
        extract_table_button.clicked.connect(
            lambda: self.preExtract(self.graphics_view, self.table_widget))
        toolBarLayout.addWidget(extract_table_button)

        # Add the "Extract" button to the tab
        export_table_button = QPushButton("Export", tab)
        export_table_button.clicked.connect(
            lambda: self.export(self.table_widget))
        toolBarLayout.addWidget(export_table_button)

    def add_image_to_tab(self, image):

        graphics_view = self.graphics_view

        pixmap = QPixmap.fromImage(image)
        scene = QGraphicsScene(graphics_view)
        scene.addPixmap(pixmap)
        graphics_view.setScene(scene)
        graphics_view.fitInView(
            scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def add_file_to_tab(self, graphics_view):

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Table File", filter="")

        # If a file was selected, display it in the graphics view
        if file_path:
            file_name = os.path.basename(file_path).split('/')[-1]

            if file_path.endswith(".pdf"):
                file_name = file_name.split('.pdf')[0]

                images = convert_from_path(
                    file_path, poppler_path=r"C:/Program Files/poppler-0.68.0_x86/bin")

                image_folder = "./pdf2Image"
                os.makedirs(image_folder, exist_ok=True)

                num_pages = len(images)

                for i in range(num_pages):

                    page_name = f"{file_name}_page{i}"
                    file_path = f"{image_folder}/{page_name}.png"
                    images[i].save(f'{file_path}', 'PNG')

                    ppm_data = QImage(images[i].tobytes(
                    ), images[i].size[0], images[i].size[1], QImage.Format.Format_RGB888)

                    if i == 0:
                        self.file_path = file_path
                        self.file_name = page_name
                        self.add_image_to_tab(ppm_data)

                        index = self.window().tab_widget.indexOf(self)
                        self.window().tab_widget.setTabText(index, page_name)

                        continue

                    curTab = self.window().add_new_tab(True)
                    curTab.file_path = file_path
                    curTab.file_name = page_name
                    curTab.add_image_to_tab(ppm_data)

                    index = self.window().tab_widget.indexOf(curTab)
                    self.window().tab_widget.setTabText(index, page_name)

            else:
                file = QFile(file_path)
                if file.open(QFile.ReadOnly):

                    image = QImage(file_path)
                    self.add_image_to_tab(image)
                    file.close()

                    self.file_name = file_name
                    self.file_path = file_path

                    index = self.window().tab_widget.indexOf(self)
                    self.window().tab_widget.setTabText(index, file_name)

    def preExtract(self, graphics_view, table_widget):

        file_path = self.file_path

        if file_path is None:
            return

        bounded, mat = extract(file_path)

        qimage = QImage(
            bounded.data, bounded.shape[1], bounded.shape[0], bounded.strides[0], QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qimage)
        scene = QGraphicsScene(graphics_view)
        scene.addPixmap(pixmap)
        graphics_view.setScene(scene)
        graphics_view.fitInView(
            scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        table_widget.setColumnCount(mat.shape[1])
        table_widget.setRowCount(mat.shape[0])

        for i in range(table_widget.columnCount()):
            for j in range(table_widget.rowCount()):
                item = QTableWidgetItem(mat[j, i])
                table_widget.setItem(j, i, item)

    def export(self, table_widget):

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Choose Save Location", filter="CSV FILES(*.csv)")

        if not file_path:
            return

        with open(file_path, mode="w", newline='') as file:

            writer = csv.writer(file, delimiter=',', quotechar='"')

            for i in range(table_widget.rowCount()):
                row = []
                for j in range(table_widget.columnCount()):
                    row.append(table_widget.item(i, j).text())
                writer.writerow(row)
                row.clear()
