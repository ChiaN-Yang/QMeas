import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from ui.view import MainWindow
from utils import MeasurementQt, TxtFunction
from shutil import copyfile


class QMeasCtrl:
    """QMeas's Controller."""
    
    def __init__(self, view, database):
        """Controller initializer."""
        # measurement & database module
        self._measurement = MeasurementQt()
        self._view = view
        self._database = database
        # Create a QThread object
        self.exp_thread = QThread()
        # Move worker to the thread
        self._database.moveToThread(self.exp_thread)
        # Connect signals and slots
        self._connectViewSignals()
        
    def _connectViewSignals(self):
        """Connect signals and slots."""
        self._view.ui.pushButton_5.clicked.connect(self.timeGo)
        self._view.ui.actionQuit.triggered.connect(lambda: self._measurement.stopMeasure())
        self._view.ui.actionQuit.triggered.connect(app.exit)
        self._view.ui.stopButton.clicked.connect(self.procedureStop)
        self._view.ui.pushButton_6.clicked.connect(self.procedureStop)
        self._view.ui.loopButton.clicked.connect(lambda: self._measurement.quitLoopMeasure())
        self._view.ui.sweepButton.clicked.connect(lambda: self._measurement.quitSweepMeasure())
        self._view.ui.pauseButton.clicked.connect(self.resumePause)

    def _connectMeasureSignals(self):
        self._measurement.finished.connect(self.timeStop)
        self._measurement.signal_txt.connect(self._database.txtUpdate)
        self._measurement.signal_axis.connect(self._view.axisUpdate)
        self._measurement.signal_plot.connect(self._view.plotUpdate)
        self._measurement.signal_lines.connect(self._view.saveLines)
        self._measurement.signal_progress.connect(self._view.setProgressBar)
        self._measurement.clear_progress.connect(self._view.clearProgressBar)
        self._measurement.page_information.connect(self._view.pageTwoInformation)

    def resumePause(self):
        self._view.resumePause()
        self._measurement.resumePauseMeasure()

    def timeGo(self):
        """ TimeGo is the first activating function when "run" the project
            At first, the name of the project will be test if it has existed.
            if you ignore the warning and choose overwrite the file, the project
            will start immediately. The txt file as well as the plot items will
            be created.
        """
        self.name = self._view.ui.lineEdit_2.text()
        file_name = f'{self.name}.csv'
        if self._view.ui.label_18.text() == '':
            self._view.folder_address = os.path.abspath(os.getcwd()) + "\\data"
            self._view.ui.label_18.setText(self._view.folder_address)
        if self.name == '':
            self._view.messageBox("Please type the file name.")
        elif self._view.tree_info == []:
            self._view.pageTwoInformation('Please set Control instruments')
        elif file_name in os.listdir(self._view.folder_address):
            if self._view.fileExist():
                self.procedureGo()
        else:
            self.procedureGo()

    def procedureGo(self):
        """"measure start"""
        # Record experimental steps
        self._database.recordSteps(self._view.getTableValues())
        self._database.txtDeleter()
        copyfile('./ui/asset/step.txt', f'{self._view.folder_address}/{self.name}_measurement_process.txt')
        self._view.procedureGo(self.name)
        self._database.setUnits(self._view.units)
        # Create a worker object
        self._measurement = None
        self._measurement = MeasurementQt()
        self._measurement.setInfo(self._view.instruments, self._view.instruments_read, self._view.options_read, self._view.instruments_magnification, self._view.tree_info)
        # Move worker to the thread
        self._measurement.moveToThread(self.exp_thread)
        # porcedure start
        self.exp_thread.started.connect(self._measurement.startMeasure)
        self._connectMeasureSignals()
        # Start the thread
        self.exp_thread.start()
        # final resets
        self.exp_thread.finished.connect(lambda: self._view.ui.pushButton_5.setEnabled(True))

    def timeStop(self, file_count):
        """measure stop"""
        # time stop
        logging.info('measure stop')
        self._measurement.stopMeasure()
        self.shutdownInstruments()
        # Save current view here (auto plot save)
        self._view.plotSave()
        # Merge data
        if self._view.folder_address:
            self._database.txtMerger(f'{self._view.folder_address}/{self.name}', file_count, self._view.read_len+1)
        self.exp_thread.quit()
        self.exp_thread.wait()

    def procedureStop(self):
        self._view.ui.stopButton.setEnabled(False)
        self._view.ui.pushButton_6.setEnabled(False)
        if self._view.stopMeasure():
            self._measurement.stopMeasure()
            self._view.ui.pushButton_5.setEnabled(True)
        else:
            self._view.ui.stopButton.setEnabled(True)
            self._view.ui.pushButton_6.setEnabled(True)

    def shutdownInstruments(self):
        for i in self._measurement.instruments:
            i.performClose()


if __name__ == "__main__":
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    # Show the GUI
    view = MainWindow()
    view.show()
    # Create instances of the model and the controller
    database = TxtFunction()
    controller = QMeasCtrl(view=view, database=database)
    # Execute main loop
    sys.exit(app.exec_())
