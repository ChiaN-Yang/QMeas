#!/usr/bin/env python
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QObject
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTreeWidgetItem, \
    QTreeWidgetItemIterator, QApplication, QMainWindow, QTableWidgetItem, QDialog
import pyqtgraph as pg
import pyqtgraph.exporters
from ui.main_window import Ui_MainWindow
from ui.control_option import Ui_Dialog
from ui.read_option import Ui_Dialog as read_Ui_Dialog
import sys
from PyQt5 import sip
import pyvisa as visa
import numpy as np
import os
from datetime import datetime
from lib.load_driver import load_drivers
from lib.txt_function import TxtFunction
from lib.time_measurement import TimeMeasurement
import qdarkstyle
from time import sleep
import nidaqmx.system
from PIL import ImageQt
import logging

# logging.basicConfig(stream=sys.stderr, level=logging.INFO)   # debug mode


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
    instruments_read = []
    instruments_magnification = []
    options_control = []
    options_read = []

    # save plot count
    save_plot_count = 0
    # PlotItem lines
    data_line = []
    saved_line = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # control panel & read panel
        self.control_panel = ControlPanel()
        self.read_panel = ReadlPanel()

        # Pre-run functions
        try:
            self.visaList()
            self.intrumentList()
        except:
            logging.error('detect available address fail')

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
        self.ui.pushButton_7.clicked.connect(self.readPanelShow)

        self.read_panel.sub_1_ui.pushButton_5.clicked.connect(
            self.readConfirm)
        self.read_panel.sub_1_ui.pushButton_5.clicked.connect(
            self.read_panel.close)
        self.read_panel.sub_1_ui.pushButton_6.clicked.connect(
            self.read_panel.close)

        self.ui.pushButton_3.clicked.connect(self.readPanelShow)
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
        self.ui.pushButton_26.clicked.connect(self.timeAddLevel)
        self.ui.pushButton_27.clicked.connect(self.timeAddChild)
        self.ui.pushButton_4.clicked.connect(self.folderMessage)
        # folder Path
        self.cwd = os.getcwd()

        # check box
        self.control_panel.sub_ui.checkBox.stateChanged.connect(
            self.checkFunctionIncrement)

        # Tables
        self.ui.tableWidget_2.cellClicked.connect(self.showMethod)

        # treeWidget init
        self.tree = self.ui.treeWidget
        self.tree.itemClicked.connect(self.checkState)

        # page 3
        # Buttons
        self.ui.pushButton_13.clicked.connect(self.displayCursorCrossHair)
        self.ui.pushButton_13.clicked.connect(self.autoPlotRange)
        self.ui.pushButton_11.clicked.connect(self.procedureStop)
        self.ui.pushButton_15.clicked.connect(self.procedureResumePause)
        self.ui.pushButton_17.clicked.connect(self.procedureQuitLoop)
        self.ui.pushButton_14.clicked.connect(self.procedureQuitSweep)
        self.ui.pushButton_16.clicked.connect(self.plot_save)

        # Tables
        self.ui.tableWidget_5.cellClicked.connect(self.lineDisplaySwitch)
        # plot widget
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
        self.ui.actionQuit.triggered.connect(self.shutdownInstruments)
        self.ui.actionQuit.triggered.connect(app.exit)
        self.ui.actionQuit.triggered.connect(self.close)

        # Set Window Icon
        self.setWindowIcon(QIcon('./ui/Qfort.png'))

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

        # DAQ
        # only one daq is available now 20210916
        system = nidaqmx.system.System.local()
        for i, device in enumerate(system.devices):
            if i > 0:
                self.ui.listWidget.addItem(device.name)
        self.ui.listWidget.addItem("default")

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
        self.ui.lineEdit.clear()

    # =============================================================================
    # Page 2
    # =============================================================================

    def pageTwoInformation(self, string):
        self.ui.textBrowser_2.append(str(string))

    def readPanelShow(self):
        # self.pageTwoInformation(self.ui.listWidget_3.currentItem())
        if self.ui.listWidget_3.currentItem() == None:
            self.pageTwoInformation('Please select a method.')
        else:
            self.read_panel.show()

    def controlPanelShow(self):
        # self.pageTwoInformation(self.ui.listWidget_3.currentItem())
        if self.ui.listWidget_3.currentItem() == None:
            self.pageTwoInformation('Please select a method.')
        else:
            self.control_panel.show()

    def deleteReadRow(self):
        row = self.ui.tableWidget_4.currentRow()
        self.ui.tableWidget_4.removeRow(row)
        self.ui.tableWidget_5.removeColumn(row+1)
        self.read_row_count -= 1
        self.instruments_read.pop(row)
        self.options_read.pop(row)

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

        self.instruments_read.append(self.instruments[row])
        self.options_read.append(read_method)
        self.instruments_magnification.append(int(magnification))

    def switchToPlotTab(self):
        self.ui.tabWidget.setCurrentIndex(2)

    def timeAddLevel(self):
        """ Provide another option to do the time measurement """
        wait_time = self.ui.lineEdit_5.text()

        if wait_time.isnumeric():
            self.root = QTreeWidgetItem(self.tree)
            self.root.setText(0, '0')
            self.root.setFlags(self.root.flags() | Qt.ItemIsUserCheckable)
            self.root.setCheckState(0, Qt.Checked)
            self.root.setExpanded(True)
            self.updateTimeMeasurement(self.root)
            self.checkState()

        else:
            self.pageTwoInformation(
                'Time measurement - Please enter a number.')

        self.ui.lineEdit_5.clear()

    def timeAddChild(self):
        """ Provide another option to do the time measurement """
        wait_time = self.ui.lineEdit_5.text()

        if wait_time.isnumeric():
            item = self.tree.currentItem()
            self.child1 = QTreeWidgetItem(item)
            self.child1.setText(0, '1')
            self.child1.setExpanded(True)
            self.updateTimeMeasurement(self.child1)
            self.child1.setFlags(self.child1.flags() | Qt.ItemIsUserCheckable)
            self.child1.setCheckState(0, Qt.Checked)
            self.control_panel.sub_ui.checkBox.setChecked(False)
            self.checkState()
        else:
            self.pageTwoInformation(
                'Time measurement - Please enter a number.')

        self.ui.lineEdit_5.clear()

    # treeWidget
    def addLevel(self, level_name):
        self.root = QTreeWidgetItem(self.tree)
        self.root.setText(0, '0')
        self.root.setFlags(self.root.flags() | Qt.ItemIsUserCheckable)
        self.root.setCheckState(0, Qt.Checked)
        self.root.setExpanded(True)
        self.updateInfo(self.root)
        self.control_panel.sub_ui.checkBox.setChecked(False)
        self.control_panel.sub_ui.lineEdit_5.setText('0')
        self.checkState()

    def chooseAddChild(self):
        # QTreeWidgetItem括號內放的物件是作為基礎(root)，child會往下一層放
        item = self.tree.currentItem()
        if self.tree.indexOfTopLevelItem(item) >= 0:
            target_item = item
        else:
            _, _, child_num, _, _, _ = self.getIndexs(item.parent())
            target_item = item.parent().child(child_num - 1)

        self.child1 = QTreeWidgetItem(target_item)
        self.child1.setText(0, '1')
        self.child1.setExpanded(True)
        self.updateInfo(self.child1)
        self.child1.setFlags(self.child1.flags() | Qt.ItemIsUserCheckable)
        self.child1.setCheckState(0, Qt.Checked)
        self.control_panel.sub_ui.checkBox.setChecked(False)
        self.control_panel.sub_ui.lineEdit_5.setText('0')
        self.checkState()

    def checkFunctionIncrement(self):
        if self.control_panel.sub_ui.checkBox.isChecked():
            self.control_panel.sub_ui.lineEdit_5.setEnabled(True)

        else:
            self.control_panel.sub_ui.lineEdit_5.setEnabled(False)

    def updateInfo(self, item):
        row = self.ui.tableWidget_2.currentRow()
        Ins_name = self.ui.tableWidget_2.item(row, 0).text()
        Ins_type = self.ui.tableWidget_2.item(row, 1).text()
        control_method = self.ui.listWidget_3.currentItem().text()

        # TODO: restrict the the value to integer only or something related to the unit
        target = self.control_panel.sub_ui.lineEdit_2.text()
        speed = self.control_panel.sub_ui.lineEdit_3.text()

        # check box
        increment = self.control_panel.sub_ui.lineEdit_5.text()
        control_list = [Ins_name, Ins_type,
                        control_method, target, speed, increment]

        for i, element in enumerate(control_list):
            item.setText((i+1), element)
        item.setText(7, str(row))

    def updateTimeMeasurement(self, item):
        row = str(-1)
        Ins_name = 'Time Meas'
        Ins_type = 'Timer'
        control_method = '-'

        # TODO: restrict the the value to integer only or something related to the unit
        target = self.ui.lineEdit_5.text()
        speed = '-'
        increment = '-'
        control_list = [Ins_name, Ins_type,
                        control_method, target, speed, increment]
        for i, element in enumerate(control_list):
            item.setText((i+1), element)
        item.setText(7, row)

    def checkState(self):
        global checklist
        iterator = QTreeWidgetItemIterator(self.tree)
        checklist = []
        for _ in range(11):
            checklist.append([])

        while iterator.value():
            item = iterator.value()
            treeindex, childindex, child_num, method, ins_label, target, speed, increment = self.getIndexs(
                item)
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
            # method
            checklist[6].append(method)
            # ins_label
            checklist[7].append(ins_label)
            # target
            checklist[8].append(target)
            # speed
            checklist[9].append(speed)
            # increment
            checklist[10].append(increment)

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
        self.tree_num, self.leve_position, self.child_num, self.check, self.method, self.ins_label, self.target, self.speed, self.increment = checklist[
            0], checklist[1], checklist[2], checklist[3], checklist[4], checklist[5], checklist[6], checklist[7], checklist[8]
        return checklist[0], checklist[1], checklist[2], checklist[3], checklist[4], checklist[5], checklist[6], checklist[7], checklist[8]

    def getIndexs(self, item):
        """ Returns Current top level item and child index.
            If no child is selected, returns -1. 
        """
        # Check if top level item is selected or child selected
        if self.tree.indexOfTopLevelItem(item) == -1:
            return self.tree.indexOfTopLevelItem(item), item.parent().indexOfChild(item), item.childCount(), item.text(3), item.text(7), item.text(4), item.text(5), item.text(6)
        else:
            return self.tree.indexOfTopLevelItem(item), -1, item.childCount(), item.text(3), item.text(7), item.text(4), item.text(5), item.text(6)

    def chooseDelete(self):
        item = self.tree.currentItem()
        sip.delete(item)
        self.checkState()

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

    def setProgressBar(self):
        self.progress += 1
        self.ui.progressBar.setValue(self.progress)

    def clearProgressBar(self, max):
        self.progress = 0
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setMaximum(max)

    # =============================================================================
    #  Start and stop function
    # =============================================================================
    def folderMessage(self):
        global folder_address
        folder_address = QFileDialog.getExistingDirectory(
            self, "Please define the file name", self.cwd)

        if folder_address != '':
            self.folder_name = folder_address
            self.ui.label_18.setText(self.folder_name)
            self.cwd = folder_address

    def timeGo(self):
        """ TimeGo is the first activating function when "run" the project
            At first, the name of the project will be test if it has existed.
            if you ignore the warning and choose overwrite the file, the project
            will start immediately. The txt file as well as the plot items will
            be created.
        """
        if self.ui.label_18.text() == '':
            QMessageBox.information(
                self, "Wrong!.", "Please select the folder.")
        else:
            self.name = self.ui.lineEdit_2.text()
            if self.name == '':
                QMessageBox.information(
                    self, "Wrong!.", "Please type the file name.")
            else:
                file_name = f'{self.name}.txt'
                List = os.listdir(folder_address)
                if file_name in List:
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
        # file name
        self.full_address = self.folder_name + '/' + self.name
        # save plot count
        self.save_plot_count = 0
        self.switchToPlotTab()
        # plotlines init
        self.createEmptyLines()
        self.lineDisplaySwitchCreat()
        # txt start
        self.txt = TxtFunction()
        # porcedure start
        self.thread = QThread()
        self.procedure = None
        self.procedure = Procedure(
            self.instruments, self.instruments_read)
        self.procedure.moveToThread(self.thread)
        self.procedure.schedule(self.tree_num, self.child_num, self.leve_position, self.check,
                                self.method, self.ins_label, self.target, self.speed, self.increment)
        self.thread.started.connect(self.procedure.startMeasure)
        self.procedure.finished.connect(self.thread.quit)
        self.procedure.signal_txt.connect(self.txt.txtUpdate)
        self.procedure.signal_axis.connect(self.axisUpdate)
        self.procedure.signal_plot.connect(self.plotUpdate)
        self.procedure.signal_lines.connect(self.saveLines)
        self.procedure.signal_progress.connect(self.setProgressBar)
        self.procedure.clear_progress.connect(self.clearProgressBar)
        self.thread.start()
        # final resets
        self.ui.pushButton_5.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.ui.pushButton_5.setEnabled(True))

    def timeStop(self):
        # time stop
        logging.info('measure stop')
        try:
            self.procedureStop()
            self.thread.quit()
            self.thread.wait()
            self.shutdownInstruments()
            self.procedure = None
        except AttributeError:
            pass

    def procedureStop(self):
        self.procedure.stopMeasure()
        self.ui.pushButton_5.setEnabled(True)

    def procedureResumePause(self):
        self.procedure.resumePauseMeasure()

    def procedureQuitLoop(self):
        self.procedure.quitLoopMeasure()

    def procedureQuitSweep(self):
        self.procedure.quitSweepMeasure()

    def shutdownInstruments(self):
        for i in self.instruments:
            i.performClose()

    # =============================================================================
    # plot setting
    # =============================================================================

    def createEmptyLines(self):
        """
        creat the plotDataItem as data_line_%d where %d = 0, 1, 2... (reference)
        the x y value will be set later within the function plot_update()
        """
        self.plt.clear()
        self.data_line = []
        self.saved_line = []
        for _ in range(len(self.instruments_read)):
            self.data_line.append(self.ui.graphWidget.plot([]))

    def saveLines(self, file_count, x, y):
        read_len = len(y)
        for i in range(read_len):
            self.saved_line.append(self.ui.graphWidget.plot([]))
            self.saved_line[i + read_len*(file_count)].setData(
                x, y[i], pen=pg.mkPen(pg.intColor(i+1), width=1))
            self.data_line[i].setData([])

    def plotUpdate(self, n, x, y_n):
        # setData to the PlotItems
        if self.switch_list[n] == 1:
            self.data_line[n].setData(
                x, y_n, pen=pg.mkPen(pg.intColor(n+1), width=1))
        else:
            self.data_line[n].setData([])

    def plot_save(self):
        exporter = pg.exporters.ImageExporter(self.plt.scene())
        exporter.export(self.full_address + '_%d.png' % self.save_plot_count)
        QMessageBox.information(
            self, "Done.", "The figure No.%d has been saved." % self.save_plot_count)
        self.save_plot_count += 1

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
        logging.info('len')
        logging.info(len(self.instruments_read))
        logging.info('x')
        logging.info(x_show)
        logging.info('y')
        logging.info(y_show)
        i = 0
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


