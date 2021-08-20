# -*- coding: utf-8 -*-
"""
Created on Wed May  5 07:53:54 2021

@author: SOC
"""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
import pyqtgraph as pg
import pyqtgraph.exporters
from visa_rm_v1 import Ui_MainWindow
from control_option_v1 import Ui_Dialog
from read_option import Ui_Dialog as read_Ui_Dialog
import sys
import pyvisa as visa
import numpy as np
import os
from datetime import datetime

# Instruments
from pymeasure.instruments.srs.sr830 import SR830
from pymeasure.instruments.signalrecovery.dsp7265 import DSP7265
from pymeasure.instruments.keithley import Keithley2400
from labdrivers.oxford import IPS120
from labdrivers.oxford import mercuryips_GPIB


# =============================================================================
# Initialize some paramters
# =============================================================================
name_count = 1
row_count = 1
temp = 0
read_row_count = 1
control_row_count = 1
click = 1
time_unit = 0.1 # 0.1s
seq_num = 0
step_num = 0
# =============================================================================
# Methods to real function conversion dictionary
# =============================================================================

# =============================================================================
# All possible output and input options
# =============================================================================
# SR830
SR830_Method = {'Voltage':'sine_voltage',
                'Frequency':'frequency',
                'Magnitude(R)':'magnitude',
                'Magnitude(X)':'x',
                'Phase':'theta',
                'Analog in 1':'aux_in_1',
                'Analog in 2':'aux_in_2'}
# TODO: add all functions to the rest of instrument depending on the control / read choice
# TODO: arrang all function in this order: {'certain property':[[read functions],[control functions]]}
# DSP7265
DSP7265_Method = ['Voltage','Frequency','Current','Phase']

# Keithley2400
Keithely_2400_Method = {'Current':['measure_current()','current','source_current'],
                        'Voltage':['measure_voltage()','voltage','source_voltage']}

# IPS 120
IPS_120_Method = {'Magnetic field':['readField()', 'setFieldSetpoint()']}

# Mercury IPS 
Mercury_IPS_Method = {'Magnetic field':['readField()','setFieldSetpoint'],
                      'current':'readcurrent'}

# Mercury ITC
Mercury_ITC_Method = ['Temperature','Needle valve']

# Dictionary
Method_dict = {'SR830':SR830_Method,
               'DSP7265':DSP7265_Method,
               'Keithley2400':Keithely_2400_Method,
               'IPS120':IPS_120_Method,
               'mercruyIPS':Mercury_IPS_Method,
               'mercruyITC':Mercury_ITC_Method}
