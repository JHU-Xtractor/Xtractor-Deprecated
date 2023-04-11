from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QTabBar, QWidget, QHBoxLayout, QTableWidget, QGraphicsView, QTableWidgetItem, QPushButton, QFileDialog, QSizePolicy, QScrollBar
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter, QImage
from PyQt5.QtCore import Qt, QFile, QEvent
from PyQt5.QtWidgets import QGraphicsScene


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create the vertical layout for the central widget
        vertical_layout = QHBoxLayout(central_widget)

        # Create the tab widget
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.South)

        # Add the initial tab
        self.add_new_tab()

        # Create the plus button to add new tabs
        plus_button = QPushButton("+", self)
        plus_button.clicked.connect(self.add_new_tab)

        # Add the plus button to the tab widget
        self.tab_widget.addTab(QWidget(), "")
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
        table_widget.setRowCount(4)
        table_widget.setColumnCount(3)
        table_widget.setAlternatingRowColors(True)
        table_widget.setShowGrid(True)
        table_widget.setItem(0, 0, QTableWidgetItem("1"))
        table_widget.setItem(1, 0, QTableWidgetItem("2"))
        table_widget.setItem(2, 0, QTableWidgetItem("3"))
        table_widget.setItem(3, 0, QTableWidgetItem("4"))

        layout.addWidget(table_widget)

        # Add the "Add File" button to the tab
        add_file_button = QPushButton("Add File", tab)
        add_file_button.clicked.connect(lambda: self.add_file_to_tab(graphics_view))
        layout.addWidget(add_file_button)

        # Add the tab to the tab widget
        self.tab_widget.insertTab(self.tab_widget.count() - 1, tab, "Tab {}".format(self.tab_widget.count()))

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
