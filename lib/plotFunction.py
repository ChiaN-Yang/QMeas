# -*- coding: utf-8 -*-
"""
Created on Sat Aug 28 14:22:55 2021

@author: Triton_exp
"""


# function
def creatEmptyLines(self):
    """
    creat the plotDataItem as data_line_%d where %d = 0, 1, 2... (reference)
    the x y value will be set later within the function plot_update()
    """
    window.plt.clear()
    for i in range(len(self.instrunebt_read)):
        window.data_line.append(self.ui.graphWidget.plot([]))


def plotUpdate(self, n, x, y_n):
    # setData to the PlotItems
    if self.switch_list[n] == 1:
        window.data_line[n].setData(x, y_n, pen=pg.mkPen(pg.intColor(n+1)))
    else:
        window.data_line[n].setData([])


def axisUpdate(self, x_show, y_show):
    # update x title (instrument name and method)
    # insturement name
    self.ui.tableWidget_5.setItem(
        0, 0, QtWidgets.QTableWidgetItem(f'{x_show[1]}'))
    # method
    self.ui.tableWidget_5.setItem(
        0, 0, QtWidgets.QTableWidgetItem(f'{x_show[2]}'))

    # update x value
    self.ui.tableWidget_5.setItem(
        2, 0, QtWidgets.QTableWidgetItem(f'{x_show[0]:g}'))
    # update y value
    for i in range(y_show):
        self.ui.tableWidget_5.setItem(
            2, i + 1, QtWidgets.QTableWidgetItem(f'{y_show[i]:g}'))


def lineDisplaySwitchCreat(self):
    self.switch_list = []
    for _ in range(self.read_len):
        self.switch_list.append([1])


def lineDisplaySwitch(self):
    col = self.ui.tableWidget_5.currentColumn()
    self.switch_list[col] = self.switch_list[col]*(-1)


if __name__ == '__main__':
    # Assume the data from doMeasurement is like: data = [x0, y1, y2, y3, y4]
    x_show = 0
    y1 = 1
    y2 = 2
    y3 = 3
    y4 = 4
    y_show = [y1, y2, y3, y4]
    y = []
    for i in range(4):
        y.append([])
