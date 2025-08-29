# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject,QRunnable,pyqtSignal,pyqtSlot
# from PyQt5.QtCore import QThread
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Worker(QRunnable):
# class Worker(QThread):

    def __init__(self, fn, args):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.fn(self.args)
        self.signals.finished.emit()

