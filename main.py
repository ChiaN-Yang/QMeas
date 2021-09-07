#!/usr/bin/env python
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QTreeWidgetItemIterator, QApplication, QMainWindow, QTableWidgetItem, QDialog, QApplication
import pyqtgraph as pg
import pyqtgraph.exporters
from libs.visa_resource_manager import Ui_MainWindow
from libs.control_option import Ui_Dialog
from libs.read_option import Ui_Dialog as read_Ui_Dialog
import sys
import sip
import pyvisa as visa
import numpy as np
import os
from datetime import datetime
from libs.load_driver import load_drivers
import qdarkstyle
from libs.txtFunction import txtUpdate
from time import sleep
from libs.time_measurement import TimeMeasurement


class MainWindow(QMainWindow):
    """Main class"""
    # pointer
    name_count = 1
    row_count = 1
    read_row_count = 1
    click = 1
    time_unit = 0.1  # 0.1s

    # instruments
    instruments = []
    instruments_control = []
    instruments_read = []
    options_control = []
    options_read = []

    # PlotItem lines
    data_line = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # control panel & read panel
        self.control_panel = ControlPanel()
        self.read_panel = ReadlPanel()

        # Pre-run functions
        self.visaList()
        self.intrumentList()

        # page 1
        # Buttons
        self.ui.pushButton.clicked.connect(self.visaList)
        self.ui.pushButton_2.clicked.connect(self.connection)
        self.ui.pushButton_10.clicked.connect(self.deleteConnectedInstrument)
        # Tables
        self.ui.tableWidget.setColumnWidth(0, 100)
        self.ui.tableWidget.setColumnWidth(1, 200)

        # page 2
        # Buttons
        self.ui.pushButton_7.clicked.connect(self.read_panel.show)
        self.read_panel.sub_1_ui.pushButton_5.clicked.connect(
            self.readConfirm)
        self.read_panel.sub_1_ui.pushButton_5.clicked.connect(
            self.read_panel.close)
        self.read_panel.sub_1_ui.pushButton_6.clicked.connect(
            self.read_panel.close)

        self.ui.pushButton_3.clicked.connect(self.control_panel.show)
        self.control_panel.sub_ui.pushButton_9.clicked.connect(
            self.addLevel)
        self.control_panel.sub_ui.pushButton_9.clicked.connect(
            self.control_panel.close)
        self.control_panel.sub_ui.pushButton_8.clicked.connect(
            self.chooseAddChild)
        self.control_panel.sub_ui.pushButton_8.clicked.connect(
            self.control_panel.close)
        self.control_panel.sub_ui.pushButton_6.clicked.connect(
            self.control_panel.close)

        self.ui.pushButton_8.clicked.connect(self.deleteReadRow)
        self.ui.pushButton_9.clicked.connect(self.chooseDelete)
        self.ui.pushButton_5.clicked.connect(self.timeGo)
        self.ui.pushButton_11.clicked.connect(self.timeStop)
        self.ui.pushButton_26.clicked.connect(self.addTimeMeasurement)
        # check box
        self.control_panel.sub_ui.checkBox.stateChanged.connect(
            self.checkFunctionWaitingTime)

        # Tables
        self.ui.tableWidget_2.cellClicked.connect(self.showMethod)

        # treeWidget init
        self.tree = self.ui.treeWidget

        # page 3
        # Buttons
        self.ui.pushButton_13.clicked.connect(self.displayCursorCrossHair)
        self.ui.pushButton_13.clicked.connect(self.autoPlotRange)
        # Tables
        self.ui.tableWidget_5.cellClicked.connect(self.lineDisplaySwitch)
        # plot widget
        # TODO: add the real time x y coordinate the corner

        pg.setConfigOptions(antialias=False)
        self.plt = self.ui.graphWidget
        # viewbox setting
        self.viewbox = self.plt.getViewBox()
        self.viewbox.disableAutoRange()  # Side note: this function can be connected
        # to a button, e.g., AUTO button = enable it first and disable it
        # plot setting
        self.plt.showGrid(x=True, y=True, alpha=1)
        self.plt.setLabel('bottom', '   ')
        self.plt.setLabel('left', '   ')

        # Menu
        self.ui.retranslateUi(self)
        self.ui.actionQuit.setShortcut('Ctrl+Q')
        self.ui.actionQuit.triggered.connect(self.timeStop)
        self.ui.actionQuit.triggered.connect(app.exit)
        self.ui.actionQuit.triggered.connect(self.close)

        # Set Window Icon
        self.setWindowIcon(QIcon('Qfort.png'))

        # Set Window style
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # =============================================================================
    # Page 1
    # =============================================================================
    def visaList(self):
        """detect available address"""
        resource_manager = visa.ResourceManager()
        self.pyvisa_list = resource_manager.list_resources()
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(self.pyvisa_list)

    def intrumentList(self):
        """detect available drivers"""
        self.driver_list = load_drivers()
        self.ui.listWidget_2.clear()
        self.ui.listWidget_2.addItems(self.driver_list.keys())

    def pageOneInformation(self, string):
        """put some word in the information board"""
        self.ui.textBrowser.append(str(string))

    def deleteConnectedInstrument(self):
        row = self.ui.tableWidget.currentRow()
        self.ui.tableWidget.removeRow(row)
        self.ui.tableWidget_2.removeRow(row)
        self.row_count -= 1
        self.instruments.pop(row)

    def connection(self):
        """add instruments into table_instrList"""
        # Get info from lists and construct new object later
        visa_address = self.ui.listWidget.currentItem().text()
        instrument_type = self.ui.listWidget_2.currentItem().text()
        instrument_personal_name = self.ui.lineEdit.text()

        row_len = self.ui.tableWidget.rowCount()
        # Check existance
        if self.ui.tableWidget.findItems(visa_address, Qt.MatchExactly) != [] or \
                self.ui.tableWidget.findItems(instrument_personal_name, Qt.MatchExactly) != []:
            self.pageOneInformation('This VISA address or name has been used.')
        else:
            if instrument_type in self.driver_list.keys():
                try:
                    instrument_name = f'{instrument_type}_{self.name_count}'
                    self.name_count += 1

                    instrument = self.driver_list[instrument_type](
                        visa_address)
                    instrument.setProperty(
                        visa_address, instrument_name, instrument_type)
                    self.instruments.append(instrument)

                    # TODO: add some condition to check if Connection is successful
                    self.pageOneInformation(
                        f'self.{instrument_name} = {instrument_type}("{visa_address}")')
                    self.pageOneInformation(
                        f'{instrument_type} has been connected successfully.')
                    # TODO: add initialization option on messagebox and show the related info

                    # Add new row if necessary
                    if self.row_count > row_len:
                        self.ui.tableWidget.insertRow(row_len)
                        self.ui.tableWidget_2.insertRow(row_len)

                    # Assign varibales to current var
                    instrument_property = [
                        instrument_personal_name, instrument_type, visa_address]
                    for i, p in enumerate(instrument_property):
                        if p == '':
                            p = instrument_name
                        # Update the info to the table in page 1
                        self.ui.tableWidget.setItem(
                            self.row_count - 1, i, QTableWidgetItem(p))

                    # Update the left top table in page 2
                    if instrument_personal_name == '':
                        instrument_personal_name = instrument_name
                    self.ui.tableWidget_2.setItem(
                        self.row_count - 1, 0, QTableWidgetItem(instrument_personal_name))
                    self.ui.tableWidget_2.setItem(
                        self.row_count - 1, 1, QTableWidgetItem(instrument_type))
                    self.row_count += 1

                except visa.VisaIOError or AttributeError:
                    self.pageOneInformation(
                        "%s connect fail" % instrument_type)

    # =============================================================================
    # Page 2
    # =============================================================================

    def pageTwoInformation(self, string):
        self.ui.textBrowser_2.append(str(string))

    def deleteReadRow(self):
        row = self.ui.tableWidget_4.currentRow()
        self.ui.tableWidget_4.removeRow(row)
        self.ui.tableWidget_5.removeColumn(row)
        self.read_row_count -= 1
        self.instruments_read.pop(row)

    def showMethod(self):
        row = self.ui.tableWidget_2.currentRow()
        instrument = self.instruments[row]
        self.ui.listWidget_3.clear()
        # show the method of the chosen itesm to the list
        self.ui.listWidget_3.addItems(instrument.METHOD)
        # TODO: add the waiting-time measurement to the option

    def readConfirm(self):
        # Get the necessary info of the chosen item
        row = self.ui.tableWidget_2.currentRow()
        instrument_name = self.ui.tableWidget_2.item(row, 0).text()
        instrument_type = self.ui.tableWidget_2.item(row, 1).text()
        read_method = self.ui.listWidget_3.currentItem().text()
        magnification = self.read_panel.sub_1_ui.lineEdit_2.text()
        Unit = self.read_panel.sub_1_ui.lineEdit_3.text()

        # Add new row if necessary
        row_len = self.ui.tableWidget_4.rowCount()
        if self.read_row_count > row_len:
            self.ui.tableWidget_4.insertRow(row_len)
            self.ui.tableWidget_5.insertColumn(row_len + 1)

        # Assign the variables to the table in page 2
        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 0, QTableWidgetItem(instrument_name))
        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 1, QTableWidgetItem(instrument_type))
        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 2, QTableWidgetItem(read_method))
        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 3, QTableWidgetItem(magnification))
        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 4, QTableWidgetItem(Unit))

        # initialize the blocks in the read option
        self.read_panel.sub_1_ui.lineEdit_2.setText("1")
        self.read_panel.sub_1_ui.lineEdit_3.clear()

        # Assign the variables to the table in page 3
        self.ui.tableWidget_5.setItem(
            0, self.read_row_count, QTableWidgetItem(instrument_name))
        self.ui.tableWidget_5.setItem(
            1, self.read_row_count, QTableWidgetItem(read_method))

        method_row_len = self.ui.tableWidget_4.rowCount()
        self.pageTwoInformation(method_row_len)

        self.read_row_count += 1

        self.instruments[row].setReadOption(magnification)
        self.instruments_read.append(self.instruments[row])
        self.options_read.append(read_method)

    def switchToPlotTab(self):
        self.ui.tabWidget.setCurrentIndex(2)

    def addTimeMeasurement(self):
        """ Provide another option to do the time measurement """
        wait_time = self.ui.lineEdit_5.text()

        if wait_time.isnumeric():
            self.root = QTreeWidgetItem(self.tree)
            self.root.setText(0, '0')
            self.root.setFlags(self.root.flags() | Qt.ItemIsUserCheckable)
            self.root.setCheckState(0, Qt.Checked)
            self.root.setExpanded(True)
            self.updateTimeMeasurement(self.root)
            self.tree_num, self.leve_position, self.child_num, self.check = self.checkState()
        else:
            self.pageTwoInformation(
                'Time measurement - Please enter a number.')

        self.ui.lineEdit_5.clear()
