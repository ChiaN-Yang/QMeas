import logging
from numpy import nan
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from modpack import TimeMeasurement
from time import sleep, time


class MeasurementQt(QObject):
    """this class is used to perform experiments"""
    finished = pyqtSignal(int)
    signal_txt = pyqtSignal(int, list, list, list, list)
    signal_plot = pyqtSignal(int, float, float, int)
    signal_axis = pyqtSignal(list, list)
    signal_lines = pyqtSignal(int)
    signal_progress = pyqtSignal()
    clear_progress = pyqtSignal(int)
    page_information = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.instruments = []
        self.instruments_read = []
        self.options_read = []
        self.magnification = []
        self.control_sequence = []
        # control variable
        self.stop_running = False
        self.quit_running = False
        self.quit_sweep = False
        self.quit_loop = False

    def setInfo(self, instruments, instruments_read, options_read, instruments_magnification, tree_info):
        self.instruments = instruments.copy()
        self.instruments_read = instruments_read.copy()
        self.options_read = options_read.copy()
        self.magnification = instruments_magnification.copy()
        self.schedule(tree_info)
        # control variable
        self.stop_running = False
        self.quit_running = False
        self.quit_sweep = False
        self.quit_loop = False
        print(f'Ins Read:\n{self.instruments_read}')

    def openInstruments(self):
        """open instruments"""
        for instrument in self.instruments:
            instrument.performOpen()

    def schedule(self, tree_info):
        """ return [tree1, tree2, tree3]
            tree view
            [ [child_num, leve_position, instrument, option, check, target, speed, increment]
              [child_num, leve_position, instrument, option, check, target, speed, increment]
              [child_num, leve_position, instrument, option, check, target, speed, increment] ]
        """
        tree_num = tree_info[0]
        child_num = tree_info[2]
        leve_position = tree_info[1]
        check = tree_info[3]
        method = tree_info[4]
        ins_label = tree_info[5]
        target = tree_info[6]
        speed = tree_info[7]
        increment = tree_info[8]
        print(f'\nControl INFO\ntree_num: {tree_num}\nchild_num: {child_num}\nleve_position: {leve_position}')

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
            level[level_count].append([info_tree[n][2], info_tree[n][3], info_tree[n][4], info_tree[n][5], info_tree[n][6], info_tree[n][7]])
            level_count += 1

            if info[0] != 0:
                for i in range(info[0]):
                    if info_tree[n+1+i][0] == -1:
                        level[level_count].append([info_tree[n+1+i][2], info_tree[n+1+i][3], info_tree[n+1+i][4], info_tree[n+1+i][5], info_tree[n+1+i][6], info_tree[n+1+i][7]])

        self.control_sequence.append(level)

    def startMeasure(self):
        self.file_count = 0
        self.line_count = 0

        # open instrument
        self.openInstruments()
        self.name_txt = ['control_name']
        self.method_txt = ['control_method']
        for n, instrument_read in enumerate(self.instruments_read):
            self.name_txt.append(instrument_read.instrumentName())
            self.method_txt.append(self.options_read[n])

        try:
            for level in self.control_sequence:
                if self.quit_running:
                    break

                if level[0] and level[1] and level[2]:
                    self.page_information.emit(f'Run three levels measurement:')
                    for ins in level[0]:
                        self.page_information.emit(f'- {ins[0]}  {ins[3]}  {ins[4]}')
                    for ins in level[1]:
                        self.page_information.emit(f'-- {ins[0]}  {ins[3]}  {ins[4]}')
                    for ins in level[2]:
                        self.page_information.emit(f'--- {ins[0]}  {ins[3]}  {ins[4]}')
                    self.threeLevelsTree(level)

                elif level[0] and level[1] and not level[2]:
                    self.page_information.emit(f'Run two levels measurement:')
                    for ins in level[0]:
                        self.page_information.emit(f'- {ins[0]}  {ins[3]}  {ins[4]}')
                    for ins in level[1]:
                        self.page_information.emit(f'-- {ins[0]}  {ins[3]}  {ins[4]}')
                    self.twoLevelsTree(level)

                elif level[0] and not level[1] and not level[2]:
                    self.page_information.emit(f'Run one level measurement:')
                    for ins in level[0]:
                        self.page_information.emit(f'- {ins[0]}  {ins[3]}  {ins[4]}')
                    self.oneLevelTree(level)
        except:
            logging.exception('measure error')

        self.finished.emit(self.file_count)

    def threeLevelsTree(self, level):
        for i in level[0]:  # i = [instrument,method,check,target,speed,increment]
            linspacer = i[0].experimentLinspacer(i[1], i[3], i[4], i[5])
            self.clear_progress.emit(len(linspacer))
            for value_i in linspacer:
                if self.performRecord(i, value_i):
                    break
                self.signal_progress.emit()

                for j in level[1]:
                    for value_j in j[0].experimentLinspacer(j[1], j[3], j[4], j[5]):
                        if self.performRecord(j, value_j):
                            break

                        for k in level[1]:
                            for value_k in k[0].experimentLinspacer(k[1], k[3], k[4], k[5]):
                                if self.performRecord(k, value_k, True):
                                    break
                                if self.quit_sweep:
                                    self.quit_sweep = False
                                    break
                                if self.quit_loop:
                                    self.quit_loop = False
                                    return

                            self.signal_lines.emit(self.line_count)
                            sleep(0.1)
                            self.line_count += 1
                            if int(k[2]):
                                self.file_count += 1

    def twoLevelsTree(self, level):
        for i in level[0]:
            linspacer = i[0].experimentLinspacer(i[1], i[3], i[4], i[5])
            self.clear_progress.emit(len(linspacer))
            for value_i in linspacer:
                if self.performRecord(i, value_i):
                    break
                self.signal_progress.emit()

                for j in level[1]:
                    for value_j in j[0].experimentLinspacer(j[1], j[3], j[4], j[5]):
                        if self.performRecord(j, value_j, True):
                            break
                        if self.quit_sweep:
                            self.quit_sweep = False
                            break
                        if self.quit_loop:
                            self.quit_loop = False
                            return

                    self.signal_lines.emit(self.line_count)
                    sleep(0.1)
                    self.line_count += 1
                    if int(j[2]):
                        self.file_count += 1

    def oneLevelTree(self, level):
        for i in level[0]:
            linspacer = i[0].experimentLinspacer(i[1], i[3], i[4], i[5])
            self.clear_progress.emit(len(linspacer))
            for value_i in linspacer:
                if self.performRecord(i, value_i, True):
                    break
                self.signal_progress.emit()
                if self.quit_sweep:
                    self.quit_sweep = False
                    break
                if self.quit_loop:
                    self.quit_loop = False
                    return

            self.signal_lines.emit(self.line_count)
            sleep(0.1)
            self.line_count += 1
            if int(i[2]):
                self.file_count += 1

    def performRecord(self, instrument_info, value, bottom_level=False):
        while self.stop_running:
            QThread.sleep(1)

        # instrument_info = instrument method check target speed increment
        if instrument_info[5] != '0' and instrument_info[5] != '-':
            for value_increment in instrument_info[0].experimentLinspacer(instrument_info[1], value, instrument_info[4], '0'):
                try:
                    incre_value = instrument_info[0].performSetValue(instrument_info[1], value_increment)
                except:
                    logging.exception('increment error')
                    incre_value = nan
                if incre_value == 'done':
                    break
                sleep(0.1)
        try:
            set_value = instrument_info[0].performSetValue(instrument_info[1], value)
        except:
            logging.exception('set_value error')
            set_value = nan
        if set_value == 'done':
            return 1

        start_time = time()
        x_show = [set_value, instrument_info[0].instrumentName(), instrument_info[1]]
        y_show = []

        self.name_txt[0] = instrument_info[0].instrumentName()
        self.method_txt[0] = instrument_info[1]

        for n, instrument_read in enumerate(self.instruments_read):
            try:
                read_value = instrument_read.performGetValue(self.options_read[n], self.magnification[n])
            except:
                logging.exception('read_value error') # exc_info=False
                read_value = nan
            y_show.append(read_value)
            if bottom_level:
                self.signal_plot.emit(n, set_value, read_value, self.line_count)

        self.signal_axis.emit(x_show, y_show)
        if int(instrument_info[2]):
            self.signal_txt.emit(self.file_count, self.method_txt, self.name_txt, x_show, y_show)
        
        elapsed_time = round(time() - start_time, 2)
        if elapsed_time < 0.1:
            sleep(0.1-elapsed_time)
        return 0

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
