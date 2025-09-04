# -*- coding: utf-8 -*-

from PyQt5 import uic
from PyQt5 import QtWidgets
import numpy as np
import json
from PyQt5.QtCore import QSettings, QPoint, QSize
from PyQt5.QtWidgets import QApplication

import pyqtgraph as pg

qt_creator_file = "curvesform.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)
import debugPrinter as dp

class CurvesForm(QtWidgets.QWidget, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Signals")

        self.pw = pg.plot(title="sig")
        self.plt = self.pw.getPlotItem()

        self.curves_num_constant = 12
        curves_eeg_num = 8
        curves_acc_num = 4

        self.checkboxes = [None]*self.curves_num_constant
        self.checkboxes[0]=self.checkBox
        self.checkboxes[1]=self.checkBox_2
        self.checkboxes[2]=self.checkBox_3
        self.checkboxes[3]=self.checkBox_4
        self.checkboxes[4]=self.checkBox_5
        self.checkboxes[5]=self.checkBox_6
        self.checkboxes[6]=self.checkBox_7
        self.checkboxes[7]=self.checkBox_8
        self.checkboxes[8]=self.checkBox_9
        self.checkboxes[9]=self.checkBox_10
        self.checkboxes[10]=self.checkBox_11
        self.checkboxes[11]=self.checkBox_12

        self.scale_offset = 100

        self.gridLayout.addWidget(self.pw)
        self.pw.setLabel('bottom', 'Time', 's')
        # self.pw.setXRange(-10, 0)

        self.curve_data_max_len = 1000
        self.curve_data_max_len_acc = 100 # self.curve_data_max_len/10  you want to make it interger, not float

        self.curves=[]
        self.curves_acc=[]

        for i in range(self.curves_num_constant):
            c = self.pw.plot()
            self.curves.append(c) 

        self.data = np.empty(shape=(0,curves_eeg_num+1))
        self.data_acc = np.empty(shape=(0,curves_acc_num+1))

        with open('user_config_curve_form.json', 'r') as file:
            self.usr_config_json = json.load(file)

        # print(self.usr_config_json)
        # self.show_ch = np.ones(shape=8)

        # self.show_ch = np.fromstring(self.usr_config_json[cv.JSON_CH_SHOW_KEY_STR])
        self.show_ch = np.array(self.usr_config_json['CH'])

        curves_num = len(self.curves)+len(self.curves_acc) 

        if self.show_ch.size==self.curves_num_constant:
            for i, ch in enumerate(self.show_ch):
                if i<curves_num:
                    if ch==1:
                        self.checkboxes[i].setChecked(True)
                        self.curves[i].show()
                    else:
                        self.checkboxes[i].setChecked(False)
                        self.curves[i].hide()

        for i in range(self.curves_num_constant):
             self.checkboxes[i].stateChanged.connect(self.cb_handler)

        self.settings = QSettings('./curveFormSetting.ini', QSettings.IniFormat)     
        # Initial window size/pos last saved. Use default values for first time
        self.resize(self.settings.value("size", QSize(270, 225)))
        if (self.settings.value("pos") is not None) and (self.settings.value("size") is not None):
            screenRect = QApplication.desktop().screenGeometry()
            self.height = screenRect.height()
            if self.settings.value("pos").x()<(screenRect.width()-100) and \
                self.settings.value("pos").y()<(screenRect.height()-100):
                self.move(self.settings.value("pos", QPoint(50, 50)))            

    def __del__(self):
        dp.dpt('del curvesform')

    def closeEvent(self, e):
        # Write window size and position to config file
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        e.accept()
        
    def close_win(self):
        dp.dpt('curveform close')
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.close()


    def cb_handler(self):
        for i in range(self.curves_num_constant):
            if (self.checkboxes[i].isChecked()):
                self.curves[i].show()
                self.show_ch[i]=1
            else:
                self.show_ch[i]=0
                self.curves[i].hide()

        self.usr_config_json['CH']=list(self.show_ch)

        with open('user_config_curve_form.json', "w") as outfile:
            json.dump(self.usr_config_json, outfile)    

    def deal_with_data_inlet(self,elapsed_time,y):
        if y.shape[1]==1: 
            y = np.hstack((y,np.zeros(shape=(y.shape[0],7))))
        # if use 1 ch, pad the data in other channels with zeros

        t = np.expand_dims(elapsed_time, axis=1)

        d = np.hstack((t,y))

        self.data = np.concatenate((self.data,d), axis=0)

        num_del = self.data.shape[0] - self.curve_data_max_len

        if(num_del>0):
            self.data = np.delete(self.data,np.s_[:num_del], axis=0)

        # dp.dpt(self.data[0, 1])
        # dp.dpt(self.data[0, 2])

        for i in range(self.data.shape[1]-1):
            if self.show_ch[i]:
                # self.curves[i].setData(x=self.data[:,0], y=self.data[:, i+1]+self.scale_offset*i)
                # self.curves[i].setData(y=self.data[:, i+1]+self.scale_offset*i)
                voltage_value = (self.data[:, i+1]-32768)*0.2
                self.curves[i].setData(x=self.data[:,0],y=voltage_value+self.scale_offset*i)

    def deal_with_data_acc_inlet(self,elapsed_time,y):

        t = np.expand_dims(elapsed_time, axis=1)

        d = np.hstack((t,y))


        self.data_acc = np.concatenate((self.data_acc,d), axis=0)

        num_del = self.data_acc.shape[0] - self.curve_data_max_len_acc

        if(num_del>0):
            self.data_acc = np.delete(self.data_acc,np.s_[:num_del], axis=0)

        for i in range(self.data_acc.shape[1]-1):
            index_for_acc_curves = i+8 # first 8 curves is eeg channels
            if self.show_ch[index_for_acc_curves]:
                # self.curves[i].setData(x=self.data[:,0], y=self.data[:, i+1]+self.scale_offset*i)
                # self.curves[index_for_acc_curves].setData(y=self.data_acc[:, i+1]+self.scale_offset*i)
                # self.curves[index_for_acc_curves].setData(x=self.data_acc[:,0],y=self.data_acc[:, i+1]+self.scale_offset*i)
                self.curves[index_for_acc_curves].setData(x=self.data_acc[:,0],y=self.data_acc[:, i+1])