# =============================================================================
# Main class
# =============================================================================
class MainWindow_p1(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow_p1, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.data_update)
        self.timer.timeout.connect(self.plot_update)

        # control panel & read panel
        self.sub_window = control_panel()
        self.sub_1_window = read_panel()
        
        # Pre-run functions
        self.visa_list()  

        # page 1
        # Buttons
        self.ui.pushButton.clicked.connect(self.visa_list)
        self.ui.pushButton_2.clicked.connect(self.connection)
        self.ui.pushButton_10.clicked.connect(self.delete_connected_ins)
        # Tables
        self.ui.tableWidget.setColumnWidth(0, 100);
        self.ui.tableWidget.setColumnWidth(1, 200);
        
        # page 2      
        # Buttons
        self.ui.pushButton_7.clicked.connect(self.sub_1_window.show)
        self.sub_1_window.sub_1_ui.pushButton_5.clicked.connect(self.read_choose)
        self.sub_1_window.sub_1_ui.pushButton_5.clicked.connect(self.sub_1_window.close)
        self.sub_1_window.sub_1_ui.pushButton_6.clicked.connect(self.sub_1_window.close)
        self.ui.pushButton_3.clicked.connect(self.sub_window.show)
        self.sub_window.sub_ui.pushButton_5.clicked.connect(self.control_choose)
        self.sub_window.sub_ui.pushButton_5.clicked.connect(self.sequencer)
        self.sub_window.sub_ui.pushButton_5.clicked.connect(self.sub_window.close)
        self.sub_window.sub_ui.pushButton_6.clicked.connect(self.sub_window.close)

        self.ui.pushButton_8.clicked.connect(self.delete_read)
        self.ui.pushButton_9.clicked.connect(self.delete_control)
        self.ui.pushButton_5.clicked.connect(self.timeGo)
        self.ui.pushButton_11.clicked.connect(self.timeStop)
        self.ui.pushButton_25.clicked.connect(self.waiting_time)
        # Tables
        self.ui.tableWidget_2.cellClicked.connect(self.show_method)


        
        # page 3
        #Buttons
        self.ui.pushButton_13.clicked.connect(self.cursor_postion_active)
        self.ui.pushButton_13.clicked.connect(self.auto_range)
        # Tables
        self.ui.tableWidget_5.cellClicked.connect(self.plot_click_option)
        # plot widget       
        # TODO: add the real time x y coordinate the corner

        pg.setConfigOptions(antialias=False)
        self.plt = self.ui.graphWidget
        # viewbox setting
        self.vb = self.plt.getViewBox()
        self.vb.disableAutoRange() # Side note: this function can be connected 
        # to a button, e.g., AUTO button = enable it first and disable it
        # plot setting
        self.plt.showGrid(x = True, y = True, alpha = 1)
        self.plt.setLabel('bottom', '   ')
        self.plt.setLabel('left', '   ')

        
        # Menu
        self.ui.retranslateUi(self)
        self.ui.actionQuit.setShortcut('Ctrl+Q')
        self.ui.actionQuit.triggered.connect(self.timeStop)
        self.ui.actionQuit.triggered.connect(app.exit)
        
        # Set Window Icon
        self.setWindowIcon(QtGui.QIcon('Qfort.png'))
        
        # some necessary var
        self.NAME = []
        self.METHOD = []

# =============================================================================
# Page 1    
# =============================================================================
    def visa_list(self):
        rm = visa.ResourceManager()
        pyvisa_list = rm.list_resources()
        self.ui.listWidget.clear()
        self.pyvisa_list = pyvisa_list
        self.ui.listWidget.addItems(self.pyvisa_list)
    
    def p_1_info(self,string):
        self.ui.textBrowser.append(str(string))
        
    def delete_connected_ins(self):
        global row_count
        row = self.ui.tableWidget.currentRow()
        self.ui.tableWidget.removeRow(row)
        self.ui.tableWidget_2.removeRow(row)
        row_count = row_count - 1
        
    def connection(self):
        global row_count, temp, NAME, METHOD, L, name_count, type_list
        
        # Get info from lists and construct new object later
        Ins_VISA_add = self.ui.listWidget.currentItem().text()
        Ins_type = self.ui.listWidget_2.currentItem().text()
        Ins_name =  self.ui.lineEdit.text()
         
        row_len = self.ui.tableWidget.rowCount()
        # Check existance
        if self.ui.tableWidget.findItems(Ins_VISA_add,QtCore.Qt.MatchExactly) != [] or self.ui.tableWidget.findItems(Ins_name,QtCore.Qt.MatchExactly) != []:
            self.p_1_info('This VISA address or name has been used.')
        else:
            # List all available insturements
            # TODO: this list can be written as list(Method_dict.keys())
            type_list = list(Method_dict.keys())

            for t in type_list:
                
                if t in Ins_type:
                    try:
                        if Ins_name == '':
                            Ins_name = t + '_' + str(name_count)
                            name_count = name_count + 1
                        # Creat a dictionary to assign variable name and associated value(string)
                        # The reason is to aviod wrong var name, e.g., self.A.Lock-in SR830 = 'Lock-in SR830'
                        Ins_property = {'Ins_name': Ins_name, 'Ins_type': Ins_type, 'Ins_VISA_add': Ins_VISA_add}
                        
                        exec("self.%s = %s('%s')" %(Ins_name, t, Ins_VISA_add))
                        # TODO: add some condition to check if connection is successful
                        self.p_1_info("self.%s = %s('%s')" %(Ins_name, t, Ins_VISA_add))
                        self.p_1_info('%s has been connected successfully.' %Ins_type)
                        # TODO: add initialization option on messagebox and show the related info
                        # Add new row if necessary
                        if row_count > row_len:
                                self.ui.tableWidget.insertRow(row_len)
                                self.ui.tableWidget_2.insertRow(row_len)
                        # Assign varibales to current var
                        for p in Ins_property:
                            exec("self.%s.%s = '%s'" %(Ins_name,p,Ins_property[p]))                    
                        
                            # Update the info to the table   
                            self.ui.tableWidget.setItem(row_count - 1, temp, QtWidgets.QTableWidgetItem(Ins_property[p]));
                            # TODO: this part can be revised by function enumerate so that var 'temp' can be removed
                            temp = temp + 1
                        # Combine the method to the object
                        exec("self.%s.method = []" %(Ins_name))
                        for i in range(len(list(Method_dict[t].keys()))):
                            exec("self.%s.method.append('%s')" %(Ins_name, list(Method_dict[t].keys())[i]))
                        
                        
                        # Update the left top table in page 2
                        self.ui.tableWidget_2.setItem(row_count - 1, 0, QtWidgets.QTableWidgetItem(Ins_name));
                        self.ui.tableWidget_2.setItem(row_count - 1, 1, QtWidgets.QTableWidgetItem(Ins_type));
                        temp = 0
                        row_count = row_count + 1
                        
                        # Creat 2 Lists for plotting: self.NAME and self.METHOD
                        self.NAME = np.append(self.NAME,Ins_name)
                        # Add Ins_name to the beginning of every method
                        for i in range(len(list(Method_dict[t].keys()))):
                            method_temp = '%s_'%Ins_name + list(Method_dict[t].keys())[i]
                            self.METHOD = np.append(self.METHOD,method_temp)
                            
                    except visa.VisaIOError or AttributeError:
                        self.p_1_info("%s connect fail" %Ins_type)
            
