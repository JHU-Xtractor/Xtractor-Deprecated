from PyQt5.QtWidgets import QLabel, QApplication, QMainWindow, QTabWidget, QTabBar, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QGraphicsView, QTableWidgetItem, QPushButton, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap, QImage, QBrush
from PyQt5.QtCore import Qt, QFile, QEvent
from PyQt5.QtWidgets import QGraphicsScene
from Pipeline import extract
import os
import csv

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.setWindowIcon(QIcon('resources/logo.png'))
        self.setWindowTitle("Xtractor")
        self.setGeometry(300, 300, 800, 600)
        self.setWindowState(Qt.WindowMaximized)

        # Create the vertical layout for the central widget
        vertical_layout = QHBoxLayout(central_widget)

        # Create the tab widget
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.South)

        # Create empty dict of file_paths
        self.file_paths = {}

        # Create the plus button to add new tabs
        plus_button = QPushButton("+", self)
        plus_button.clicked.connect(self.add_new_tab)

        self.plus_tab = QWidget()
        self.plus_tab.setObjectName("main")
        # Set the background image
        self.plus_tab.setStyleSheet('QWidget#main{background-image:url("resources/background.png"); background-position: center; background-repeat: no-repeat;}')

        # Add the plus button to the tab widget
        self.tab_widget.addTab(self.plus_tab, "")
        self.tab_widget.setTabEnabled(self.tab_widget.count() - 1, False)
        self.tab_widget.tabBar().setTabButton(self.tab_widget.count() - 1, QTabBar.RightSide, plus_button)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(lambda index: self.tab_widget.removeTab(index))

        # Add the tab widget to the vertical layout
        vertical_layout.addWidget(self.tab_widget)

    def add_new_tab(self):
        # Create a new tab widget
        tab = QWidget()

        # Create the horizontal layout for the tab widget
        layout = QHBoxLayout(tab)

        # Create the graphics view and add it to the layout
        graphics_view = ZoomView(tab)

        graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        layout.addWidget(graphics_view)

        # Create the table widget and add it to the layout
        table_widget = QTableWidget(tab)
        table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.setAlternatingRowColors(True)
        table_widget.setShowGrid(True)

        layout.addWidget(table_widget)

        toolBarLayout = QVBoxLayout()
        layout.addLayout(toolBarLayout)
       
        # Add the "Add File" button to the tab
        add_file_button = QPushButton("Add File", tab)
        add_file_button.clicked.connect(lambda: self.add_file_to_tab(graphics_view))
        toolBarLayout.addWidget(add_file_button)

        # Add the "Extract" button to the tab
        extract_table_button = QPushButton("Extract", tab)
        extract_table_button.clicked.connect(lambda: self.preExtract(graphics_view, table_widget))
        toolBarLayout.addWidget(extract_table_button)

        # Add the "Extract" button to the tab
        export_table_button = QPushButton("Export", tab)
        export_table_button.clicked.connect(lambda: self.export(table_widget))
        toolBarLayout.addWidget(export_table_button)

        # Add the tab to the tab widget
        idx = self.tab_widget.count() - 1
        self.tab_widget.insertTab(idx, tab, "Tab {}".format(self.tab_widget.count()))
        self.tab_widget.setCurrentIndex(idx)

    
    def add_file_to_tab(self, graphics_view):

        # Prompt the user to select a PDF file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Table File", filter="")

        # If a file was selected, display it in the graphics view
        if file_path:
            file = QFile(file_path)
            if file.open(QFile.ReadOnly):
                pixmap = QPixmap.fromImage(QImage(file_path))
                scene = QGraphicsScene(graphics_view)
                scene.addPixmap(pixmap)
                graphics_view.setScene(scene)
                graphics_view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
                file.close()

                idx = self.tab_widget.currentIndex()
                file_name = os.path.basename(file_path).split('/')[-1]
                self.tab_widget.setTabText(idx, file_name)

                self.file_paths[file_name] = file_path

    
    def preExtract(self, graphics_view, table_widget):
        idx = self.tab_widget.currentIndex()
        file_name = self.tab_widget.tabText(idx)
        
        if file_name not in self.file_paths:
                return

        file_path = self.file_paths[file_name]

        bounded, mat = extract(file_path)

        qimage = QImage(bounded.data, bounded.shape[1], bounded.shape[0], bounded.strides[0] ,QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qimage)
        scene = QGraphicsScene(graphics_view)
        scene.addPixmap(pixmap)
        graphics_view.setScene(scene)
        graphics_view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        table_widget.setColumnCount(mat.shape[1])
        table_widget.setRowCount(mat.shape[0])

        for i in range(table_widget.columnCount()):
            for j in range(table_widget.rowCount()):
                item = QTableWidgetItem(mat[j, i])
                table_widget.setItem(j, i, item)


    def export(self, table_widget):

        file_path, _ = QFileDialog.getSaveFileName(self, "Choose Save Location", filter="CSV FILES(*.csv)")

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


class ZoomView(QGraphicsView):

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                scale = 1.25
            else:
                scale = 0.85
            self.scale(scale, scale)

    
            
if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
