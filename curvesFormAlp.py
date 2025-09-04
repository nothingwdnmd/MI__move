# -*- coding: utf-8 -*-

from PyQt5 import uic
from PyQt5 import QtWidgets
import numpy as np
import json
from PyQt5.QtCore import QSettings, QPoint, QSize
from PyQt5.QtWidgets import QApplication

import pyqtgraph as pg

qt_creator_file = "curveformAlp.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)
import debugPrinter as dp

class CurvesFormAlp(QtWidgets.QWidget, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Alpha Amp")

        self.pw = pg.plot(title="sig")
        self.plt = self.pw.getPlotItem()
        self.gridLayout.addWidget(self.pw)
        self.pw.setLabel('bottom', 'Time', 's')
        # self.pw.setXRange(-10, 0)
        self.curves=[]
        for i in range(4):
            c = self.pw.plot()
            self.curves.append(c) 

        self.curve_data_max_len = 100

        self.data = np.empty(shape=(0,4))

        self.settings = QSettings('./curveFormAlpSetting.ini', QSettings.IniFormat)     
        # self.settings = QSettings( 'My Company', 'CurvesForm')     
        # Initial window size/pos last saved. Use default values for first time
        self.resize(self.settings.value("size", QSize(270, 225)))

        # self.desktop = QApplication.desktop()

        if (self.settings.value("pos") is not None) and (self.settings.value("size") is not None):
            screenRect = QApplication.desktop().screenGeometry()
            self.height = screenRect.height()
            if self.settings.value("pos").x()<(screenRect.width()-100) and \
                self.settings.value("pos").y()<(screenRect.height()-100):
                self.move(self.settings.value("pos", QPoint(50, 50)))            

        # self.t = np.empty((1))
        # self.t[0] = 1
        self.t=0
        self.scale_offset = 10000

        self.showing_state = False


    def __del__(self):
        dp.dpt('del curvesform')

    def closeEvent(self, e):
        # Write window size and position to config file
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        e.accept()

    def close_win(self):
        dp.dpt('Alpcurveform close')
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.close()



    def new_data(self,d):
        # print(x)
        # print(type(x))
        # print(x.shape)

        d = np.expand_dims(d, axis=1).T
        # d = np.hstack((t,x))

        self.data = np.concatenate((self.data,d), axis=0)
        num_del = self.data.shape[0] - self.curve_data_max_len

        if(num_del>0):
            self.data = np.delete(self.data,np.s_[:num_del], axis=0)

        data_len = self.data.shape[0]

        x = np.linspace(start=self.t-data_len+1, stop=self.t,num=data_len)

        for i in range(self.data.shape[1]):
            self.curves[i].setData(x=x,y=self.data[:, i]+self.scale_offset*i)


