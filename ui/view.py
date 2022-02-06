#!/usr/bin/env python
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTreeWidgetItem, QTreeWidgetItemIterator, QMainWindow, QTableWidgetItem, QDialog
import pyqtgraph as pg
import pyqtgraph.exporters
from ui import Qt_Window, Control_Window, Read_Window
from PyQt5 import sip
import pyvisa as visa
import os
from utils import load_drivers, addtwodimdict, colorLoop
import qdarkstyle
from nidaqmx.system import System
import logging
import numpy as np

# logging.basicConfig(format="%(message)s", level=logging.INFO)   # debug mode


class MainWindow(QMainWindow):
    """Main class"""
    # pointer
    name_count = 1
    row_count = 1
    read_row_count = 1
    save_plot_count = 0
    # click = 1
    time_unit = 0.1  # sec
    progress = 0

    # instruments
    instruments = []
    instruments_read = []
    instruments_magnification = []
    options_read = []
    tree_info = []

    # PlotItem lines
    data_line = []
    x_data = []
    y_data = []
    color_offset = 0

    # choose line
    choose_line_start = 0
    choose_line_space = 1
    choose_line_num = 0
    line_num_now = 0

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

        # Tables
        self.ui.tableWidget.setColumnWidth(0, 100)
        self.ui.tableWidget.setColumnWidth(1, 200)

        # plot widget
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

        # Menu
        self.ui.retranslateUi(self)
        self.ui.actionQuit.setShortcut('Ctrl+Q')
        self.ui.actionQuit.triggered.connect(self.close)

        # Set Window Icon
        self.setWindowIcon(QIcon('./ui/Qfort.png'))

        # Set Window style
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # =============================================================================
    # Page 1
    # =============================================================================
    def _visaList(self):
        """detect available address"""
        try:
            resource_manager = visa.ResourceManager()
            self.pyvisa_list = resource_manager.list_resources()
            self.ui.listWidget.clear()
            self.ui.listWidget.addItems(self.pyvisa_list)

            # DAQ TODO:only one daq is available now 20210916
            system = System.local()
            for i, device in enumerate(system.devices):
                if i > 0:
                    self.ui.listWidget.addItem(device.name)
            self.ui.listWidget.addItem("default")
        except:
            logging.error('detect available address fail')

    def _intrumentList(self):
        """detect available drivers"""
        self.driver_list = load_drivers()
        self.ui.listWidget_2.clear()
        self.ui.listWidget_2.addItems(self.driver_list.keys())

    def _connectSignals(self):
        # page 1
        # Buttons
        self.ui.pushButton.clicked.connect(self._visaList)
        self.ui.pushButton_2.clicked.connect(self.connection)
        self.ui.pushButton_10.clicked.connect(self.deleteConnectedInstrument)
        # page 2
        # Buttons
        self.ui.pushButton_7.clicked.connect(self.readPanelShow)
        self.read_panel.ctr_ui.pushButton_5.clicked.connect(self.readConfirm)
        self.read_panel.ctr_ui.pushButton_5.clicked.connect(self.read_panel.close)
        self.read_panel.ctr_ui.pushButton_6.clicked.connect(self.read_panel.close)
        self.ui.pushButton_3.clicked.connect(self.readPanelShow)
        self.control_panel.read_ui.pushButton_9.clicked.connect(self.addLevel)
        self.control_panel.read_ui.pushButton_9.clicked.connect(self.control_panel.close)
        self.control_panel.read_ui.pushButton_8.clicked.connect(self.chooseAddChild)
        self.control_panel.read_ui.pushButton_8.clicked.connect(self.control_panel.close)
        self.control_panel.read_ui.pushButton_6.clicked.connect(self.control_panel.close)
        self.ui.pushButton_8.clicked.connect(self.deleteReadRow)
        self.ui.pushButton_9.clicked.connect(self.chooseDelete)
        self.ui.pushButton_26.clicked.connect(self.timeAddLevel)
        self.ui.pushButton_27.clicked.connect(self.timeAddChild)
        self.ui.pushButton_4.clicked.connect(self.folderMessage)
        # check box
        self.control_panel.read_ui.checkBox.stateChanged.connect(self.checkFunctionIncrement)
        # Tables
        self.ui.tableWidget_2.cellClicked.connect(self.showMethod)
        # treeWidget init
        self.tree = self.ui.treeWidget
        self.tree.itemClicked.connect(self.checkState)
        # page 3
        # Buttons
        self.ui.pushButton_13.clicked.connect(self.displayCursorCrossHair)
        self.ui.pushButton_12.clicked.connect(self.autoPlotRange)
        self.ui.pushButton_16.clicked.connect(self.plotSave)
        # Tables
        self.ui.tableWidget_5.cellClicked.connect(self.lineDisplaySwitch)

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
        """ Connect instrument and add to table_instrList """
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

                except visa.VisaIOError or AttributeError as e:
                    self.pageOneInformation(f"{instrument_type} connect fail")
                    logging.exception('connect fail', exc_info=e)
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

    def readConfirm(self):
        # Get the necessary info of the chosen item
        row = self.ui.tableWidget_2.currentRow()
        instrument_name = self.ui.tableWidget_2.item(row, 0).text()
        instrument_type = self.ui.tableWidget_2.item(row, 1).text()
        read_method = self.ui.listWidget_3.currentItem().text()
        magnification = self.read_panel.ctr_ui.lineEdit_2.text()
        Unit = self.read_panel.ctr_ui.lineEdit_3.text()

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

        method_row_len = self.ui.tableWidget_4.rowCount()
        self.pageTwoInformation(method_row_len)

        self.read_row_count += 1

        self.instruments_read.append(self.instruments[row])
        self.options_read.append(read_method)
        try:
            self.instruments_magnification.append(int(magnification))
        except ValueError:
            self.instruments_magnification.append(magnification)
            logging.warning('magnification is not int')

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
            self.control_panel.read_ui.checkBox.setChecked(False)
            self.checkState()
        else:
            self.pageTwoInformation('Time measurement - Please enter a number.')
        self.ui.lineEdit_5.clear()

    # treeWidget
    def addLevel(self, level_name):
        self.root = QTreeWidgetItem(self.tree)
        self.root.setText(0, '0')
        self.root.setFlags(self.root.flags() | Qt.ItemIsUserCheckable)
        self.root.setCheckState(0, Qt.Checked)
        self.root.setExpanded(True)
        self.updateInfo(self.root)
        self.control_panel.read_ui.checkBox.setChecked(False)
        self.control_panel.read_ui.lineEdit_5.setText('0')
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
        self.control_panel.read_ui.checkBox.setChecked(False)
        self.control_panel.read_ui.lineEdit_5.setText('0')
        self.checkState()

    def checkFunctionIncrement(self):
        if self.control_panel.read_ui.checkBox.isChecked():
            self.control_panel.read_ui.lineEdit_5.setEnabled(True)
        else:
            self.control_panel.read_ui.lineEdit_5.setEnabled(False)

    def updateInfo(self, item):
        row = self.ui.tableWidget_2.currentRow()
        Ins_name = self.ui.tableWidget_2.item(row, 0).text()
        Ins_type = self.ui.tableWidget_2.item(row, 1).text()
        control_method = self.ui.listWidget_3.currentItem().text()

        # TODO: restrict the the value to integer only or something related to the unit
        target = self.control_panel.read_ui.lineEdit_2.text()
        speed = self.control_panel.read_ui.lineEdit_3.text()

        # check box
        increment = self.control_panel.read_ui.lineEdit_5.text()
        control_list = [Ins_name, Ins_type, control_method, target, speed, increment]

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
        control_list = [Ins_name, Ins_type, control_method, target, speed, increment]
        for i, element in enumerate(control_list):
            item.setText((i+1), element)
        item.setText(7, row)

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
        sip.delete(item)
        self.checkState()

    # =============================================================================
    # Page 3
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
    #  Start and stop function
    # =============================================================================
    def folderMessage(self):
        cwd = os.getcwd()
        self.folder_address = QFileDialog.getExistingDirectory(self, "Please define the folder name", cwd)

        if self.folder_address != '':
            self.ui.label_18.setText(self.folder_address)
            cwd = self.folder_address

    def messageBox(self, message):
        QMessageBox.information(self, "Wrong!.", message)

    def fileExist(self):
        reply = QMessageBox.information(self, "Wrong!.", "The file has existed. Do you want to overwrite it?",
                                        QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
        if reply == QMessageBox.Close:
            QMessageBox.information(self, "Wrong!.", "Please adjust the file name.")
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
        # all data
        self.saved_data = {}
        # plot item
        self.data_line = []
        # line display switch
        self.switch_list = []

        for _ in range(self.read_len):
            self.data_line.append(self.ui.graphWidget.plot([]))
            self.y_data.append(np.array([], dtype=np.float32))
            self.switch_list.append(True)
            
    def plotUpdate(self, n, x, y_n, line_id):
        if n == 0:
            self.x_data = np.append(self.x_data, [x])
        self.y_data[n] = np.append(self.y_data[n], y_n)
        # setData to the PlotItems
        # TODO: self.choose_line_num==0 is not complete
        if self.switch_list[n] and self.choose_line_num==0:
            self.data_line[n].setData(self.x_data, self.y_data[n], pen=pg.mkPen(colorLoop(n+self.color_offset), width=1))
        elif self.switch_list[n] and line_id in self.choose_line:
            self.data_line[n].setData(self.x_data, self.y_data[n], pen=pg.mkPen(colorLoop(n+self.color_offset), width=1))

    def saveLines(self, file_count):
        for i in range(self.read_len):
            if self.switch_list[file_count%self.read_len]:
                self.ui.graphWidget.plot(self.x_data, self.y_data[i], pen=pg.mkPen(colorLoop(i+self.color_offset), width=1))
            addtwodimdict(self.saved_data, file_count, i, [self.x_data, self.y_data[i]])
            self.data_line[i].setData([])
            self.color_offset += 3
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
        else:
            self.switch_list[col] = True
        self.renewGraph()

    def renewGraph(self):
        self.plt.clear()
        self.color_offset = 0
        self.data_line = []
        for _ in range(self.read_len):
            self.data_line.append(self.ui.graphWidget.plot([]))

        # get choose_line_num
        self.choose_line_num = self.ui.spinBox_2.value()
        if self.choose_line_num == 0:
            self.choose_line_num = int(self.line_num_now)
        else:
            self.choose_line_num -= 1
        
        start = self.choose_line_start*self.choose_line_space
        self.choose_line = np.linspace(start, start+self.choose_line_space*self.choose_line_num, self.choose_line_num+1, dtype=np.int16)
        print(self.choose_line_num+1)
        print(self.choose_line)
        for curve_group in self.choose_line:
            for curve_num in range(self.read_len):
                if self.switch_list[curve_num]:                    
                    try:
                        data = self.saved_data[curve_group][curve_num]
                        print(f'curve_group:{curve_group}, curve_num:{curve_num}')
                        self.ui.graphWidget.plot(data[0], data[1], pen=pg.mkPen(colorLoop(curve_group+self.color_offset), width=1))
                        self.color_offset += 3
                    except KeyError:
                        pass
                    
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
        i = 0
        for i in range(self.read_len):
            self.ui.tableWidget_5.setItem(2, (i + 1), QTableWidgetItem(f'{y_show[i]:g}'))


class ControlPanel(QDialog):
    """Page 2 subwindow Control option panel"""

    def __init__(self):
        super(ControlPanel, self).__init__()
        self.read_ui = Control_Window()
        self.read_ui.setupUi(self)


class ReadlPanel(QDialog):
    """Page 2 subwindow Read option panel"""

    def __init__(self):
        super(ReadlPanel, self).__init__()
        self.ctr_ui = Read_Window()
        self.ctr_ui.setupUi(self)