class Procedure(QObject):
    """this class is used to perform experiments"""
    finished = pyqtSignal()
    signal_txt = pyqtSignal(int, list, list, list, list)
    signal_plot = pyqtSignal(int, list, list)
    signal_axis = pyqtSignal(list, list)
    signal_lines = pyqtSignal(int, list, list)
    signal_progress = pyqtSignal()
    clear_progress = pyqtSignal(int)

    def __init__(self, instruments, instruments_read):
        super().__init__()
        self.instruments = instruments
        self.instruments_read = instruments_read
        self.options_read = window.options_read
        self.magnification = window.instruments_magnification
        self.control_sequence = []
        # control variable
        self.stop_running = False
        self.quit_running = False
        self.quit_sweep = False
        self.quit_loop = False
        # open instrument
        self.openInstruments()

    def openInstruments(self):
        """open instruments"""
        for instrument in self.instruments:
            instrument.performOpen()

    def schedule(self, tree_num, child_num, leve_position, check, method, ins_label, target, speed, increment):
        """ return [tree1, tree2, tree3]
            tree view
            [ [child_num, leve_position, instrument, option, check, target, speed, increment]
              [child_num, leve_position, instrument, option, check, target, speed, increment]
              [child_num, leve_position, instrument, option, check, target, speed, increment] ]
        """
        logging.info('\ntree_num', tree_num)
        logging.info('\nchild_num', child_num)
        logging.info('\nleve_position', leve_position)
        logging.info('\ncheck', check)
        logging.info('\nmethod', method)
        logging.info('\nins_label', ins_label)
        logging.info('\ntarget', target)
        logging.info('\nspeed', speed)
        logging.info('\nincredment', increment)

        # Know how many trees there are
        tree_total = max(tree_num) + 1

        # Create empty list to store tree info
        # [[], []]
        info_list = []
        for _ in range(tree_total):
            info_list.append([])

        for n, tree, label in zip(range(len(tree_num)), tree_num, ins_label):
            if label != '-1':
                info_list[tree].append([child_num[n], leve_position[n], self.instruments[int(
                    label)], method[n], check[n], target[n], speed[n], increment[n]])
            else:
                timeMeasure = TimeMeasurement(target[n])
                info_list[tree].append(
                    [child_num[n], leve_position[n], timeMeasure, method[n], check[n], target[n], speed[n], increment[n]])

        for i in info_list:
            self.buildTree(i)

    def buildTree(self, info_tree):
        """put [instruments, option] into [level_0, level_1, level_2]"""
        # info_tree: [child_num, leve_position, instrument, method, check, target, speed, increment]
        level = [[], [], []]
        # level = [level0, level1, level2]  level0 = [[instrument,method,check,target,speed,increment], [instrument,method,check,target,speed,increment]...]
        level_count = 0
        # put instrument in level
        for n, info in enumerate(info_tree):
            if info[0] == -1:
                continue
            level[level_count].append(
                [info_tree[n][2], info_tree[n][3], info_tree[n][4], info_tree[n][5], info_tree[n][6], info_tree[n][7]])
            level_count += 1

            if info[0] != 0:
                for i in range(info[0]):
                    level[level_count].append([info_tree[n+1+i][2], info_tree[n+1+i][3], info_tree[n+1+i]
                                              [4], info_tree[n+1+i][5], info_tree[n+1+i][6], info_tree[n+1+i][7]])

        self.control_sequence.append(level)

    def startMeasure(self):
        self.file_count = 0
        self.line_count = 0

        for level in self.control_sequence:
            if self.quit_running:
                return

            if level[0] and level[1] and level[2]:
                self.threeLevelsTree(level)

            elif level[0] and level[1] and not level[2]:
                self.twoLevelsTree(level)

            elif level[0] and not level[1] and not level[2]:
                self.oneLevelTree(level)
                
        self.finished.emit()
        window.txt.txtMerger(window.full_address, self.file_count,
                             len(self.instruments_read)+1)
        window.txt.txtDeleter(self.file_count)
        

    def threeLevelsTree(self, level):
        for i in level[0]:  # i = [instrument,method,check,target,speed,increment]
            for value_i in i[0].experimentLinspacer(i[1], i[3], i[4], i[5]):
                self.performRecord(i, value_i, False)

                for j in level[1]:
                    for value_j in j[0].experimentLinspacer(j[1], j[3], j[4], j[5]):
                        self.performRecord(j, value_j, False)

                        for k in level[1]:
                            self.createEmptyDataSet()
                            linspacer = k[0].experimentLinspacer(
                                k[1], k[3], k[4], k[5])
                            self.clear_progress.emit(len(linspacer))
                            for value_k in linspacer:
                                self.performRecord(k, value_k, True)
                                if self.quit_sweep:
                                    self.quit_sweep = False
                                    break
                                if self.quit_loop:
                                    self.quit_loop = False
                                    return

                            self.signal_lines.emit(
                                self.line_count, self.x, self.y)
                            self.line_count += 1
                            if int(k[2]):
                                self.file_count += 1

    def twoLevelsTree(self, level):
        for i in level[0]:
            for value_i in i[0].experimentLinspacer(i[1], i[3], i[4], i[5]):
                self.performRecord(i, value_i)

                for j in level[1]:
                    self.createEmptyDataSet()
                    linspacer = j[0].experimentLinspacer(
                        j[1], j[3], j[4], j[5])
                    self.clear_progress.emit(len(linspacer))
                    for value_j in linspacer:
                        self.performRecord(j, value_j, True)
                        if self.quit_sweep:
                            self.quit_sweep = False
                            break
                        if self.quit_loop:
                            self.quit_loop = False
                            return

                    self.signal_lines.emit(self.line_count, self.x, self.y)
                    self.line_count += 1
                    if int(j[2]):
                        self.file_count += 1

    def oneLevelTree(self, level):
        for i in level[0]:
            self.createEmptyDataSet()
            linspacer = i[0].experimentLinspacer(i[1], i[3], i[4], i[5])
            logging.info('linespacer: ', linspacer)
            self.clear_progress.emit(len(linspacer))
            for value_i in linspacer:
                logging.info(value_i, 'value_i')
                self.performRecord(i, value_i, True)
                if self.quit_sweep:
                    self.quit_sweep = False
                    break
                if self.quit_loop:
                    self.quit_loop = False
                    return

            self.signal_lines.emit(self.line_count, self.x, self.y)
            self.line_count += 1
            if int(i[2]):
                self.file_count += 1

    def performRecord(self, instrument_info, value, bottom_level=False):
        while self.stop_running:
            QThread.sleep(1)

        # instrument_info = instrument method check target speed increment
        if instrument_info[5] != '0' and instrument_info[5] != '-':
            for value_increment in instrument_info[0].experimentLinspacer(instrument_info[1], value, instrument_info[4], '0'):
                instrument_info[0].performSetValue(
                    instrument_info[1], value_increment)
                sleep(0.1)
        set_value = instrument_info[0].performSetValue(
            instrument_info[1], value)
        sleep(0.1)
        x_show = [set_value, instrument_info[0].instrumentName(),
                  instrument_info[1]]
        y_show = []
        name_txt = []
        method_txt = []

        name_txt.append(instrument_info[0].instrumentName())
        method_txt.append(instrument_info[1])

        if bottom_level:
            self.x.append(set_value)

        for n, instrument_read in enumerate(self.instruments_read):
            read_value = instrument_read.performGetValue(
                self.options_read[n], self.magnification[n])
            y_show.append(read_value)
            name_txt.append(instrument_read.instrumentName())
            method_txt.append(self.options_read[n])
            if bottom_level:
                self.y[n].append(read_value)
                self.signal_plot.emit(n, self.x, self.y[n])

        self.signal_axis.emit(x_show, y_show)
        if int(instrument_info[2]):
            self.signal_txt.emit(self.file_count, method_txt,
                                 name_txt, x_show, y_show)
        self.signal_progress.emit()

    def resumePauseMeasure(self):
        if self.stop_running == False:
            self.stop_running = True
        else:
            self.stop_running = False

    def quitSweepMeasure(self):
        self.quit_sweep = True

    def stopMeasure(self):
        self.quit_running = True
        self.quit_loop = True

    def quitLoopMeasure(self):
        self.quit_loop = True

    def createEmptyDataSet(self):
        x = []
        y = []
        read_len = len(self.instruments_read)
        for _ in range(read_len):
            y.append([])
        self.x = x
        self.y = y


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
