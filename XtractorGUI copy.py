from PyQt5.QtWidgets import QLabel, QApplication, QMainWindow, QTabWidget, QTabBar, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QGraphicsView, QTableWidgetItem, QPushButton, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap, QImage, QBrush
from PyQt5.QtCore import Qt, QFile, QEvent
from PyQt5.QtWidgets import QGraphicsScene
from Pipeline import extract
import os
import csv
from SplitTab import ZoomView, PageTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle("Xtractor")
        self.setWindowState(Qt.WindowMaximized)

        # Create the tab widget
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.South)
        self.setCentralWidget(self.tab_widget)

        # Create the plus button to add new tabs
        plus_button = QPushButton("+", self)
        plus_button.clicked.connect(self.add_new_tab)

        self.plus_tab = QWidget()
        self.plus_tab.setObjectName("main")
        # Set the background image
        self.plus_tab.setStyleSheet(
            'QWidget#main{background-image:url("background.png"); background-position: center; background-repeat: no-repeat;}')

        # Add the plus button to the tab widget
        self.tab_widget.addTab(self.plus_tab, "")
        self.tab_widget.setTabEnabled(self.tab_widget.count() - 1, False)
        self.tab_widget.tabBar().setTabButton(
            self.tab_widget.count() - 1, QTabBar.RightSide, plus_button)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(
            lambda index: self.tab_widget.removeTab(index))

    def add_new_tab(self, ret=False):
        # Create a new tab widget
        tab = PageTab()

        # Add the tab to the tab widget
        idx = self.tab_widget.count() - 1
        self.tab_widget.insertTab(
            idx, tab, "Tab {}".format(self.tab_widget.count()))
        self.tab_widget.setCurrentIndex(idx)

        if ret:
            return tab


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
