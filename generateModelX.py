from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QStringListModel
import shutil
import os
from PyQt5.QtWidgets import QInputDialog, QLineEdit
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QThreadPool
from worker import Worker
from datetime import datetime
import train_model
import train_model_curctrl

import debugPrinter as dp


from PyQt5.QtWidgets import QLabel,QDialog,QVBoxLayout,QHBoxLayout
 
class ProgressBarX(QDialog):
    def __init__(self,parent = None):
        super(ProgressBarX, self).__init__(parent)
        self.resize(280,50)
        self.setWindowTitle(self.tr("calculating..."))

        self.FeatProgressBar = QProgressBar(self)
        self.FeatProgressBar.setMinimum(0)
        self.FeatProgressBar.setMaximum(0) 
 
        self.TipLabel = QLabel("Please wait...This may take 1 minute")

        TipLayout = QHBoxLayout()
        TipLayout.addWidget(self.TipLabel)

        FeatLayout = QHBoxLayout()
        FeatLayout.addWidget(self.FeatProgressBar)

        layout = QVBoxLayout()
        layout.addLayout(FeatLayout)
        layout.addLayout(TipLayout)
        self.setLayout(layout)

    def show_bar(self):
        self.show()

    def close_bar(self):
        self.close() 



qt_creator_file = "trainingDataSelector.ui"

win, QtBaseClass = uic.loadUiType(qt_creator_file)


class GenerateModelX(QtWidgets.QWidget, win):

    def __init__(self,task_name):
    # task_name: str: 'cc', 'mi'
        QtWidgets.QWidget.__init__(self)
        win.__init__(self)
        self.task_name = task_name 
        self.setupUi(self)
        self.setWindowTitle("Select Training Data")
        self.modelFolder = './models/'
        self.name_extension = '.mim'
        self.new_model_default_name = 'new_model_bv8#p!_'+self.name_extension

        if self.task_name=='cc':
            label_to_show = 'Cursor Control Task Model'
            self.trianingDataFolder = './training_data_curctrl/'
        elif self.task_name=='mi':
            label_to_show = 'Motor Imagine Task Model'
            self.trianingDataFolder = './training_data/'

        self.label_show_task_name.setText(label_to_show)
        self.listModel = QStringListModel()
        self.list=[]

        for file_name in os.listdir(self.trianingDataFolder):
            self.list.append(file_name)

        self.listModel.setStringList(self.list)

        self.listView_files.setModel(self.listModel)

        self.btn_add_file.clicked.connect(self.btn_add_file_click)
        self.btn_clear.clicked.connect(self.btn_clear_click)
        self.btn_generate_model.clicked.connect(self.btn_generateModel)

        self.threadpool = QThreadPool()

        self.pgb = ProgressBarX()

        self.model_name=[]

    def thread_on_exit(self):
        self.pgb.close_bar()
        origin_filePathName = self.modelFolder + self.new_model_default_name
        
        if not os.path.isfile(origin_filePathName):
            dp.dpt('there is no model generated successfully maybe, check it ...')
            
        mtime = os.path.getmtime(origin_filePathName)
        t = datetime.now() - datetime.fromtimestamp(mtime) 
        t_diff = t.total_seconds()
        
        if t_diff<10:# this model should be just generated
            if len(self.model_name)>0:
                new_filePathName = self.modelFolder+self.model_name+self.name_extension                               
                shutil.copyfile(origin_filePathName, new_filePathName)

    def calculate_model(self,s):
        if self.task_name=='cc':
            dp.dpt('cc')
            train_model_curctrl.calculate_model()
        elif self.task_name=='mi':
            dp.dpt('mi')
            train_model.calculate_model()

    def btn_generateModel(self):
        hint = 'model_1'
        text, ok = QInputDialog().getText(self, "Model Name For Saving",
                         "(Name your model with these data):", QLineEdit.Normal,hint)
        if ok and text:
            self.model_name = text
            worker = Worker(self.calculate_model,'dummy')
            worker.signals.finished.connect(self.thread_on_exit)

            worker.autoDelete()
            self.threadpool.start(worker)

            self.pgb.show_bar()


    def btn_add_file_click(self):
        filePathNames,_ = QFileDialog.getOpenFileNames(self, "Select Training Data", "./data",("edf files(*edf)"))
        for fpn in filePathNames:
            f = fpn.split('/')[-1]
            des = self.trianingDataFolder+f
            shutil.copyfile(fpn, des)

            self.list.append(f)

        self.listModel.setStringList(self.list)


    def btn_clear_click(self):
        print('btn_clear_click')
        self.list.clear()
        self.listModel.setStringList(self.list)

        for file_name in os.listdir(self.trianingDataFolder):
            file = self.trianingDataFolder + file_name
            if os.path.isfile(file):
                print('Deleting file:', file)
                os.remove(file)