# =============================================================================
# Page 2
# =============================================================================
    
    def p_2_info(self,string):
        self.ui.textBrowser_2.append(str(string))
        
    def delete_read(self):
        global read_row_count
        row = self.ui.tableWidget_4.currentRow()
        self.ui.tableWidget_4.removeRow(row)
        self.ui.tableWidget_5.removeColumn(row)
        read_row_count = read_row_count - 1
        
    def delete_control(self):
        global control_row_count
        row = self.ui.tableWidget_3.currentRow()
        self.ui.tableWidget_3.removeRow(row)
        control_row_count = control_row_count - 1
        
        
    def show_method(self):
        row = self.ui.tableWidget_2.currentRow()
        Ins_name = self.ui.tableWidget_2.item(row, 0).text()
        self.ui.listWidget_3.clear()

        # show the method of the chosen itesm to the list
        exec("self.ui.listWidget_3.addItems(self.%s.method)" %(Ins_name))
        # TODO: add the waiting-time measurement to the option

        
    def read_choose(self):
        global read_row_count, type_list, method_row_len
        
        # Get the necessary info of the chosen item
        row = self.ui.tableWidget_2.currentRow()
        Ins_name = self.ui.tableWidget_2.item(row, 0).text()
        Ins_type = self.ui.tableWidget_2.item(row, 1).text()
        read_method = self.ui.listWidget_3.currentItem().text()
        Magnification = self.sub_1_window.sub_1_ui.lineEdit_2.text()
        Unit = self.sub_1_window.sub_1_ui.lineEdit_3.text()
        
        # Add new row if necessary
        row_len = self.ui.tableWidget_4.rowCount()
        
        if read_row_count > row_len:
            self.ui.tableWidget_4.insertRow(row_len)
            self.ui.tableWidget_5.insertColumn(row_len + 1)
        
        # Assign the variables to the table in page 2

        self.ui.tableWidget_4.setItem(read_row_count - 1, 0, QtWidgets.QTableWidgetItem(Ins_name))
        self.ui.tableWidget_4.setItem(read_row_count - 1, 1, QtWidgets.QTableWidgetItem(Ins_type))
        self.ui.tableWidget_4.setItem(read_row_count - 1, 2, QtWidgets.QTableWidgetItem(read_method))
        self.ui.tableWidget_4.setItem(read_row_count - 1, 3, QtWidgets.QTableWidgetItem(Magnification))
        self.ui.tableWidget_4.setItem(read_row_count - 1, 4, QtWidgets.QTableWidgetItem(Unit))
        
        # initialize the blocks in the read option
        self.sub_1_window.sub_1_ui.lineEdit_2.setText("1")
        self.sub_1_window.sub_1_ui.lineEdit_3.clear()
        
        # Assign the variables to the table in page 3
        self.ui.tableWidget_5.setItem(0, read_row_count, QtWidgets.QTableWidgetItem(Ins_name))
        self.ui.tableWidget_5.setItem(1, read_row_count, QtWidgets.QTableWidgetItem(read_method))
        
        for t in type_list:
                if t in Ins_type:
                    Ins_type = t
        if Ins_type == 'Keithley2400':
            exec("self.%s.%s" %(Ins_name, Method_dict[Ins_type][read_method][0]))

        method_row_len = self.ui.tableWidget_4.rowCount()
        self.p_2_info(method_row_len)
        
        read_row_count = read_row_count + 1
        

    def control_choose(self):
        global control_row_count
        
        # Get the necessary info of the chosen item
        row = self.ui.tableWidget_2.currentRow()
        Ins_name = self.ui.tableWidget_2.item(row, 0).text()
        Ins_type = self.ui.tableWidget_2.item(row, 1).text()
        control_method = self.ui.listWidget_3.currentItem().text()
        
        # TODO: restrict the the value to integer only or something related to the unit
        target = self.sub_window.sub_ui.lineEdit_2.text()
        speed = self.sub_window.sub_ui.lineEdit_3.text()

        
        # Add new row if necessary
        row_len = self.ui.tableWidget_3.rowCount()
        if control_row_count > row_len:
            self.ui.tableWidget_3.insertRow(row_len)
        
        # Assign the variables to the table
        self.ui.tableWidget_3.setItem(control_row_count - 1, 0, QtWidgets.QTableWidgetItem(Ins_name))
        self.ui.tableWidget_3.setItem(control_row_count - 1, 1, QtWidgets.QTableWidgetItem(Ins_type))
        self.ui.tableWidget_3.setItem(control_row_count - 1, 2, QtWidgets.QTableWidgetItem(control_method))
        self.ui.tableWidget_3.setItem(control_row_count - 1, 3, QtWidgets.QTableWidgetItem(target))
        self.ui.tableWidget_3.setItem(control_row_count - 1, 4, QtWidgets.QTableWidgetItem(speed))
        
        # Empty the blocks in the control option
        self.sub_window.sub_ui.lineEdit_2.clear()
        self.sub_window.sub_ui.lineEdit_3.clear()
        
        # Initial the control varibales to the table in page 3
        if control_row_count == 1:
            self.ui.tableWidget_5.setItem(0, 0, QtWidgets.QTableWidgetItem(Ins_name))
            self.ui.tableWidget_5.setItem(1, 0, QtWidgets.QTableWidgetItem(control_method))        
        
        control_row_count = control_row_count + 1
    
    def switch_to_plot_tab(self):    
        self.ui.tabWidget.setCurrentIndex(2)
        
    def waiting_time(self):
        global control_row_count
        wait_time = self.ui.lineEdit_5.text()
        
        if wait_time.isnumeric():
            row_len = self.ui.tableWidget_3.rowCount()
            if control_row_count > row_len:
                self.ui.tableWidget_3.insertRow(row_len)
            
            # Assign the variables to the table
            self.ui.tableWidget_3.setItem(control_row_count - 1, 0, QtWidgets.QTableWidgetItem('Time(s)'))
            self.ui.tableWidget_3.setItem(control_row_count - 1, 1, QtWidgets.QTableWidgetItem('-'))
            self.ui.tableWidget_3.setItem(control_row_count - 1, 2, QtWidgets.QTableWidgetItem('-'))
            self.ui.tableWidget_3.setItem(control_row_count - 1, 3, QtWidgets.QTableWidgetItem('0'))
            self.ui.tableWidget_3.setItem(control_row_count - 1, 4, QtWidgets.QTableWidgetItem('-'))
            self.ui.tableWidget_3.setItem(control_row_count - 1, 5, QtWidgets.QTableWidgetItem(wait_time))
            
            control_row_count = control_row_count + 1
        else:
            self.p_2_info('Time measurement - Please enter a number.')
        # Add new row if necessary
        
        
        
