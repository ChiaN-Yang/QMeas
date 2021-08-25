#!/usr/bin/env python
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
import pyqtgraph as pg
import pyqtgraph.exporters
from libs.visa_resource_manager import Ui_MainWindow
from libs.control_option import Ui_Dialog
from libs.read_option import Ui_Dialog as read_Ui_Dialog
import sys
import pyvisa as visa
import numpy as np
import os
from datetime import datetime
from libs.load_driver import load_drivers


# =============================================================================
# Main class
# =============================================================================

class MainWindow(QtWidgets.QMainWindow):

    name_count = 1
    row_count = 1
    read_row_count = 1
    control_row_count = 1
    click = 1
    time_unit = 0.1  # 0.1s
    sequence_num = 0
    sequence_step_num = 0
    driver_list = load_drivers()
    instruments = []
    instruments_control = []
    instruments_read = []
    data = []
    data_show = []
    sequence = []
    data_line = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.data_update)
        self.timer.timeout.connect(self.plot_update)

        # control panel & read panel
        self.sub_window = ControlPanel()
        self.sub_1_window = ReadlPanel()

        # Pre-run functions
        self.VisaList()

        # page 1
        # Buttons
        self.ui.pushButton.clicked.connect(self.VisaList)
        self.ui.pushButton_2.clicked.connect(self.Connection)
        self.ui.pushButton_10.clicked.connect(self.DeleteConnectedInstrument)
        # Tables
        self.ui.tableWidget.setColumnWidth(0, 100)
        self.ui.tableWidget.setColumnWidth(1, 200)

        # page 2
        # Buttons
        self.ui.pushButton_7.clicked.connect(self.sub_1_window.show)
        self.sub_1_window.sub_1_ui.pushButton_5.clicked.connect(
            self.ReadConfirm)
        self.sub_1_window.sub_1_ui.pushButton_5.clicked.connect(
            self.sub_1_window.close)
        self.sub_1_window.sub_1_ui.pushButton_6.clicked.connect(
            self.sub_1_window.close)
        self.ui.pushButton_3.clicked.connect(self.sub_window.show)
        self.sub_window.sub_ui.pushButton_5.clicked.connect(
            self.ControlConfirm)
        self.sub_window.sub_ui.pushButton_5.clicked.connect(
            self.ExperimentSequencer)
        self.sub_window.sub_ui.pushButton_5.clicked.connect(
            self.sub_window.close)
        self.sub_window.sub_ui.pushButton_6.clicked.connect(
            self.sub_window.close)

        self.ui.pushButton_8.clicked.connect(self.DeleteReadRow)
        self.ui.pushButton_9.clicked.connect(self.DeleteControlRow)
        self.ui.pushButton_5.clicked.connect(self.TimeGo)
        self.ui.pushButton_11.clicked.connect(self.TimeStop)
        self.ui.pushButton_25.clicked.connect(self.TimeMeasurement)
        # Tables
        self.ui.tableWidget_2.cellClicked.connect(self.ShowMethod)

        # page 3
        # Buttons
        self.ui.pushButton_13.clicked.connect(self.DisplayCursorCrossHair)
        self.ui.pushButton_13.clicked.connect(self.AutoPlotRange)
        # Tables
        self.ui.tableWidget_5.cellClicked.connect(self.LineDisplaySwitch)
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
        self.ui.actionQuit.triggered.connect(self.TimeStop)
        self.ui.actionQuit.triggered.connect(app.exit)

        # Set Window Icon
        self.setWindowIcon(QtGui.QIcon('Qfort.png'))

    # =============================================================================
    # Page 1
    # =============================================================================
    def VisaList(self):
        """detect available address"""
        resource_manager = visa.ResourceManager()
        self.pyvisa_list = resource_manager.list_resources()
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(self.pyvisa_list)
        self.IntrumentList()

    def IntrumentList(self):
        """detect available drivers"""
        self.ui.listWidget_2.clear()
        self.ui.listWidget_2.addItems(self.driver_list.keys())

    def PageOneInformation(self, string):
        """put some word in the information board"""
        self.ui.textBrowser.append(str(string))

    def DeleteConnectedInstrument(self):
        row = self.ui.tableWidget.currentRow()
        self.ui.tableWidget.removeRow(row)
        self.ui.tableWidget_2.removeRow(row)
        self.row_count -= 1
        self.instruments.pop(row)

    def Connection(self):
        """add instruments into table_instrList"""
        # Get info from lists and construct new object later
        visa_address = self.ui.listWidget.currentItem().text()
        instrument_type = self.ui.listWidget_2.currentItem().text()
        instrument_personal_name = self.ui.lineEdit.text()

        self.row_len = self.ui.tableWidget.rowCount()
        # Check existance
        if self.ui.tableWidget.findItems(visa_address, QtCore.Qt.MatchExactly) != [] or \
                self.ui.tableWidget.findItems(instrument_personal_name, QtCore.Qt.MatchExactly) != []:
            self.PageOneInformation('This VISA address or name has been used.')
        else:
            if instrument_type in self.driver_list.keys():
                try:
                    instrument_name = f'{instrument_type}_{self.name_count}'
                    self.name_count += 1

                    instrument = self.driver_list[instrument_type](
                        visa_address, instrument_name, instrument_type)
                    self.instruments.append(instrument)

                    # TODO: add some condition to check if Connection is successful
                    self.PageOneInformation(
                        f'self.{instrument_name} = {instrument_type}("{visa_address}")')
                    self.PageOneInformation(
                        f'{instrument_type} has been connected successfully.')
                    # TODO: add initialization option on messagebox and show the related info

                    # Add new row if necessary
                    if self.row_count > self.row_len:
                        self.ui.tableWidget.insertRow(self.row_len)
                        self.ui.tableWidget_2.insertRow(self.row_len)

                    # Assign varibales to current var
                    instrument_property = [
                        instrument_personal_name, instrument_type, visa_address]
                    for i, p in enumerate(instrument_property):
                        if p == '':
                            p = instrument_name
                        # Update the info to the table in page 1
                        self.ui.tableWidget.setItem(
                            self.row_count - 1, i, QtWidgets.QTableWidgetItem(p))

                    # Update the left top table in page 2
                    if instrument_personal_name == '':
                        instrument_personal_name = instrument_name
                    self.ui.tableWidget_2.setItem(
                        self.row_count - 1, 0, QtWidgets.QTableWidgetItem(instrument_personal_name))
                    self.ui.tableWidget_2.setItem(
                        self.row_count - 1, 1, QtWidgets.QTableWidgetItem(instrument_type))
                    self.row_count += 1

                except visa.VisaIOError or AttributeError:
                    self.PageOneInformation(
                        "%s connect fail" % instrument_type)

    # =============================================================================
    # Page 2
    # =============================================================================

    def PageTwoInformation(self, string):
        self.ui.textBrowser_2.append(str(string))

    def DeleteReadRow(self):
        row = self.ui.tableWidget_4.currentRow()
        self.ui.tableWidget_4.removeRow(row)
        self.ui.tableWidget_5.removeColumn(row)
        self.read_row_count -= 1
        self.instruments_read.pop(row)

    def DeleteControlRow(self):
        row = self.ui.tableWidget_3.currentRow()
        self.ui.tableWidget_3.removeRow(row)
        self.control_row_count -= 1
        self.instruments_control.pop(row)

    def ShowMethod(self):
        row = self.ui.tableWidget_2.currentRow()
        instrument = self.instruments[row]
        self.ui.listWidget_3.clear()

        # show the method of the chosen itesm to the list
        self.ui.listWidget_3.addItems(instrument.METHOD)
        # TODO: add the waiting-time measurement to the option

    def ReadConfirm(self):
        # Get the necessary info of the chosen item
        row = self.ui.tableWidget_2.currentRow()
        instrument_name = self.ui.tableWidget_2.item(row, 0).text()
        instrument_type = self.ui.tableWidget_2.item(row, 1).text()
        read_method = self.ui.listWidget_3.currentItem().text()
        Magnification = self.sub_1_window.sub_1_ui.lineEdit_2.text()
        Unit = self.sub_1_window.sub_1_ui.lineEdit_3.text()

        # Add new row if necessary
        self.row_len = self.ui.tableWidget_4.rowCount()

        if self.read_row_count > self.row_len:
            self.ui.tableWidget_4.insertRow(self.row_len)
            self.ui.tableWidget_5.insertColumn(self.row_len + 1)

        # Assign the variables to the table in page 2

        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 0, QtWidgets.QTableWidgetItem(instrument_name))
        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 1, QtWidgets.QTableWidgetItem(instrument_type))
        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 2, QtWidgets.QTableWidgetItem(read_method))
        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 3, QtWidgets.QTableWidgetItem(Magnification))
        self.ui.tableWidget_4.setItem(
            self.read_row_count - 1, 4, QtWidgets.QTableWidgetItem(Unit))

        # initialize the blocks in the read option
        self.sub_1_window.sub_1_ui.lineEdit_2.setText("1")
        self.sub_1_window.sub_1_ui.lineEdit_3.clear()

        # Assign the variables to the table in page 3
        self.ui.tableWidget_5.setItem(
            0, self.read_row_count, QtWidgets.QTableWidgetItem(instrument_name))
        self.ui.tableWidget_5.setItem(
            1, self.read_row_count, QtWidgets.QTableWidgetItem(read_method))

        method_row_len = self.ui.tableWidget_4.rowCount()
        self.PageTwoInformation(method_row_len)

        self.read_row_count += 1

        self.instruments_read.append(self.instruments[row])

    def ControlConfirm(self):
        # Get the necessary info of the chosen item
        row = self.ui.tableWidget_2.currentRow()
        instrument_name = self.ui.tableWidget_2.item(row, 0).text()
        instrument_type = self.ui.tableWidget_2.item(row, 1).text()
        control_method = self.ui.listWidget_3.currentItem().text()

        # TODO: restrict the the value to integer only or something related to the unit
        target = self.sub_window.sub_ui.lineEdit_2.text()
        speed = self.sub_window.sub_ui.lineEdit_3.text()

        # Add new row if necessary
        row_len = self.ui.tableWidget_3.rowCount()
        if self.control_row_count > row_len:
            self.ui.tableWidget_3.insertRow(row_len)

        # Assign the variables to the table
        self.ui.tableWidget_3.setItem(
            self.control_row_count - 1, 0, QtWidgets.QTableWidgetItem(instrument_name))
        self.ui.tableWidget_3.setItem(
            self.control_row_count - 1, 1, QtWidgets.QTableWidgetItem(instrument_type))
        self.ui.tableWidget_3.setItem(
            self.control_row_count - 1, 2, QtWidgets.QTableWidgetItem(control_method))
        self.ui.tableWidget_3.setItem(
            self.control_row_count - 1, 3, QtWidgets.QTableWidgetItem(target))
        self.ui.tableWidget_3.setItem(
            self.control_row_count - 1, 4, QtWidgets.QTableWidgetItem(speed))

        # Empty the blocks in the control option
        self.sub_window.sub_ui.lineEdit_2.clear()
        self.sub_window.sub_ui.lineEdit_3.clear()

        # Initial the control varibales to the table in page 3
        if self.control_row_count == 1:
            self.ui.tableWidget_5.setItem(
                0, 0, QtWidgets.QTableWidgetItem(instrument_name))
            self.ui.tableWidget_5.setItem(
                1, 0, QtWidgets.QTableWidgetItem(control_method))

        self.control_row_count += 1

        self.instruments_control.append(self.instruments[row])

    def SwitchToPlotTab(self):
        self.ui.tabWidget.setCurrentIndex(2)

    def TimeMeasurement(self):
        """ Provide another option to do the time measurement """
        wait_time = self.ui.lineEdit_5.text()

        if wait_time.isnumeric():
            row_len = self.ui.tableWidget_3.rowCount()
            if self.control_row_count > row_len:
                self.ui.tableWidget_3.insertRow(row_len)

            # Assign the variables to the table
            self.ui.tableWidget_3.setItem(
                self.control_row_count - 1, 0, QtWidgets.QTableWidgetItem('Time(s)'))
            self.ui.tableWidget_3.setItem(
                self.control_row_count - 1, 1, QtWidgets.QTableWidgetItem('-'))
            self.ui.tableWidget_3.setItem(
                self.control_row_count - 1, 2, QtWidgets.QTableWidgetItem('-'))
            self.ui.tableWidget_3.setItem(
                self.control_row_count - 1, 3, QtWidgets.QTableWidgetItem('0'))
            self.ui.tableWidget_3.setItem(
                self.control_row_count - 1, 4, QtWidgets.QTableWidgetItem('-'))
            self.ui.tableWidget_3.setItem(
                self.control_row_count - 1, 5, QtWidgets.QTableWidgetItem(wait_time))

            self.control_row_count += 1
        else:
            self.PageTwoInformation(
                'Time measurement - Please enter a number.')
        # Add new row if necessary

    # =============================================================================
    # Page 3
    # =============================================================================

    def PageThreeInformation(self, string):
        self.ui.textBrowser_3.clear
        self.ui.textBrowser_3.append(str(string))

    # Add crosshair lines.
    def DisplayCursorCrossHair(self):

        if self.ui.pushButton_13.isChecked():
            self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
            self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
            self.ui.graphWidget.addItem(self.crosshair_v, ignoreBounds=True)
            self.ui.graphWidget.addItem(self.crosshair_h, ignoreBounds=True)

            self.proxy = pg.SignalProxy(self.ui.graphWidget.scene(
            ).sigDisplayCursorCoordinate, rateLimit=60, slot=self.DisplayCursorCoordinate)
        else:
            self.ui.graphWidget.removeItem(self.crosshair_h)
            self.ui.graphWidget.removeItem(self.crosshair_v)
            self.proxy = []

    def DisplayCursorCoordinate(self, e):
        pos = e[0]
        if self.ui.graphWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.ui.graphWidget.getPlotItem().vb.mapSceneToView(pos)
            self.crosshair_v.setPos(mousePoint.x())
            self.crosshair_h.setPos(mousePoint.y())

    def AutoPlotRange(self):
        # TODO: auto view when clicking is still not working
        self.viewbox.enableAutoRange()
        self.viewbox.disableAutoRange()

    # =============================================================================
    #  Control setting
    # =============================================================================
    def UpdateTable5FirstColumnTitle(self, sequence_num):
        instrument_name = self.ui.tableWidget_3.item(sequence_num, 0).text()
        control_method = self.ui.tableWidget_3.item(sequence_num, 3).text()

        self.ui.tableWidget_5.setItem(
            0, 0, QtWidgets.QTableWidgetItem(instrument_name))
        self.ui.tableWidget_5.setItem(
            1, 0, QtWidgets.QTableWidgetItem(control_method))

    def ExperimentSequencer(self):
        self.control_row_len = self.ui.tableWidget_3.rowCount()
        self.max_sequence_num = self.control_row_len
        self.sequence = []
        self.sequence = [f'sequence_{i}' for i in range(self.control_row_len)]
        for i in range(self.control_row_len):
            target_value = self.ui.tableWidget_3.item(i, 3).text()
            speed = self.ui.tableWidget_3.item(i, 4).text()
            time_unit = self.time_unit
            control_property = self.ui.tableWidget_3.item(i, 2).text()
            self.sequence[i] = self.instruments_control[i].experimentLinspacer(
                target_value, speed, time_unit, control_property)
            self.PageTwoInformation(len(self.sequence[i]))

    def UpdateTable5XData(self, value):
        self.ui.tableWidget_5.setItem(
            2, 0, QtWidgets.QTableWidgetItem(f'{value:g}'))

    def XDataAppendAndTxtWrite(self, value):
        # TODO: X should append the value from instrument instead of that from sequence list
        self.x.append(value)
        self.TxtWrite(-1, value)

    # =============================================================================
    #  Read setting
    # =============================================================================

    def CreatEmptyDataSet(self):
        """
        this function mainly creat 2 varibles for the recording and display
        1. self.data_show_%d -- used for displaying the value
        2. self.data_%d -- append all data
        the detailed coding method are explained in the function "data_upadate"
        """
        self.x = []
        self.data_show = [[0 for _ in range(1)] for _ in range(self.method_row_len)]
        self.data = [[0 for _ in range(1)] for _ in range(self.method_row_len)]

    def UpdateTable5ReadData(self, i):
        # assign the self.data_show_%d to the tablewidget_5 as the display method
        temp = self.data_show[i]
        self.ui.tableWidget_5.setItem(
            2, i + 1, QtWidgets.QTableWidgetItem(f'{temp:g}'))

    def read_function_processor(self, i, Ins_method, magnification):
        '''Method_dict['SR830']['Voltage']  = sin_voltage'''
        self.instruments_read[i].performOpen(Ins_method)
        # Assign the read value to list "data_show[i]" and data[i]
        self.data_show[i] = self.instruments_read[i].performGetValue(Ins_method) * magnification
        # XY data append
        self.data[i].append(self.data_show[i])
        # write data
        self.TxtWrite(i, self.data_show[i])

    # =============================================================================
    #  Update setting
    # =============================================================================
    def data_update(self):
        """
        this function mainly keep updating 2 variables:
        1. self.data_show -- used for displaying the value
        2. self.data -- append all data
        to obtain the read value, the Ins_name, Ins_type, Ins_method are needed
        by combining all the above parameters, we can find the correct function
        corresponding to what we want to measure,
        e.g.
        self.data_show_%d = self.%s.%s" %(i, Ins_name, Method_dict[Ins_type][Ins_method]))

        Ins_name = SR830_1
        Ins_type = SR830
        Ins_method = Voltage

        Method_dict[Ins_type][Ins_method] equals to sin_voltage

        we are actually running self.data.show_0 = self.SR830_1.sin_voltage,
        which is the voltage value of the insturemnt SR830_1
        """
        # control instrument
        control_instrument_method = self.ui.tableWidget_3.item(
            self.sequence_num, 2).text()
        set_value = self.instruments_control[self.sequence_num].performSetValue(
            self.sequence[self.sequence_num][self.sequence_step_num], control_instrument_method)
        self.XDataAppendAndTxtWrite(set_value)

        # read instruments and show the data
        for i in range(self.method_row_len):
            Ins_method = self.ui.tableWidget_4.item(i, 2).text()
            # add Magnification to the value
            Magnification = float(
                "%e" % (float(self.ui.tableWidget_4.item(i, 3).text())))
            # read_function_processor
            self.read_function_processor(
                i, Ins_method, Magnification)
            # show x axis
            self.UpdateTable5XData(set_value)
            # show y axis
            self.UpdateTable5ReadData(i)
            # TODO: assign the value to a temp variable to make the plot value and record value same

    # =============================================================================
    #         c_time = datetime.now()
    #         d_time = c_time - s_time
    #         d_sec = str(d_time.total_seconds())
    #         x.append(float(d_sec))
    # =============================================================================

        # Change to next sequence and stop if all sequeces is finished
        self.sequence_step_num += 1
        x_length = len(self.sequence[self.sequence_num])
        if self.sequence_step_num == x_length-1:
            # empty the all append data
            for i in range(self.method_row_len):
                self.x = []
                self.data[i] = []
            self.sequence_num += 1
            if self.sequence_num == self.max_sequence_num:
                self.TimeStop()
            else:
                self.UpdateTable5FirstColumnTitle(self.sequence_num)

    # =============================================================================
    #    Timer setting
    # =============================================================================
    def TimeGo(self):
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
            self.full_name = self.name + '.txt'
            List = os.listdir()
            if self.full_name in List:
                reply = QMessageBox.information(
                    self, "Wrong!.", "The file has existed. Do you want to overwrite it?",
                    QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
                if reply == QMessageBox.Close:
                    QMessageBox.information(
                        self, "Wrong!.", "Please adjust the file name.")
                elif reply == QMessageBox.Ok:
                    self.CreateEmptyLines()
                    self.CreatNewTxt(self.full_name)
                    self.SwitchToPlotTab()
                    self.CreatEmptyDataSet()
                    self.timer.start(self.time_unit)
                    self.s_time = datetime.now()

            else:
                self.CreateEmptyLines()
                self.CreatNewTxt(self.full_name)
                self.SwitchToPlotTab()
                self.CreatEmptyDataSet()
                self.timer.start(self.time_unit)

    def TimeStop(self):
        # time stop
        self.timer.stop()
        self.sequence_num = 0
        self.x = []
        for i in range(self.control_row_len):
            self.sequence[i] = []

    # =============================================================================
    # Text write setting
    # =============================================================================

    def CreatNewTxt(self, full_name):
        """
        creat the txt file
        the name of file and title are according to the user-defined file name
        and the method (control/read) properties of the instrument
        """
        self.method_row_len = self.ui.tableWidget_4.rowCount()
        f = open(full_name, 'w')

        title = 'X axis, '
        f.write(title)
        for i in range(self.method_row_len):
            Ins_name = self.ui.tableWidget_4.item(i, 0).text()
            Ins_method = self.ui.tableWidget_4.item(i, 2).text()
            Unit = self.ui.tableWidget_4.item(i, 4).text()
            temp_title = Ins_name + '-' + Ins_method + '(' + Unit + ')'
            # TODO: \n still has some issue when only one reading and only one running
            if i == self.method_row_len - 1:
                f.write(str(temp_title))
                f.write('\n')
            else:
                f.write(str(temp_title))
                f.write(', ')

        f.close()

    def TxtWrite(self, i, data):
        # TODO: separate the data of different sequece
        """
        write the value to the txt file which is created at beginning
        the i value affects the writing mode to control it changes line
        """
        f = open(self.full_name, 'a')
        if i == self.method_row_len - 1:
            f.write(str(data))
            f.write('\n')
        else:
            f.write(str(data))
            f.write(',')

    # =============================================================================
    # plot setting
    # =============================================================================
    def CreateEmptyLines(self):
        """
        creat the plotDataItem as data_line_%d where %d = 0, 1, 2... (reference)
        the x y value will be set later within the function plot_update()
        """
        self.method_row_len = self.ui.tableWidget_4.rowCount()
        self.plt.clear()
        for i in range(self.method_row_len):
            self.data_line.append(self.ui.graphWidget.plot([]))

    def plot_update(self):
        """ The plot data is from the self.data_%d. Make sure the data is correct
            before the assingment
            setData to references (data_line_%d where %d = 0, 1, 2...) (reference)
            click (1 or 0) is the switch to decide if the line will show
            col is the column number where the mouse clicks
        """
        col = self.ui.tableWidget_5.currentColumn()
        for i in range(self.method_row_len):
            if self.click == 0 and i == col:
                self.data_line[i].setData([])
            else:
                self.data_line[i].setData(
                    self.x, self.data[i], pen=pg.mkPen(pg.intColor(i+1)))

    def LineDisplaySwitch(self):
        """ this function is connected to tableWidget_5 on page 3
            the function activates whenever the tablewidge_5 is clicked
            TODO: this function is not well working. it needs to establish multiple
            switch to each channel
        """
        if self.click == 1:
            self.click = 0
        elif self.click == 0:
            self.click = 1


# =============================================================================
# Page 2 subwindow Control option panel
# =============================================================================
class ControlPanel(QtWidgets.QDialog):
    def __init__(self):
        super(ControlPanel, self).__init__()
        self.sub_ui = Ui_Dialog()
        self.sub_ui.setupUi(self)


class ReadlPanel(QtWidgets.QDialog):
    def __init__(self):
        super(ReadlPanel, self).__init__()
        self.sub_1_ui = read_Ui_Dialog()
        self.sub_1_ui.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
