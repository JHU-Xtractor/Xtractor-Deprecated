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

        self.setWindowIcon(QIcon('resources/logo.png'))
        self.setWindowTitle("Xtractor")
        self.setGeometry(300, 300, 800, 600)
        self.setWindowState(Qt.WindowMaximized)

        # Create the central tab bar widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create the vertical layout for the central widget
        main_layout = QVBoxLayout(central_widget)
        self.bar = QTabBar(central_widget)
        self.window = QWidget(central_widget)
        self.window.setObjectName("main")
        self.window.setStyleSheet('QWidget#main{background-image:url("resources/background.png"); background-position: center; background-repeat: no-repeat;}')
        self.bar.setShape(QTabBar.Shape.TriangularSouth)
        vertical_layout = QHBoxLayout(self.window)
        main_layout.addWidget(self.bar)
        main_layout.addWidget(self.window)

        # Create empty dict of file_paths
        self.file_paths = {}
        # Create empty dict for data
        self.data = {}

        # Create the plus button to add new tabs
        self.plus_button = QPushButton("+", self.bar)
        self.plus_button.clicked.connect(self.add_new_tab)

        # Add the plus button to the tab widget
        self.bar.addTab("")
        self.bar.setTabEnabled(self.bar.count() - 1, False)
        self.bar.setTabButton(self.bar.count() - 1, QTabBar.RightSide, self.plus_button)
        self.bar.tabCloseRequested.connect(self.remove_tab)
        self.bar.currentChanged.connect(self.change_tab)
        self.bar.setTabsClosable(True)

    def tabSetup(self):
        # Create the graphics view and add it to the layout
        graphics_view = ZoomView(self.window)

        graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self.window.layout().addWidget(graphics_view)

        # Create the table widget and add it to the layout
        table_widget = QTableWidget(self.window)
        table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.setAlternatingRowColors(True)
        table_widget.setShowGrid(True)

        self.window.layout().addWidget(table_widget)

        toolBarLayout = QVBoxLayout()
        self.window.layout().addLayout(toolBarLayout)
       
        # Add the "Add File" button to the tab
        add_file_button = QPushButton("Add File", self.window)
        add_file_button.clicked.connect(lambda: self.add_file_to_tab(graphics_view))
        toolBarLayout.addWidget(add_file_button)

        # Add the "Extract" button to the tab
        extract_table_button = QPushButton("Extract", self.window)
        extract_table_button.clicked.connect(lambda: self.preExtract(graphics_view, table_widget))
        toolBarLayout.addWidget(extract_table_button)

        # Add the "Extract" button to the tab
        export_table_button = QPushButton("Export", self.window)
        export_table_button.clicked.connect(lambda: self.export(table_widget))
        toolBarLayout.addWidget(export_table_button)

    def remove_tab(self, index):
        layout = self.window.layout()

        self.bar.removeTab(index)
        if self.bar.count() == 1:
            for i in reversed(range(layout.count())):
                w = layout.itemAt(i).widget()
                layout.removeWidget(w)
                w.setParent(None)

    def add_new_tab(self):
        if self.bar.count() == 1:
            self.tabSetup()
        # Add the tab to the tab widget
        idx = self.bar.count() - 1
        self.bar.insertTab(idx, "Tab {}".format(self.bar.count()))
        self.bar.setCurrentIndex(idx)

    def change_tab(self, index):
        return
    
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

                idx = self.bar.currentIndex()
                file_name = os.path.basename(file_path).split('/')[-1]
                self.bar.setTabText(idx, file_name)

                self.file_paths[file_name] = file_path

    
    def preExtract(self, graphics_view, table_widget):
        idx = self.bar.currentIndex()
        file_name = self.bar.tabText(idx)
        
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

        file_path, _ = QFileDialog.getSaveFileName(self, "Choose Save Location", filter="CSV Files(*.csv)")

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