# =============================================================================
# Page 3
# =============================================================================
    def p_3_info(self,string):
        self.ui.textBrowser_3.clear
        self.ui.textBrowser_3.append(str(string))
        
    # Add crosshair lines.
    def cursor_postion_active(self):

        if self.ui.pushButton_13.isChecked():
            self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
            self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
            self.ui.graphWidget.addItem(self.crosshair_v, ignoreBounds=True)
            self.ui.graphWidget.addItem(self.crosshair_h, ignoreBounds=True)
            
            self.proxy = pg.SignalProxy(self.ui.graphWidget.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        else:
            self.ui.graphWidget.removeItem(self.crosshair_h)
            self.ui.graphWidget.removeItem(self.crosshair_v)
            self.proxy = []

    def mouseMoved(self, e):
        pos = e[0]
        if self.ui.graphWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.ui.graphWidget.getPlotItem().vb.mapSceneToView(pos)
            self.crosshair_v.setPos(mousePoint.x())
            self.crosshair_h.setPos(mousePoint.y())
     
    def auto_range(self):
        # TODO: auto view when clicking is still not working
        self.vb.enableAutoRange()
        self.vb.disableAutoRange()

# =============================================================================
#  Control setting
# =============================================================================
    def title_update(self, seq_num):
        Ins_name = self.ui.tableWidget_3.item(seq_num, 0).text()
        control_method = self.ui.tableWidget_3.item(seq_num, 3).text()
        
        self.ui.tableWidget_5.setItem(0, 0, QtWidgets.QTableWidgetItem(Ins_name))
        self.ui.tableWidget_5.setItem(1, 0, QtWidgets.QTableWidgetItem(control_method))        
    
    def linspacer(self, Ins_name, table_type, Ins_method, target, speed):
        global type_list, result

        for t in type_list:
                if t in table_type:
                    Ins_type = t
        if Ins_type == 'Keithley2400':
            exec("init = self.%s.%s" %(Ins_name, Method_dict[Ins_type][Ins_method][2]))
            exec("step = %f / 3600 * %f" %(float(speed), time_unit))
            exec("if init > float(target):\n\tstep = -step")
            exec("result = np.arange(init, float(target), step)")
            exec("result = list(np.append(result, float(target)))")
        elif Ins_type == 'IPS120':
            exec("init = self.%s.%s" %(Ins_name, Method_dict[Ins_type][Ins_method][0]))
            exec("step = %f / 3600 * %f" %(float(0.2), time_unit))
            
            exec("print(init)")
            exec("print(step)")
            
            exec("if init > float(target):\n\tstep = -step")
            exec("result = np.arange(init, float(target), step)")
            exec("result = list(np.append(result, float(target)))")
        else:    
            exec("init = self.%s.%s" %(Ins_name, Method_dict[Ins_type][Ins_method]))
            exec("step = %f / 3600 * %f" %(float(speed), time_unit))
            exec("if init > float(target):\n\tstep = -step")
            exec("result = np.arange(init, float(target), step)")
            exec("result = list(np.append(result, float(target)))")
        return eval("result")
    
    def sequencer(self):
        global control_row_len, max_seq_num
        control_row_len = self.ui.tableWidget_3.rowCount()
        max_seq_num = control_row_len
        for i in range(control_row_len):
            exec("self.seq_%d = self.linspacer(self.ui.tableWidget_3.item(%d, 0).text(),\
                                        self.ui.tableWidget_3.item(%d, 1).text(),\
                                        self.ui.tableWidget_3.item(%d, 2).text(),\
                                        self.ui.tableWidget_3.item(%d, 3).text(),\
                                        self.ui.tableWidget_3.item(%d, 4).text())" %(i, i, i, i, i, i))
            print("self.p_2_info(len(self.seq_%d))" %(i))
            exec("self.p_2_info(len(self.seq_%d))" %(i))
             
    def showing_x_data(self, C_Ins_name, C_Ins_type, C_Ins_method, seq_num, step_num):
        
        if C_Ins_type == 'IPS120':
            temp = float(eval("self.%s.%s" %(C_Ins_name, Method_dict[C_Ins_type][C_Ins_method][1])))
        else:
            temp = eval("self.seq_%d[%d]" %(seq_num, step_num))
        exec("self.ui.tableWidget_5.setItem(2, 0, QtWidgets.QTableWidgetItem(str(%g)))" %(temp))
        
    def x_append_processor(self, C_Ins_name, C_Ins_type, C_Ins_method, seq_num, step_num):
        global x
        
        if C_Ins_type == 'IPS120':
            # X data append
            exec("x.append(self.%s.%s)" %(C_Ins_name, Method_dict[C_Ins_type][C_Ins_method][0]))
            # write x data
            exec("self.txt_write(%d, self.%s.%s)" %(-1, C_Ins_name, Method_dict[C_Ins_type][C_Ins_method][0]))
        else:
            # TODO: X should append the value from instrument instead of that from sequence list
            # X data append
            exec("x.append(self.seq_%d[%d])" %(seq_num, step_num))
            # write x data
            exec("self.txt_write(%d, self.seq_%d[%d])" %(-1, seq_num, step_num))
        
# =============================================================================
#  Instruement manipulation
# =============================================================================
    def control_ins(self, C_Ins_name, C_Ins_type, C_Ins_method, seq_num, step_num):
        
        if C_Ins_type == 'Keithley2400':
            exec("self.%s.%s = self.seq_%d[%d]" %(C_Ins_name, Method_dict[C_Ins_type][C_Ins_method][2], seq_num, step_num))
        elif C_Ins_type == 'IPS120':
            exec("self.%s.%s(self.seq_%d[-1])" %(C_Ins_name, Method_dict[C_Ins_type][C_Ins_method][1], seq_num))
        else:
            exec("self.%s.%s = self.seq_%d[%d]" %(C_Ins_name, Method_dict[C_Ins_type][C_Ins_method], seq_num, step_num))
# =============================================================================
#  Read setting
# =============================================================================
    def method_function_convertor(self):
        # this function mainly creat 2 varibles for the recording and display
        # 1. self.data_show_%d -- used for displaying the value
        # 2. self.data_%d -- append all data        
        # the detailed coding method are explained in the function "data_upadate"
        global method_row_len, type_list, x, s_time
        
        for i in range(method_row_len):
            x = []
            exec("self.data_%d = []" %(i))
            exec("self.data_show_%d = []" %(i))
    
    def showing_data(self, i):
        # assign the self.data_show_%d to the tablewidget_5 as the display method
        global method_row_len   
        
        temp = (eval("self.data_show_%d" % (i)))
        exec("self.ui.tableWidget_5.setItem(2, %d + 1, QtWidgets.QTableWidgetItem(str(%g)))" %(i, temp))
            

            
    def read_function_processor(self, i, Ins_name, Ins_type, Ins_method, Magnification): 
        '''Method_dict['SR830']['Voltage']  = sin_voltage'''
        if Ins_type == 'Keithley2400':
            # show
            exec("self.%s.sample_continuously()" %(Ins_name))
            exec("self.data_show_%d = float(self.%s.%s) * %f" %(i, Ins_name, Method_dict[Ins_type][Ins_method][1], Magnification))
            # XY data append
            exec("self.data_%d.append(float(self.%s.%s)* %f)" %(i, Ins_name, Method_dict[Ins_type][Ins_method][1], Magnification))
            # write data
            exec("self.txt_write(%d, self.data_show_%d)" %(i, i))  
        elif Ins_type == 'IPS120':
            # show
            exec("self.data_show_%d = float(self.%s.%s) * %f" %(i, Ins_name, Method_dict[Ins_type][Ins_method][0], Magnification))
            # XY data append
            exec("self.data_%d.append(float(self.%s.%s) * %f)" %(i, Ins_name, Method_dict[Ins_type][Ins_method][0], Magnification))
            # write data
            exec("self.txt_write(%d, self.data_show_%d)" %(i, i))
        else:
            # show
            exec("self.data_show_%d = float(self.%s.%s) * %f" %(i, Ins_name, Method_dict[Ins_type][Ins_method], Magnification))
            # XY data append
            exec("self.data_%d.append(float(self.%s.%s) * %f)" %(i, Ins_name, Method_dict[Ins_type][Ins_method], Magnification))
            # write data
            exec("self.txt_write(%d, self.data_show_%d)" %(i, i))
            
# =============================================================================
#  Update setting    
# =============================================================================
    def data_update(self):
        # this function mainly keep updating 2 variables:
        # 1. self.data_show_%d -- used for displaying the value
        # 2. self.data_%d -- append all data
        # to obtain the read value, the Ins_name, Ins_type, Ins_method are needed
        # by combining all the above parameters, we can find the correct function
        # corresponding to what we want to measure,
        # e.g.
        # self.data_show_%d = self.%s.%s" %(i, Ins_name, Method_dict[Ins_type][Ins_method])) 
        #
        # Ins_name = SR830_1
        # Ins_type = SR830
        # Ins_method = Voltage
        #
        # Method_dict[Ins_type][Ins_method] equals to sin_voltage
        #
        # we are actually running self.data.show_0 = self.SR830_1.sin_voltage,
        # which is the voltage value of the insturemnt SR830_1 
        global method_row_len, type_list, d_sec, x, s_time, step_num, max_seq_num, seq_num
        
        # control instrument
        C_Ins_name = self.ui.tableWidget_3.item(seq_num, 0).text()
        C_table_type = self.ui.tableWidget_3.item(seq_num, 1).text()
        for t in type_list:
                if t in C_table_type:
                    C_Ins_type = t
        C_Ins_method = self.ui.tableWidget_3.item(seq_num, 2).text()
        
        self.x_append_processor(C_Ins_name, C_Ins_type, C_Ins_method, seq_num, step_num)
        self.control_ins(C_Ins_name, C_Ins_type, C_Ins_method, seq_num, step_num)
        
        # read instruments and show the data
        for i in range(method_row_len):
            Ins_name = self.ui.tableWidget_4.item(i, 0).text()
            for t in type_list:
                if t in self.ui.tableWidget_4.item(i, 1).text():
                    Ins_type = t
            Ins_method = self.ui.tableWidget_4.item(i, 2).text()
            # add Magnification to the value
            Magnification = float("%e"%(float(self.ui.tableWidget_4.item(i, 3).text())))
            # read_function_processor
            self.read_function_processor(i, Ins_name, Ins_type, Ins_method, Magnification)
            # show x axis
            self.showing_x_data(C_Ins_name, C_Ins_type, C_Ins_method, seq_num, step_num)
            # show y axis
            self.showing_data(i)
            # TODO: assign the value to a temp variable to make the plot value and record value same

            
# =============================================================================
#         c_time = datetime.now()
#         d_time = c_time - s_time
#         d_sec = str(d_time.total_seconds())
#         x.append(float(d_sec))
# =============================================================================
        
        # Change to next sequence and stop if all sequeces is finished
        step_num = step_num + 1
        exec("x_length = len(self.seq_%d)" %(seq_num))
        if step_num == eval("x_length"):
            # empty the all append data
            for i in range(method_row_len):
                x = []
                exec("self.data_%d = []" %(i))
            seq_num = seq_num + 1
            if seq_num == max_seq_num:
                self.timeStop()
            else:
                self.title_update(seq_num)
        
# =============================================================================
#    Timer setting         
# =============================================================================
    def timeGo(self):
        # timeGo is the first activating function when "run" the project
        # At first, the name of the project will be test if it has existed.
        # if you ignore the warning and choose overwrite the file, the project
        # will start immediately. The txt file as well as the plot items will
        # be created.
        global name, full_name, s_time
        name = self.ui.lineEdit_2.text()
        if name == '':
            QMessageBox.information(self,"Wrong!.","Please type the file name.")
        else:
            full_name = name + '.txt'
            List = os.listdir()
            if full_name in List:
                reply = QMessageBox.information(self,"Wrong!.","The file has existed. Do you want to overwrite it?", QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
                if reply == QMessageBox.Close:
                    QMessageBox.information(self,"Wrong!.","Please adjust the file name.")
                elif reply == QMessageBox.Ok:
                    self.plot_creat()
                    self.txt_creat(full_name)
                    self.switch_to_plot_tab()
                    self.method_function_convertor()
                    self.timer.start(time_unit)
                    s_time = datetime.now()
                    
            else:
                self.plot_creat()
                self.txt_creat(full_name)
                self.switch_to_plot_tab()
                self.method_function_convertor()
                self.timer.start(time_unit)




        
    def timeStop(self):
        global x, seq_num, control_row_len
        # time stop
        self.timer.stop()
        seq_num = 0
        x = []
        for i in range(control_row_len):
            exec("self.seq_%d = []")




# =============================================================================
# Text write setting
# =============================================================================
    def txt_creat(self, full_name):
        # creat the txt file
        # the name of file and title are according to the user-defined file name
        # and the method (control/read) properties of the instrument
        global name, method_row_len
        method_row_len = self.ui.tableWidget_4.rowCount()
        f = open(full_name, 'w')
        
        title = 'X axis, '
        f.write(title)
        for i in range(method_row_len):
            Ins_name = self.ui.tableWidget_4.item(i, 0).text()
            Ins_method = self.ui.tableWidget_4.item(i, 2).text()
            Unit = self.ui.tableWidget_4.item(i, 4).text()
            temp_title = Ins_name + '-' + Ins_method + '(' + Unit + ')'
            # TODO: \n still has some issue when only one reading and only one running
            if i == method_row_len - 1:
                f.write(str(temp_title))
                f.write('\n')
            else:
                f.write(str(temp_title))
                f.write(', ')

        f.close()

    def txt_write(self, i, data):
        # TODO: separate the data of different sequece
        # write the value to the txt file which is created at beginning
        # the i value affects the writing mode to control it changes line
        global method_row_len, full_name
        f = open(full_name, 'a')
        if i == method_row_len - 1:
            f.write(str(data))
            f.write('\n')
        else:
            f.write(str(data))
            f.write(',')
        
# =============================================================================
# plot setting
# =============================================================================
    def plot_creat(self):
        # creat the plotDataItem as data_line_%d where %d = 0, 1, 2... (reference)
        # the x y value will be set later within the function plot_update()
        global method_row_len
        method_row_len = self.ui.tableWidget_4.rowCount()
        self.plt.clear()
        for i in range(method_row_len):
            exec("self.data_line_%d =  self.ui.graphWidget.plot([])" %(i))
        
    def plot_update(self):
        # The plot data is from the self.data_%d. Make sure the data is correct
        # before the assingment
        # setData to references (data_line_%d where %d = 0, 1, 2...) (reference)
        # click (1 or 0) is the switch to decide if the line will show
        # col is the column number where the mouse clicks
        global method_row_len, d_sec, x, click
        col = self.ui.tableWidget_5.currentColumn()
        for i in range(method_row_len):
            if click == 0 and i == col:
                exec("self.data_line_%d.setData([])" %(i))
            else:    
                exec("self.data_line_%d.setData(x, self.data_%d, pen = pg.mkPen(pg.intColor(%d)))" %(i, i, i + 1))
           
    def plot_click_option(self):
        # this function is connected to tableWidget_5 on page 3
        # the function activates whenever the tablewidge_5 is clicked
        # TODO: this function is not well working. it needs to establish multiple
        # switch to each channel
        global click
        if click == 1:
            click = 0
        elif click == 0:
            click = 1

    
# =============================================================================
# Page 2 subwindow Control option panel   
# =============================================================================
class control_panel(QtWidgets.QDialog):
     def __init__(self):
         super(control_panel, self).__init__()
         self.sub_ui = Ui_Dialog()
         self.sub_ui.setupUi(self)

class read_panel(QtWidgets.QDialog):
    def __init__(self):
         super(read_panel, self).__init__()
         self.sub_1_ui = read_Ui_Dialog()
         self.sub_1_ui.setupUi(self)
    
         

        

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow_p1()
    window.show()
    sys.exit(app.exec_())