# =============================================================================
#         # Add new row if necessary
#
#         instrument = TimeMeasurement(wait_time)
#
#         self.instruments_control.insert(row+1, instrument)
#         self.options_control.insert(row+1, None)
# =============================================================================

    # treeWidget
    def addLevel(self, level_name):
        self.root = QTreeWidgetItem(self.tree)
        self.root.setText(0, '0')
        self.root.setFlags(self.root.flags() | Qt.ItemIsUserCheckable)
        self.root.setCheckState(0, Qt.Checked)
        self.root.setExpanded(True)
        self.updateInfo(self.root)
        self.control_panel.sub_ui.checkBox.setChecked(False)
        self.tree_num, self.leve_position, self.child_num, self.check = self.checkState()

    def chooseAddChild(self):
        # QTreeWidgetItem括號內放的物件是作為基礎(root)，child會往下一層放
        item = self.tree.currentItem()
        if self.tree.indexOfTopLevelItem(item) >= 0:
            target_item = item
        else:
            _, _, child_num = self.getIndexs(item.parent())
            target_item = item.parent().child(child_num - 1)

        self.child1 = QTreeWidgetItem(target_item)
        self.child1.setText(0, '1')
        self.child1.setExpanded(True)
        self.updateInfo(self.child1)
        self.child1.setFlags(self.child1.flags() | Qt.ItemIsUserCheckable)
        self.child1.setCheckState(0, Qt.Checked)
        self.control_panel.sub_ui.checkBox.setChecked(False)
        self.tree_num, self.leve_position, self.child_num, self.check = self.checkState()

    def checkFunctionWaitingTime(self):
        if self.control_panel.sub_ui.checkBox.isChecked():
            self.control_panel.sub_ui.lineEdit_5.setEnabled(True)
            self.control_panel.sub_ui.lineEdit_5.setText('2')

        else:
            self.control_panel.sub_ui.lineEdit_5.setEnabled(False)
            self.control_panel.sub_ui.lineEdit_5.setText('0')

    def updateInfo(self, item):
        row = self.ui.tableWidget_2.currentRow()
        Ins_name = self.ui.tableWidget_2.item(row, 0).text()
        Ins_type = self.ui.tableWidget_2.item(row, 1).text()
        control_method = self.ui.listWidget_3.currentItem().text()

        # TODO: restrict the the value to integer only or something related to the unit
        target = self.control_panel.sub_ui.lineEdit_2.text()
        speed = self.control_panel.sub_ui.lineEdit_3.text()

        # check box
        waiting_time = self.control_panel.sub_ui.lineEdit_5.text()
        control_list = [Ins_name, Ins_type,
                        control_method, target, speed, waiting_time]

        for i, element in enumerate(control_list):
            item.setText((i+1), element)

        self.instruments[row].setControlOption(target, speed, self.time_unit)
        self.instruments_control.append(self.instruments[row])
        self.options_control.append(control_method)

    def updateTimeMeasurement(self, item):
        Ins_name = 'Time Meas'
        Ins_type = 'Timer'
        control_method = ' - '

        # TODO: restrict the the value to integer only or something related to the unit
        target = self.ui.lineEdit_5.text()
        speed = '-'
        control_list = [Ins_name, Ins_type, control_method, target, speed]
        for i, element in enumerate(control_list):
            item.setText((i+1), element)

        # TODO: discuss this part to add info to list
        # self.instruments[row].setControlOption(target, speed, self.time_unit)
        # self.instruments_control.append(self.instruments[row])
        # self.options_control.append(control_method)

    def checkState(self):
        global checklist
        iterator = QTreeWidgetItemIterator(self.tree)
        checklist = []
        for _ in range(6):
            checklist.append([])

        while iterator.value():
            item = iterator.value()
            treeindex, childindex, child_num = self.getIndexs(item)
            checkstate = item.checkState(0)

            # tree index
            checklist[0].append(treeindex)
            # item's child number
            checklist[1].append(child_num)
            # item index in parents view
            checklist[2].append(childindex)
            # ischild or not, if not, it shows how many child it has; if yes, it shows -1,
            checklist[3].append(child_num)
            # check
            checklist[4].append(checkstate)
            # temp
            checklist[5].append(treeindex)

            iterator += 1

        for i in range(len(checklist[3])):
            if checklist[0][i] == -1:
                checklist[0][i] = checklist[0][i-1]
            else:
                checklist[0][i] = checklist[0][i]

            if checklist[2][i] == -1:
                checklist[2][i] = 0

            if checklist[1][i] == 0 and checklist[5][i] == -1:
                checklist[3][i] = checklist[5][i]
        del(checklist[5])
        del(checklist[1])

        return checklist[0], checklist[1], checklist[2], checklist[3]

    def getIndexs(self, item):
        """ Returns Current top level item and child index.
            If no child is selected, returns -1. 
        """
        # TODO: check if two level will still work
        # Check if top level item is selected or child selected
        if self.tree.indexOfTopLevelItem(item) == -1:
            return self.tree.indexOfTopLevelItem(item), item.parent().indexOfChild(item), item.childCount()
        else:
            return self.tree.indexOfTopLevelItem(item), -1, item.childCount()

    def chooseDelete(self):
        item = self.tree.currentItem()
        sip.delete(item)
    # =============================================================================
    # Page 3
    # =============================================================================

    def pageThreeInformation(self, string):
        self.ui.textBrowser_3.clear
        self.ui.textBrowser_3.append(str(string))

    def displayCursorCrossHair(self):
        """Add crosshair lines."""
        if self.ui.pushButton_13.isChecked():
            self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
            self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
            self.ui.graphWidget.addItem(self.crosshair_v, ignoreBounds=True)
            self.ui.graphWidget.addItem(self.crosshair_h, ignoreBounds=True)
            self.proxy = pg.SignalProxy(self.ui.graphWidget.scene(
            ).sigDisplayCursorCoordinate, rateLimit=60, slot=self.displayCursorCoordinate)
        else:
            self.ui.graphWidget.removeItem(self.crosshair_h)
            self.ui.graphWidget.removeItem(self.crosshair_v)
            self.proxy = []

    def displayCursorCoordinate(self, e):
        pos = e[0]
        if self.ui.graphWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.ui.graphWidget.getPlotItem().vb.mapSceneToView(pos)
            self.crosshair_v.setPos(mousePoint.x())
            self.crosshair_h.setPos(mousePoint.y())

    def autoPlotRange(self):
        # TODO: auto view when clicking is still not working
        self.viewbox.enableAutoRange()
        self.viewbox.disableAutoRange()

    # =============================================================================
    #  Start and stop function
    # =============================================================================

    def timeGo(self):
        """ TimeGo is the first activating function when "run" the project
            At first, the name of the project will be test if it has existed.
            if you ignore the warning and choose overwrite the file, the project
            will start immediately. The txt file as well as the plot items will
            be created.
        """
        self.name = self.ui.lineEdit_2.text()
        if self.name == '':
            QMessageBox.information(
                self, "Wrong!.", "Please type the file name.")
        else:
            self.full_name = f'{self.name}.txt'
            List = os.listdir()
            if self.full_name in List:
                reply = QMessageBox.information(
                    self, "Wrong!.", "The file has existed. Do you want to overwrite it?",
                    QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
                if reply == QMessageBox.Close:
                    QMessageBox.information(
                        self, "Wrong!.", "Please adjust the file name.")
                elif reply == QMessageBox.Ok:
                    self.procedureGo()
            else:
                self.procedureGo()

    def procedureGo(self):
        self.switchToPlotTab()
        # plotlines init
        self.createEmptyLines()
        self.lineDisplaySwitchCreat()
        # porcedure start
        self.procedure = Procedure(
            self.instruments_control, self.instruments_read)
        self.procedure.schedule(
            self.tree_num, self.child_num, self.leve_position)
        self.procedure.startMeasure()
        self.s_time = datetime.now()

    def timeStop(self):
        # time stop
        try:
            self.procedure.stopMeasure()
        except:
            pass

    # =============================================================================
    # plot setting
    # =============================================================================

    def createEmptyLines(self):
        """
        creat the plotDataItem as data_line_%d where %d = 0, 1, 2... (reference)
        the x y value will be set later within the function plot_update()
        """
        self.plt.clear()
        for i in range(len(self.instruments_read)):
            self.data_line.append(self.ui.graphWidget.plot([]))
        print('creat line')

    def plotUpdate(self, n, x, y_n):
        # setData to the PlotItems
        if self.switch_list[n] == 1:
            self.data_line[n].setData(x, y_n, pen=pg.mkPen(pg.intColor(n+1)))
        else:
            self.data_line[n].setData([])

    def axisUpdate(self, x_show, y_show):
        # update x title (instrument name and method)
        # insturement name
        self.ui.tableWidget_5.setItem(
            0, 0, QTableWidgetItem(f'{x_show[1]}'))
        # method
        self.ui.tableWidget_5.setItem(
            1, 0, QTableWidgetItem(f'{x_show[2]}'))

        # update x value
        self.ui.tableWidget_5.setItem(
            2, 0, QTableWidgetItem(f'{x_show[0]:g}'))
        # update y value
        print('len_upDate')
        print(len(self.instruments_read))
        print('x_show')
        print(x_show)
        print('y_show')
        print(y_show)

        for i in range(len(self.instruments_read)):
            self.ui.tableWidget_5.setItem(
                2, (i + 1), QTableWidgetItem(f'{y_show[i]:g}'))

    def lineDisplaySwitchCreat(self):
        global switch_list
        switch_list = []
        self.switch_list = []
        for _ in range(len(self.instruments_read)):
            self.switch_list.append(1)
            switch_list.append(1)

    def lineDisplaySwitch(self):
        """ this function is connected to tableWidget_5 on page 3
            the function activates whenever the tablewidge_5 is clicked
        """
        # TODO: this function is not well working. it needs to establish multiple switch to each channel
        col = self.ui.tableWidget_5.currentColumn()
        if col == 0:
            return
        else:
            self.switch_list[col - 1] = self.switch_list[col - 1]*(-1)


# =============================================================================
# Page 2 subwindow Control option panel
# =============================================================================
class ControlPanel(QDialog):
    def __init__(self):
        super(ControlPanel, self).__init__()
        self.sub_ui = Ui_Dialog()
        self.sub_ui.setupUi(self)


class ReadlPanel(QDialog):
    def __init__(self):
        super(ReadlPanel, self).__init__()
        self.sub_1_ui = read_Ui_Dialog()
        self.sub_1_ui.setupUi(self)


class Procedure():
    """this class is used to perform experiments"""
    control_sequence = []
    control_pointer = -1
    linspacer_sequence = []
    linspacer_pointer = 0

    def __init__(self, instruments_control, instruments_read):
        self.instruments_control = instruments_control
        self.instruments_read = instruments_read
        self.read_len = len(instruments_read)
        self.options_control = window.options_control
        self.options_read = window.options_read
        # Timer
        self.sequence_num = 0

        # open instrument
        for n, instrument in enumerate(instruments_control):
            instrument.performOpen(self.options_control[n])

    def schedule(self, tree_num, child_num, leve_position):
        """ return [tree1, tree2, tree3]
            tree view
            [ [child_num, leve_position, instrument, option]
              [child_num, leve_position, instrument, option]
              [child_num, leve_position, instrument, option] ]
        """
        # Know how many trees there are
        tree_total = max(tree_num) + 1

        # Create empty list to store tree info
        # [[], []]
        info_list = []
        for _ in range(tree_total):
            info_list.append([])

        for n, i in enumerate(tree_num):
            info_list[i].append(
                [child_num[n], leve_position[n], self.instruments_control[n], self.options_control[n]])

        for i in info_list:
            self.buildTree(i)

    def buildTree(self, info_tree):
        """put [instruments, option] into [level_0, level_1, level_2]"""
        # info_tree: [child_num, leve_position, instrument, method]
        level = [[], [], []]
        # level = [level0, level1, level2]  level0 = [[instrument,method], [instrument,method]...]
        level_count = 0
        # put instrument in level
        for n, info in enumerate(info_tree):
            if info[0] == -1:
                continue
            level[level_count].append([info_tree[n][2], info_tree[n][3]])
            level_count += 1

            if info[0] != 0:
                for i in range(info[0]):
                    level[level_count].append(
                        [info_tree[n+1+i][2], info_tree[n+1+i][3]])

            if level[0] and level[1] and level[2]:
                for i in level[0]:  # i = [instrument,method]
                    self.control_sequence.append(i)
                    for j in level[1]:
                        self.control_sequence.append(j)
                        for k in level[2]:
                            self.control_sequence.append(k)

            elif level[0] and level[1] and not level[2]:
                for i in level[0]:
                    self.control_sequence.append(i)
                    for j in level[1]:
                        self.control_sequence.append(j)

            elif level[0] and not level[1] and not level[2]:
                for i in level[0]:
                    self.control_sequence.append(i)

    def startMeasure(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.measure)
        self.time_unit = window.time_unit * self.read_len
        self.renewLinspacer()
        self.timer.start(100)  # self.time_unit

    def renewLinspacer(self):
        self.control_pointer += 1
        if self.control_pointer < len(self.control_sequence):
            instrument_method = self.control_sequence[self.control_pointer]
            instrument_control = instrument_method[0]
            method = instrument_method[1]
            self.linspacer_sequence = instrument_control.experimentLinspacer(
                method)

            self.x, self.y = self.createEmptyDataSet()
        else:
            self.stopMeasure()

    def measure(self):
        if self.linspacer_pointer < len(self.linspacer_sequence):
            # creat the empty 1D list x and 2D list y to record the value
            instrument_method = self.control_sequence[self.control_pointer]
            instrument_control = instrument_method[0]
            method = instrument_method[1]
            name = instrument_control.instrumentName()
            value = self.linspacer_sequence[self.linspacer_pointer]

            y_show = []
            name_txt = []
            method_txt = []

            set_value = instrument_control.performSetValue(method, value)
            x_show = [set_value, name, method]
            self.x.append(set_value)
            name_txt.append(name)
            method_txt.append(method)

            for n, instrument_read in enumerate(self.instruments_read):
                read_value = instrument_read.performGetValue(
                    self.options_read[n])
                y_show.append(read_value)
                self.y[n].append(read_value)
                name_txt.append(instrument_read.instrumentName())
                method_txt.append(self.options_read[n])
                window.plotUpdate(n, self.x, self.y[n])
                QApplication.processEvents()

            txtUpdate(self.sequence_num, name_txt, method_txt, x_show, y_show)
            # x_show = [value, name , method]
            window.axisUpdate(x_show, y_show)

            self.linspacer_pointer += 1

        elif self.control_pointer < len(self.control_sequence)-1:
            self.renewLinspacer()
            self.linspacer_pointer = 0
            self.measure()
        else:
            self.linspacer_pointer = 0
            self.stopMeasure()

    def createEmptyDataSet(self):
        x = []
        y = []
        for _ in range(self.read_len):
            y.append([])
        return x.copy(), y.copy()

    def stopMeasure(self):
        self.timer.stop()
        self.sequence_num = 0


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
