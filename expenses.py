
import sys
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import (QAction, QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QFileDialog)
from PySide2.QtCharts import QtCharts
import pandas as pd
import numpy as np


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.items = 0

        # Example data
        self._data = pd.DataFrame([[0,1]],columns=['Step','v_ntot'])

        # Left
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Step", "v_ntot"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Chart
        self.chart_view = QtCharts.QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # Right
        self.description = QLineEdit()
        self.price = QLineEdit()
        self.add = QPushButton("Add")
        self.clear = QPushButton("Clear")
        self.quit = QPushButton("Quit")
        self.plot = QPushButton("Plot")
        self.open = QPushButton("Open")

        # Disabling 'Add' button
        self.add.setEnabled(False)

        self.right = QVBoxLayout()
        self.right.setMargin(10)
        self.right.addWidget(QLabel("Description"))
        self.right.addWidget(self.description)
        self.right.addWidget(QLabel("Price"))
        self.right.addWidget(self.price)
        self.right.addWidget(self.add)
        self.right.addWidget(self.plot)
        self.right.addWidget(self.chart_view)
        self.right.addWidget(self.clear)
        self.right.addWidget(self.quit)
        self.right.addWidget(self.open)
        

        # QWidget Layout
        self.layout = QHBoxLayout()

        #self.table_view.setSizePolicy(size)
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.right)

        # Set the layout to the QWidget
        self.setLayout(self.layout)

        # Signals and Slots
        self.add.clicked.connect(self.add_element)
        self.quit.clicked.connect(self.quit_application)
        self.plot.clicked.connect(self.plot_data)
        self.clear.clicked.connect(self.clear_table)
        self.description.textChanged[str].connect(self.check_disable)
        self.price.textChanged[str].connect(self.check_disable)
        self.open.clicked.connect(self.open_file)

        # Fill example data
        self.fill_table()
    
    def read_log(self,file):
        log = {}
        headers = [] 
        run = 0
        start = False
        every = False
        update_header = True
        with open(file) as logfile:
            lines = [line.split() for line in logfile.readlines() if len(line.split()) > 1 ]
            
            for line in lines:
                
                if line[0].lower() == 'run':
                    update_header = True
                    if 'every' in line:
                        every = True
                    run += 1
                    continue
                if line[0].lower() == 'step':
                    start = True
                    if update_header:
                        headers.append(line)
                    update_header = False
                    continue
                if line[0].lower() == 'loop':
                    start = False
                    continue
                if start:
                    try:
                        log['Run '+str(run)].append(np.asarray(line).astype(float))
                    except:
                        log['Run '+str(run)] = [np.asarray(line).astype(float)]
        return headers, log

    @Slot()
    def open_file(self):
        fileNames = QFileDialog.getOpenFileNames(self, "Select one or more files to open",
                                       "~/")
        for thisFile in fileNames[0]:
            if 'log' in thisFile:
                headers, data = self.read_log(thisFile)
                df = pd.DataFrame(data['Run 1'], columns=headers[0])
                self.table.setRowCount(0)
                self.items = 0
                for step, v_ntot in zip(df['Step'],df['v_ntot']):
                    step_item = QTableWidgetItem("{:.2f}".format(step))
                    vntot_item = QTableWidgetItem("{:.2f}".format(v_ntot))
                    vntot_item.setTextAlignment(Qt.AlignRight)
                    self.table.insertRow(self.items)
                    self.table.setItem(self.items, 0, step_item)
                    self.table.setItem(self.items, 1, vntot_item)
                    self.items += 1
            if 'csv' in thisFile:
                pass
            if 'profile' in thisFile:
                pass
    
    @Slot()
    def add_element(self):
        des = self.description.text()
        price = self.price.text()

        self.table.insertRow(self.items)
        description_item = QTableWidgetItem(des)
        price_item = QTableWidgetItem("{:.2f}".format(float(price)))
        price_item.setTextAlignment(Qt.AlignRight)

        self.table.setItem(self.items, 0, description_item)
        self.table.setItem(self.items, 1, price_item)

        self.description.setText("")
        self.price.setText("")

        self.items += 1

    @Slot()
    def check_disable(self, s):
        if not self.description.text() or not self.price.text():
            self.add.setEnabled(False)
        else:
            self.add.setEnabled(True)

    @Slot()
    def plot_data(self):
        # Get table information
        series = QtCharts.QLineSeries()
        for i in range(self.table.rowCount()):
            text = float(self.table.item(i, 0).text())
            number = float(self.table.item(i, 1).text())
            series.append(text, number)

        chart = QtCharts.QChart()
        chart.addSeries(series)
        #chart.legend().setAlignment(Qt.AlignLeft)

        axis_x = QtCharts.QValueAxis()
        axis_x.setTickCount(10)
        axis_x.setLabelFormat("%.2f")
        axis_x.setTitleText("Step")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QtCharts.QValueAxis()
        axis_y.setTickCount(10)
        axis_y.setLabelFormat("%.2f")
        axis_y.setTitleText("v_ntot")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)


        self.chart_view.setChart(chart)

    @Slot()
    def quit_application(self):
        QApplication.quit()

    def fill_table(self, data=None):
        data = self._data if not data else data
        for step, v_ntot in zip(data['Step'],data['v_ntot']):
            step_item = QTableWidgetItem("{:.2f}".format(step))
            vntot_item = QTableWidgetItem("{:.2f}".format(v_ntot))
            vntot_item.setTextAlignment(Qt.AlignRight)
            self.table.insertRow(self.items)
            self.table.setItem(self.items, 0, step_item)
            self.table.setItem(self.items, 1, vntot_item)
            self.items += 1

    @Slot()
    def clear_table(self):
        self.table.setRowCount(0)
        self.items = 0


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Tutorial")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)
        self.setCentralWidget(widget)

    @Slot()
    def exit_app(self, checked):
        QApplication.quit()


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QWidget
    widget = Widget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec_())
