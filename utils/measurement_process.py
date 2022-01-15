from PyQt5.QtCore import QThread, pyqtSignal, QObject
import logging
from modpack import TimeMeasurement
from time import sleep


class MeasurementProcess(QObject):
    """this class is used to perform experiments"""
    finished = pyqtSignal(int)
    signal_txt = pyqtSignal(int, list, list, list, list)
    signal_plot = pyqtSignal(int, list, list)
    signal_axis = pyqtSignal(list, list)
    signal_lines = pyqtSignal(int, list, list)
    signal_progress = pyqtSignal()
    clear_progress = pyqtSignal(int)

    def __init__(self, instruments, instruments_read, options_read, instruments_magnification):
        super().__init__()
        self.instruments = instruments
        self.instruments_read = instruments_read
        self.options_read = options_read
        self.magnification = instruments_magnification
        self.control_sequence = []
        # control variable
        self.stop_running = False
        self.quit_running = False
        self.quit_sweep = False
        self.quit_loop = False

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

        # open instrument
        self.openInstruments()

        for level in self.control_sequence:
            if self.quit_running:
                return

            if level[0] and level[1] and level[2]:
                self.threeLevelsTree(level)

            elif level[0] and level[1] and not level[2]:
                self.twoLevelsTree(level)

            elif level[0] and not level[1] and not level[2]:
                self.oneLevelTree(level)

        self.finished.emit(self.file_count)

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
