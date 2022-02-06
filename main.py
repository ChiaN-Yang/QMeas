import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from ui.view import MainWindow
from utils import MeasurementQt, TxtFunction


class QMeasCtrl:
    """QMeas's Controller."""
    
    def __init__(self, model, view, database):
        """Controller initializer."""
        # measurement & database module
        self._measurement = model
        self._view = view
        self._database = database
        # Create a QThread object
        self.exp_thread = QThread()
        # Move worker to the thread
        self._measurement.moveToThread(self.exp_thread)
        self._database.moveToThread(self.exp_thread)
        # Connect signals and slots
        self._connectSignals()
        
    def _connectSignals(self):
        """Connect signals and slots."""
        self._view.ui.pushButton_5.clicked.connect(self.timeGo)
        self._view.ui.actionQuit.triggered.connect(self.timeStop)
        self._view.ui.actionQuit.triggered.connect(app.exit)
        self._view.ui.stopButton.clicked.connect(self.procedureStop)
        self._view.ui.loopButton.clicked.connect(self._measurement.quitLoopMeasure)
        self._view.ui.sweepButton.clicked.connect(self._measurement.quitSweepMeasure)
        self._view.ui.pauseButton.clicked.connect(self.resumePause)
        self._measurement.finished.connect(self.timeStop)
        self._measurement.signal_txt.connect(self._database.txtUpdate)
        self._measurement.signal_axis.connect(self._view.axisUpdate)
        self._measurement.signal_plot.connect(self._view.plotUpdate)
        self._measurement.signal_lines.connect(self._view.saveLines)
        self._measurement.signal_progress.connect(self._view.setProgressBar)
        self._measurement.clear_progress.connect(self._view.clearProgressBar)

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
        file_name = f'{self.name}.txt'
        if self._view.ui.label_18.text() == '':
            self._view.folder_address = os.path.abspath(os.getcwd()) + "\\data"
        if self.name == '':
            self._view.messageBox("Please type the file name.")
        elif file_name in os.listdir(self._view.folder_address):
            if self._view.fileExist():
                self.procedureGo()
        else:
            self.procedureGo()

    def procedureGo(self):
        """"measure start"""
        if self._view.tree_info == []:
            self._view.pageTwoInformation('Please set Control instruments')
            return
        # file name
        self.full_address = self._view.folder_address + '/' + self.name
        # save plot count
        self._view.save_plot_count = 0
        self._view.switchToPlotTab()
        # plotlines init
        self._view.createEmptyLines()
        # Create a worker object
        self._measurement.setInfo(self._view.instruments, self._view.instruments_read, self._view.options_read, self._view.instruments_magnification, self._view.tree_info)
        # porcedure start
        self.exp_thread.started.connect(self._measurement.startMeasure)
        # Start the thread
        self.exp_thread.start()
        # final resets
        self._view.ui.pushButton_5.setEnabled(False)
        self.exp_thread.finished.connect(lambda: self._view.ui.pushButton_5.setEnabled(True))

    def timeStop(self, file_count):
        """measure stop"""
        # time stop
        logging.info('measure stop')
        try:
            self.procedureStop()
            self.shutdownInstruments()
            self.measurement = None
            self._database.txtMerger(self.full_address, file_count, self.read_len+1)
            self._database.txtDeleter(file_count)
            self.exp_thread.quit()
            self.exp_thread.wait()
        except AttributeError:
            pass

    def procedureStop(self):
        self._measurement.stopMeasure()
        self._view.ui.pushButton_5.setEnabled(True)

    def shutdownInstruments(self):
        for i in self._measurement.instruments:
            i.performClose()


if __name__ == "__main__":
    # Create an instance of `QApplication`
    app = QApplication(sys.argv)
    # Show the calculator's GUI
    view = MainWindow()
    view.show()
    # Create instances of the model and the controller
    model = MeasurementQt()
    database = TxtFunction()
    controller = QMeasCtrl(model=model, view=view, database=database)
    # Execute calculator's main loop
    sys.exit(app.exec_())
