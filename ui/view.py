#!/usr/bin/env python
from PyQt5 import sip
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTreeWidgetItem, QTreeWidgetItemIterator, QMainWindow, QTableWidgetItem, QDialog
from ui import Qt_Window, Control_Window, Read_Window
from time import sleep
from utils import load_drivers, addtwodimdict, colorLoop, is_number
from nidaqmx.system import System
import pyqtgraph as pg
import pyqtgraph.exporters
import pyvisa as visa
import os
import qdarkstyle
import logging
import numpy as np


class MainWindow(QMainWindow):
    """Main class"""
    RECENT_PATH = './ui/asset/step.txt'
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Qt_Window()
        self.ui.setupUi(self)

        # control panel & read panel
        self.control_panel = ControlPanel()
        self.read_panel = ReadlPanel()

        # Pre-run functions
        self._intrumentList()
        self._visaList()
        self._connectSignals()
        self._setPlotWidget()
        self._initParameters()
        self._defaultPosition()

        # Set Window style
        self.ui.tableWidget.setColumnWidth(0, 300)
        self.ui.tableWidget.setColumnWidth(1, 300)
        self.setWindowIcon(QIcon('./ui/asset/Qfort.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # =============================================================================
    # Pre-run functions
    # =============================================================================
    def _visaList(self):
        """detect available address"""
        try:
            resource_manager = visa.ResourceManager()
            self.pyvisa_list = resource_manager.list_resources()
            self.ui.listWidget.clear()
            self.ui.listWidget.addItems(self.pyvisa_list)
            self.ui.listWidget.addItem("default")
            # DAQ TODO:only one daq is available now 20210916
            system = System.local()
            for i, device in enumerate(system.devices):
                if i > 0:
                    self.ui.listWidget.addItem(device.name)
        except:
            self.pageOneInformation('detect available address fail')

    def _intrumentList(self):
        """detect available drivers"""
        self.driver_list = load_drivers()
        self.ui.listWidget_2.clear()
        self.ui.listWidget_2.addItems(self.driver_list.keys())

    def _connectSignals(self):
        """Connect buttons with functions"""
        # Page 1 Buttons
        self.ui.pushButton.clicked.connect(self._visaList)
        self.ui.pushButton_2.clicked.connect(lambda: self.connection())
        self.ui.pushButton_10.clicked.connect(self.deleteConnectedInstrument)
        self.ui.nextButton.clicked.connect(lambda: self.switchToPlotTab(1))
        # Page 2 Buttons
        self.ui.pushButton_7.clicked.connect(self.readPanelShow)
        self.read_panel.ctr_ui.pushButton_5.clicked.connect(lambda: self.readConfirm())
        self.ui.pushButton_3.clicked.connect(self.controlPanelShow)
        self.control_panel.read_ui.pushButton_9.clicked.connect(lambda: self.addLevel())
        self.control_panel.read_ui.pushButton_8.clicked.connect(lambda: self.chooseAddChild())
        self.ui.pushButton_8.clicked.connect(self.deleteReadRow)
        self.ui.pushButton_9.clicked.connect(self.chooseDelete)
        self.ui.pushButton_26.clicked.connect(lambda: self.timeAddLevel())
        self.ui.pushButton_27.clicked.connect(lambda: self.timeAddChild())
        self.ui.pushButton_4.clicked.connect(self.folderMessage)
        # check box
        self.control_panel.read_ui.checkBox.stateChanged.connect(self.checkFunctionIncrement)
        # Tables
        self.ui.tableWidget_2.cellClicked.connect(self.showMethod)
        # treeWidget init
        self.tree = self.ui.treeWidget
        self.tree.itemClicked.connect(self.checkState)
        # Page 3 Buttons
        self.ui.pushButton_13.clicked.connect(self.displayCursorCrossHair)
        self.ui.pushButton_12.clicked.connect(self.autoPlotRange)
        self.ui.pushButton_16.clicked.connect(self.plotSave)
        # Tables
        self.ui.tableWidget_5.cellClicked.connect(self.lineDisplaySwitch)
        # Menu
        self.ui.retranslateUi(self)
        self.ui.actionQuit.setShortcut('Ctrl+Q')
        self.ui.actionQuit.triggered.connect(self.close)
        self.ui.actionRecent.triggered.connect(self.openRecentStep)
        self.ui.actionRecent.setShortcut('Ctrl+R')
        self.ui.actionOpen.triggered.connect(self.openFileStep)
        self.ui.actionOpen.setShortcut('Ctrl+O')

    def _setPlotWidget(self):
        """Set PyQtGraph"""
        pg.setConfigOptions(antialias=False)
        self.plt = self.ui.graphWidget
        # viewbox setting
        self.viewbox = self.plt.getViewBox()
        self.viewbox.disableAutoRange()
        # plot setting
        self.plt.showGrid(x=True, y=True, alpha=1)
        self.plt.setLabel('bottom', '   ')
        self.plt.setLabel('left', '   ')
        self.plt.setDownsampling(auto=True, mode='peak')

    def _defaultPosition(self):
        if os.path.exists(self.RECENT_PATH):
            with open('./ui/asset/step.txt') as f:
                steps = f.readlines()
            info = steps[-3].rstrip().split('\t')
            address = info[0]
            self.folder_address = address
            self.ui.label_18.setText(address)
            self.open_folder = address

    def _initParameters(self):
        # pointer
        self.name_count = 1
        self.row_count = 1
        self.read_row_count = 1
        self.save_plot_count = 0
        self.time_unit = 0.1  # sec
        self.progress = 0
        self.load = True
        self.full_address = ""
        self.open_folder = os.getcwd()

        # instruments
        self.instruments = []
        self.instruments_read = []
        self.tree_info = []
        self.instruments_dict = {}

        # PlotItem lines
        self.data_line = []
        self.x_data = []
        self.y_data = []
        self.color_offset = 0

        # choose line
        self.choose_line_start = 0
        self.choose_line_space = 1
        self.choose_line_num = 0
        self.line_num_now = 0

    # =============================================================================
    # Record measurement process
    # =============================================================================

    def getTableValues(self):
        steps = [[],[],[],[],[]]
        # 0 Connection:
        for row in range(self.ui.tableWidget.rowCount()):
            for col in range(self.ui.tableWidget.columnCount()):
                steps[0].append(self.ui.tableWidget.item(row,col).text())
            steps[0].append(".")
        # 1 Control:
        iterator = QTreeWidgetItemIterator(self.tree)
        level = {'0': '-', '1': '--', '2': '---' }
        while iterator.value():
            item = iterator.value()
            steps[1].append(level[item.text(0)])
            for i in range(1,8):
                steps[1].append(item.text(i))
            steps[1].append(".")
            iterator += 1
        # 2 Read:
        for row in range(self.ui.tableWidget_4.rowCount()):
            for col in range(self.ui.tableWidget_4.columnCount()):
                steps[2].append(self.ui.tableWidget_4.item(row,col).text())
            steps[2].append(".")
        # 3 folder address:
        steps[3].append(self.ui.label_18.text())
        # file name:
        steps[4].append(self.ui.lineEdit_2.text())
        return steps

    def openRecentStep(self):
        if self.load and os.path.exists(self.RECENT_PATH):
            self.pageOneInformation("Opening recent file...")
            with open(self.RECENT_PATH) as f:
                steps = f.readlines()
            self.loadStep(steps)
        
    def openFileStep(self):
        file = QFileDialog.getOpenFileName(self, "Please select the file", self.open_folder)
        if file[0] and self.load:
            self.pageOneInformation("Opening specified file...")
            with open(file[0]) as f:
                steps = f.readlines()
            self.loadStep(steps)

    def loadStep(self, steps):
        modes = {   'Connection (Name/Type/Address) :' : 0,
                    'Control (Level/Name/Type/Property/Target/Speed/Increment/Ins_lable) :' : 1,
                    'Read (Name/Type/Property/Magnification/Unit) :' : 2,
                    'File address:' : 3, 'File name:' : 4, 'Created on' : -1    }
        try:
            for step in steps:
                info = step.rstrip().split('\t')
                if info[0] in modes:
                    mode = modes[info[0]]
                    continue
                # Connection:
                if mode == 0:
                    self.connection(info[0], info[1], info[2])
                    sleep(0.5)
                # Control:
                elif mode == 1:
                    if info[0] == '-':
                        if info[1] == 'Time Meas':
                            self.timeAddLevel(info[4])
                        else:
                            self.addLevel(info[1:])
                    elif info[0] == '--':
                        if info[1] == 'Time Meas':
                            self.timeAddChild(info[4], self.root)
                        else:
                            self.chooseAddChild(info[1:], self.root)
                    elif info[0] == '---':
                        if info[1] == 'Time Meas':
                            self.timeAddChild(info[4], self.child1)
                        else:
                            self.chooseAddChild(info[1:], self.child1)
                # Read:
                elif mode == 2:
                    if len(info)==4:
                        self.readConfirm(info[0], info[1], info[2], info[3])
                    elif len(info)==5:
                        self.readConfirm(info[0], info[1], info[2], info[3], info[4])
                # File address:
                elif mode == 3:
                    self.folder_address = info[0]
                    self.ui.label_18.setText(info[0])
                elif mode == 4:
                    self.ui.lineEdit_2.setText(info[0])
            self.pageOneInformation("Done.")
            self.load = False
            self.switchToPlotTab(1)
        except:
            logging.exception('open file failed')
            self.pageOneInformation("Failed.")

    # =============================================================================
    # Page 1 Connection
    # =============================================================================

    def connection(self, instrument_personal_name="", instrument_type="", visa_address=""):
        """ Connect instrument and add to table_instrList """
        if visa_address=="" or instrument_type=="" or instrument_personal_name=="":
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

                    instrument = self.driver_list[instrument_type](visa_address)
                    instrument.setProperty(visa_address, instrument_name, instrument_type)
                    self.instruments.append(instrument)

                    self.pageOneInformation(f'visa_address: {visa_address}')
                    self.pageOneInformation(f'{instrument_type} has been connected successfully.')
                    # TODO: add initialization option on messagebox and show the related info

                    # Add new row if necessary
                    if self.row_count > row_len:
                        self.ui.tableWidget.insertRow(row_len)
                        self.ui.tableWidget_2.insertRow(row_len)

                    # Assign varibales to current var
                    instrument_property = [instrument_personal_name, instrument_type, visa_address]
                    for i, p in enumerate(instrument_property):
                        if p == '':
                            p = instrument_name
                        # Update the info to the table in page 1
                        self.ui.tableWidget.setItem(self.row_count - 1, i, QTableWidgetItem(p))

                    # Update the left top table in page 2
                    if instrument_personal_name == '':
                        instrument_personal_name = instrument_name
                    self.ui.tableWidget_2.setItem(self.row_count - 1, 0, QTableWidgetItem(instrument_personal_name))
                    self.ui.tableWidget_2.setItem(self.row_count - 1, 1, QTableWidgetItem(instrument_type))
                    self.row_count += 1
                    # add instrument name to dict
                    self.instruments_dict[str(instrument_personal_name)] = instrument

                except visa.VisaIOError or AttributeError as e:
                    self.pageOneInformation(f"{instrument_type} connect fail")
                    logging.exception('connect fail', exc_info=e)
        self.ui.lineEdit.clear()

    def deleteConnectedInstrument(self):
        if self.ui.tableWidget.rowCount() >= 1:
            row = self.ui.tableWidget.currentRow()
            name = self.ui.tableWidget.item(row,0).text()
            self.ui.tableWidget.removeRow(row)
            self.ui.tableWidget_2.removeRow(row)
            self.row_count -= 1
            self.instruments.pop(row)
            del self.instruments_dict[name]
        else:
            self.pageOneInformation('Deletion failed due to no component')
        
    # =============================================================================
    # Page 2 Read
    # =============================================================================

    def readPanelShow(self):
        # self.pageTwoInformation(self.ui.listWidget_3.currentItem())
        if self.ui.listWidget_3.currentItem() == None:
            self.pageTwoInformation('Please select a method.')
        else:
            self.read_panel.show()

    def readConfirm(self, instrument_name="", instrument_type="", read_method="", magnification="", Unit=""):
        if magnification=="":
            # Get the necessary info of the chosen item
            row = self.ui.tableWidget_2.currentRow()
            instrument_name = self.ui.tableWidget_2.item(row, 0).text()
            instrument_type = self.ui.tableWidget_2.item(row, 1).text()
            read_method = self.ui.listWidget_3.currentItem().text()
            magnification = self.read_panel.ctr_ui.lineEdit_2.text()
            Unit = self.read_panel.ctr_ui.lineEdit_3.text()
        # check if magnification is number
        if read_method != "Triton Temperature (AUX in 3)" and not is_number(magnification):
            self.pageTwoInformation('magnification is not a number.')
            return
                
        # Add new row if necessary
        row_len = self.ui.tableWidget_4.rowCount()
        if self.read_row_count > row_len:
            self.ui.tableWidget_4.insertRow(row_len)
            self.ui.tableWidget_5.insertColumn(row_len + 1)
        # Assign the variables to the table in page 2
        self.ui.tableWidget_4.setItem(self.read_row_count - 1, 0, QTableWidgetItem(instrument_name))
        self.ui.tableWidget_4.setItem(self.read_row_count - 1, 1, QTableWidgetItem(instrument_type))
        self.ui.tableWidget_4.setItem(self.read_row_count - 1, 2, QTableWidgetItem(read_method))
        self.ui.tableWidget_4.setItem(self.read_row_count - 1, 3, QTableWidgetItem(magnification))
        self.ui.tableWidget_4.setItem(self.read_row_count - 1, 4, QTableWidgetItem(Unit))
        # initialize the blocks in the read option
        self.read_panel.ctr_ui.lineEdit_2.setText("1")
        self.read_panel.ctr_ui.lineEdit_3.clear()
        # Assign the variables to the table in page 3
        self.ui.tableWidget_5.setItem(0, self.read_row_count, QTableWidgetItem(instrument_name))
        self.ui.tableWidget_5.setItem(1, self.read_row_count, QTableWidgetItem(read_method))
        color = colorLoop(self.read_row_count-1)
        self.ui.tableWidget_5.item(0,self.read_row_count).setForeground(QColor(color[0],color[1],color[2]))

        self.read_row_count += 1
        self.instruments_read.append(self.instruments_dict[instrument_name])

    def deleteReadRow(self):
        if self.ui.tableWidget_4.rowCount() >= 1:
            row = self.ui.tableWidget_4.currentRow()
            self.ui.tableWidget_4.removeRow(row)
            self.ui.tableWidget_5.removeColumn(row+1)
            self.read_row_count -= 1
            self.instruments_read.pop(row)
        else:
            self.pageTwoInformation('Deletion failed due to no component')

    # =============================================================================
    # Page 2 Control
    # =============================================================================

    def controlPanelShow(self):
        # self.pageTwoInformation(self.ui.listWidget_3.currentItem())
        if self.ui.listWidget_3.currentItem() == None:
            self.pageTwoInformation('Please select a method.')
        else:
            self.control_panel.show()

    def timeAddLevel(self, wait_time=""):
        """ Provide another option to do the time measurement """
        if wait_time=="":
            wait_time = self.ui.lineEdit_5.text()
        if is_number(wait_time):
            self.root = QTreeWidgetItem(self.tree)
            self.root.setText(0, '0')
            self.root.setFlags(self.root.flags() | Qt.ItemIsUserCheckable)
            self.root.setCheckState(0, Qt.Checked)
            self.root.setExpanded(True)
            self.updateTimeMeasurement(self.root, wait_time)
            self.checkState()
        else:
            self.pageTwoInformation('Time measurement - Please enter a number.')
        self.ui.lineEdit_5.clear()

    def timeAddChild(self, wait_time="", item=""):
        """ Provide another option to do the time measurement """
        # When button is used
        if wait_time=="":
            wait_time = self.ui.lineEdit_5.text()
            item = self.tree.currentItem()
        # Check if the # of childs has reached 2 (Maximum value)            
        if item.text(0) == '2':
            self.pageTwoInformation("Time measurement - Can't join more childs in new layer. The Maximum layers is 3.")
            return
        if is_number(wait_time):
            self.child1 = QTreeWidgetItem(item)
            # The child_text is its up-level item.text(0) + 1
            child_text = str(int(item.text(0)) + 1)
            self.child1.setText(0, child_text)
            self.child1.setExpanded(True)
            self.updateTimeMeasurement(self.child1, wait_time)
            self.child1.setFlags(self.child1.flags() | Qt.ItemIsUserCheckable)
            self.child1.setCheckState(0, Qt.Checked)
            self.control_panel.read_ui.checkBox.setChecked(False)
            self.checkState()
        else:
            self.pageTwoInformation('Time measurement - Please enter a number.')
        self.ui.lineEdit_5.clear()

    @staticmethod
    def updateTimeMeasurement(item, wait_time):
        row = str(-1)
        Ins_name = 'Time Meas'
        Ins_type = 'Timer'
        control_method = '-'

        # TODO: restrict the the value to integer only or something related to the unit
        target = wait_time
        speed = '-'
        increment = '-'
        control_list = [Ins_name, Ins_type, control_method, target, speed, increment]
        for i, element in enumerate(control_list):
            item.setText((i+1), element)
        item.setText(7, row)

    # treeWidget
    def addLevel(self, control_list=[]):
        if control_list==[]:
            control_list = self.getControlList()
        self.root = QTreeWidgetItem(self.tree)
        self.root.setText(0, '0')
        self.root.setFlags(self.root.flags() | Qt.ItemIsUserCheckable)
        self.root.setCheckState(0, Qt.Checked)
        self.root.setExpanded(True)
        self.updateInfo(self.root, control_list)
        self.control_panel.read_ui.checkBox.setChecked(False)
        self.control_panel.read_ui.lineEdit_5.setText('0')
        self.checkState()

    def chooseAddChild(self, control_list=[], item=[]):
        if control_list==[]:
            control_list = self.getControlList()
            # QTreeWidgetItem括號內放的物件是作為基礎(root)，child會往下一層放
            item = self.tree.currentItem()
        # Check if the # of childs has reached 2 (Maximum value)
        if item.text(0) == '2':
            self.pageTwoInformation("Control - Can't join more childs in new layer. The Maximum layers is 3.")
            return 
        # Check if the current item is the father (value >= 0)
        if self.tree.indexOfTopLevelItem(item) >= 0:
            target_item = item
        # If it's the child, the value is -1. The condition falls into else:
        else:
            _, _, child_num, _, _, _, _, _ = self.getIndexs(item.parent())
            target_item = item.parent().child(child_num - 1)
        self.child1 = QTreeWidgetItem(target_item)
        # The child_text is its up-level item.text(0) + 1
        child_text = str(int(item.text(0)) + 1)
        self.child1.setText(0, child_text)
        self.child1.setExpanded(True)
        self.updateInfo(self.child1, control_list)
        self.child1.setFlags(self.child1.flags() | Qt.ItemIsUserCheckable)
        self.child1.setCheckState(0, Qt.Checked)
        self.control_panel.read_ui.checkBox.setChecked(False)
        self.control_panel.read_ui.lineEdit_5.setText('0')
        self.checkState()

    def getControlList(self):
        row = self.ui.tableWidget_2.currentRow()
        Ins_name = self.ui.tableWidget_2.item(row, 0).text()
        Ins_type = self.ui.tableWidget_2.item(row, 1).text()
        control_method = self.ui.listWidget_3.currentItem().text()
        target = self.control_panel.read_ui.lineEdit_2.text()
        speed = self.control_panel.read_ui.lineEdit_3.text()
        increment = self.control_panel.read_ui.lineEdit_5.text()
        control_list = [Ins_name, Ins_type, control_method, target, speed, increment, str(row)]
        return control_list

    def updateInfo(self, item, control_list):
        target = control_list[3]
        speed = control_list[4]
        if is_number(target) and is_number(speed):
            for i, element in enumerate(control_list):
                item.setText((i+1), element)
        else:
            self.pageTwoInformation('Control measurement - Please enter a number.')

    # =============================================================================
    # Page 2 Other
    # =============================================================================

    def showMethod(self):
        row = self.ui.tableWidget_2.currentRow()
        instrument = self.instruments[row]
        self.ui.listWidget_3.clear()
        # show the method of the chosen itesm to the list
        self.ui.listWidget_3.addItems(instrument.METHOD)

    def checkFunctionIncrement(self):
        if self.control_panel.read_ui.checkBox.isChecked():
            self.control_panel.read_ui.lineEdit_5.setEnabled(True)
        else:
            self.control_panel.read_ui.lineEdit_5.setEnabled(False)

    def checkState(self):
        iterator = QTreeWidgetItemIterator(self.tree)
        checklist = []
        for _ in range(11):
            checklist.append([])

        while iterator.value():
            item = iterator.value()
            treeindex, childindex, child_num, method, ins_label, target, speed, increment = self.getIndexs(item)
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
        self.tree_info = checklist

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
        if item:
            sip.delete(item)
            self.checkState()
        else:
            self.pageTwoInformation('Deletion failed due to no component')

    # =============================================================================
    # Page 3 Button
    # =============================================================================

    def resumePause(self):
        if self.ui.pauseButton.text() == "Pause":
            self.ui.pauseButton.setText("Resune")
        else:
            self.ui.pauseButton.setText("Pause")

    @pyqtSlot(int)
    def on_spinBox_valueChanged(self, value):
        """ Draw from the nth line """
        self.choose_line_start = value-1
        self.renewGraph()

    @pyqtSlot(int)
    def on_spinBox_2_valueChanged(self, value):
        """ A total of n lines to draw """
        self.renewGraph()

    @pyqtSlot(int)
    def on_spinBox_3_valueChanged(self, value):
        """ draw every n lines """
        self.choose_line_space = value
        self.renewGraph()

    def displayCursorCrossHair(self):
        """Add crosshair lines."""
        if self.ui.pushButton_13.isChecked():
            self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
            self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
            self.ui.graphWidget.addItem(self.crosshair_v, ignoreBounds=True)
            self.ui.graphWidget.addItem(self.crosshair_h, ignoreBounds=True)
            self.proxy = pg.SignalProxy(self.ui.graphWidget.scene().sigMouseMoved, rateLimit=60, slot=self.displayCursorCoordinate)
        else:
            self.ui.graphWidget.removeItem(self.crosshair_h)
            self.ui.graphWidget.removeItem(self.crosshair_v)
            del self.proxy
            self.ui.label_coordinate_x.setText(f"")
            self.ui.label_coordinate_y.setText(f"")

    def displayCursorCoordinate(self, e):
        pos = e[0]
        if self.ui.graphWidget.sceneBoundingRect().contains(pos):
            mouse_point = self.ui.graphWidget.getPlotItem().vb.mapSceneToView(pos)
            self.ui.label_coordinate_x.setText(f"x={mouse_point.x():g}")
            self.ui.label_coordinate_y.setText(f"y={mouse_point.y():g}")
            self.crosshair_v.setPos(mouse_point.x())
            self.crosshair_h.setPos(mouse_point.y())

    def plotSave(self):
        """ save figure from page3 """
        exporter = pyqtgraph.exporters.ImageExporter(self.plt.scene())
        exporter.export(self.full_address + '_%d.png' % self.save_plot_count)
        QMessageBox.information(self, "Done.", "The figure No.%d has been saved." % self.save_plot_count)
        self.save_plot_count += 1

    def autoPlotRange(self):
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
    #  Page 3 Start and stop function
    # =============================================================================

    def folderMessage(self):
        folder_address = QFileDialog.getExistingDirectory(self, "Please define the folder name", self.open_folder)
        if folder_address != '':
            self.ui.label_18.setText(folder_address)
            self.open_folder = folder_address
            self.folder_address = folder_address

    def messageBox(self, message):
        QMessageBox.information(self, "Wrong!", message)

    def fileExist(self):
        reply = QMessageBox.information(self, "Wrong!", "The file has existed. Do you want to overwrite it?",
                                        QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
        if reply == QMessageBox.Close:
            QMessageBox.information(self, "Wrong!", "Please adjust the file name.")
            return False
        elif reply == QMessageBox.Ok:
            return True

    def procedureGo(self, name):
        # file name
        self.full_address = self.folder_address + '/' + name
        # save plot count
        self.save_plot_count = 0
        self.switchToPlotTab(2)
        # plotlines init
        self.createEmptyLines()
        self.getReadInfo()
        # final resets
        self.ui.pushButton_5.setEnabled(False)

    def getReadInfo(self):
        self.instruments_magnification = []
        self.options_read = []
        self.units = []   
        for row in range(self.ui.tableWidget_4.rowCount()):
            read_method = self.ui.tableWidget_4.item(row,2).text()
            self.options_read.append(read_method)
            magnification = self.ui.tableWidget_4.item(row,3).text()
            if read_method == "Triton Temperature (AUX in 3)":
                self.instruments_magnification.append(magnification)
            elif is_number(magnification):
                self.instruments_magnification.append(float(magnification))
            unit = self.ui.tableWidget_4.item(row,4).text()
            self.units.append(unit)

    def stopMeasure(self):
        reply = QMessageBox.information(self, "Warning!", "Are you sure you want to stop measuring?",
                                        QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply == QMessageBox.Cancel:
            return False
        elif reply == QMessageBox.Ok:
            return True

    # =============================================================================
    # plot setting
    # =============================================================================

    def createEmptyLines(self):
        """ creat the plotDataItem as data_line[i] where i = 0, 1, 2... (reference)
            the x y value will be set later within the function plotUpdate()
        """
        self.plt.clear()
        self.read_len = len(self.instruments_read)
        # one line data
        self.x_data = np.array([], dtype=np.float32)
        self.y_data = []
        # all plot Item
        self.saved_data = {}
        # plot item
        self.data_line = []
        # line display switch
        self.switch_list = []
        # color
        self.color = []

        for i in range(self.read_len):
            self.data_line.append(self.ui.graphWidget.plot([]))
            self.y_data.append(np.array([], dtype=np.float32))
            self.switch_list.append(True)
            self.color.append(colorLoop(i+self.color_offset))
            
    def plotUpdate(self, n, x, y_n, line_id):
        if not np.isnan(x):
            if n == 0:
                self.x_data = np.append(self.x_data, [x])
            self.y_data[n] = np.append(self.y_data[n], y_n)
            # setData to the PlotItems
            # TODO: The three line selection functions currently only include the second one
            if not self.switch_list[n] or (self.choose_line_num!=0 and not line_id in self.choose_line):
                pass
            else:
                self.data_line[n].setData(self.x_data, self.y_data[n], pen=pg.mkPen(self.color[n], width=1))

    def saveLines(self, file_count):
        for i in range(self.read_len):       
            line = self.ui.graphWidget.plot(self.x_data, self.y_data[i], pen=pg.mkPen(self.color[i], width=1))
            addtwodimdict(self.saved_data, file_count, i, line)
            self.color_offset += 3
            self.color[i] = colorLoop(i+self.color_offset)
            if self.switch_list[i]:
                self.ui.tableWidget_5.item(0,i+1).setForeground(QColor(self.color[i][0], self.color[i][1], self.color[i][2]))
            if not self.switch_list[i] or (self.choose_line_num!=0 and not file_count in self.choose_line):
                line.hide()
            self.line_num_now = file_count
        
        # initialize x y data
        self.x_data = np.array([], dtype=np.float32)
        self.y_data = []
        for _ in range(self.read_len):
            self.y_data.append(np.array([], dtype=np.float32))

    def lineDisplaySwitch(self):
        """ this function is connected to tableWidget_5 on page 3
            the function activates whenever the tablewidge_5 is clicked
        """
        col = self.ui.tableWidget_5.currentColumn()-1
        if col == -1:   # ignore x_show column
            return
        if self.switch_list[col]:
            self.switch_list[col] = False
            self.ui.tableWidget_5.item(0,col+1).setForeground(QColor(255,255,255))
        else:
            self.switch_list[col] = True
            self.ui.tableWidget_5.item(0,col+1).setForeground(QColor(self.color[col][0], self.color[col][1], self.color[col][2]))
        self.renewGraph()

    def renewGraph(self):
        # hide all line in graph
        for group in self.saved_data.values():
            for line in group.values():
                line.hide()

        for id, line in enumerate(self.data_line):
            if self.switch_list[id]:
                line.show()
            else:
                line.hide()

        # get choose_line_num
        self.choose_line_num = self.ui.spinBox_2.value()
        if self.choose_line_num == 0:
            choose_line_num = int(self.line_num_now)
            display_line_num = int(choose_line_num/self.choose_line_space)+1
        else:
            choose_line_num = self.choose_line_num - 1
            display_line_num = self.choose_line_num
        
        start = self.choose_line_start*self.choose_line_space
        end = start+self.choose_line_space*(int(choose_line_num/self.choose_line_space)-self.choose_line_start)
        if end > start:
            choose_line = np.linspace(start, end, display_line_num, dtype=np.int16)
        else:
            choose_line = np.array([])
        self.choose_line = set(choose_line)
        print(self.choose_line)

        if self.saved_data:
            try:
                self.rePlotData(choose_line)      
            except KeyError:
                logging.exception("renewGraph error")

    def rePlotData(self, choose_line):
        for curve_group in choose_line:
            for curve_num in self.saved_data[curve_group].keys():
                if self.switch_list[curve_num]:                    
                    self.saved_data[curve_group][curve_num].show()

                    
    # =============================================================================
    # axis setting
    # =============================================================================

    def axisUpdate(self, x_show, y_show):
        # update x title (instrument name and method)
        # insturement name
        self.ui.tableWidget_5.setItem(0, 0, QTableWidgetItem(f'{x_show[1]}'))
        # method
        self.ui.tableWidget_5.setItem(1, 0, QTableWidgetItem(f'{x_show[2]}'))

        # update x value
        self.ui.tableWidget_5.setItem(2, 0, QTableWidgetItem(f'{x_show[0]:g}'))
        # update y value
        for i in range(self.read_len):
            self.ui.tableWidget_5.setItem(2, (i + 1), QTableWidgetItem(f'{y_show[i]:g}'))

    # =============================================================================
    # Other
    # =============================================================================

    def pageOneInformation(self, string):
        """put some word in the information board"""
        self.ui.textBrowser.append(str(string))

    def pageTwoInformation(self, string):
        self.ui.textBrowser_2.append(str(string))

    def pageThreeInformation(self, string):
        self.ui.textBrowser_3.clear
        self.ui.textBrowser_3.append(str(string))

    def switchToPlotTab(self, page):
        self.ui.tabWidget.setCurrentIndex(page)


class ControlPanel(QDialog):
    """Page 2 subwindow Control option panel"""

    def __init__(self):
        super(ControlPanel, self).__init__()
        self.read_ui = Control_Window()
        self.read_ui.setupUi(self)
        self.read_ui.pushButton_9.clicked.connect(self.close)
        self.read_ui.pushButton_8.clicked.connect(self.close)
        self.read_ui.pushButton_6.clicked.connect(self.close)


class ReadlPanel(QDialog):
    """Page 2 subwindow Read option panel"""

    def __init__(self):
        super(ReadlPanel, self).__init__()
        self.ctr_ui = Read_Window()
        self.ctr_ui.setupUi(self)
        self.ctr_ui.pushButton_5.clicked.connect(self.close)
        self.ctr_ui.pushButton_6.clicked.connect(self.close)
