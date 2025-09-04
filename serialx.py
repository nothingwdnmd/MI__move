# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QObject , pyqtSignal, QByteArray

import constantValues as cv
import debugPrinter as dp
from signal_generator_json import SignalGeneratorJsonx


class SerialX(QObject):
    """docstring for SerialX"""
    # evt_serial = pyqtSignal(str,int)
    evt_com_list = pyqtSignal(list)
    evt_serial_data = pyqtSignal(QByteArray)
    evt_serial_cmd = pyqtSignal(str)

    def __init__(self, arg):
        super().__init__()
        self.arg = arg
        # print("setup ")
        self.port = QSerialPort()
        
        self.timer = QtCore.QTimer()
        # self.timer.setInterval(50)
        self.timer.setInterval(10)
        # self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timer_handler)
        
        self.readyReadConnected = False
        self.ack_ok = bytes(cv.SERIAL_ACK_OK,"ascii")

        self.tmp_data=bytes()

        self.end_byte_defined = b'\n'

        self.use_simulator=0
        self.sj = None

        self.simulator_timer = QtCore.QTimer()
        # self.timer.setInterval(50)
        self.simulator_timer.setInterval(78)  # 1/128*10=78.125
        self.simulator_timer.timeout.connect(self.simulator_timer_handler)

    def __del__(self):
        try:
            if self.use_simulator:
                self.simulator_timer.stop()
                self.use_simulator=0
            else:
                if self.port.isOpen():
                    self.port.close()
                    self.timer.stop()

            print("serial closed in exit")
        except:
            pass  # XXX errors on shutdown
            

    def simulator_timer_handler(self):
        if self.sj is not None:
            s = self.sj.get_json_array()
            self.evt_serial_data.emit(bytes(s,'utf-8'))

    # serialx.py 中的定时器处理串口数据
    def timer_handler(self):
        data = self.port.readLine()
        if data.size()>0:
            end_byte_read = data[data.size()-1]
            
            if self.end_byte_defined == end_byte_read:
                self.evt_serial_data.emit(self.tmp_data+data)
                self.tmp_data = bytes()
            else:
                self.tmp_data = self.tmp_data+data

    def find_serial_ports(self):
        self.port_list = QSerialPortInfo.availablePorts()           
        if len(self.port_list)>0:
            self.evt_com_list.emit(self.port_list)
        else:
            print("no serial port was found")
            
    def open_serial(self,s):
        if s==cv.SERIAL_SIMULATOR:
            self.use_simulator=1
            self.evt_serial_cmd.emit(cv.EVT_SERIAL_OPEN_SUC)
            self.simulator_timer.start()
            self.sj = SignalGeneratorJsonx()
            dp.dpt('use SignalGenerator')
            return 1
        # 配置串口参数
        self.port.setPortName(s);
        self.port.setBaudRate(921600);
        self.port.setDataBits(QSerialPort.Data8);
        self.port.setStopBits(QSerialPort.OneStop);
        self.port.setParity(QSerialPort.NoParity);

        # 打开串口
        r = self.port.open(QtCore.QIODevice.ReadWrite);
        if r:
            # print("open ok")
            # self.evt_serial.emit(cv.EVT_SERIAL_OPEN_SUC, 0)
            self.evt_serial_cmd.emit(cv.EVT_SERIAL_OPEN_SUC)
            self.timer.start()

            # if not self.readyReadConnected:
            #     self.port.readyRead.connect(self.read_port)
            #     self.readyReadConnected=True
            #     dp.dpt('port.readyRead.connect')
        else:
            self.evt_serial_cmd.emit(cv.EVT_SERIAL_OPEN_FAILED)
            # print("open failed")
        
        return r

    # def read_port(self):
    #     self.timer.start()

    def write_port(self,s):
        if self.use_simulator:
            return
        if self.port.isOpen():
            self.port.write(bytes(s,"ascii"))              

    def write_port_ack_ok(self):
        # dp.dpt('-')
        if self.use_simulator:
            return
        if self.port.isOpen():
            self.port.write(self.ack_ok)     
            
    def close_serial(self):
        if self.use_simulator:
            self.use_simulator=0
            self.simulator_timer.stop()
            self.evt_serial_cmd.emit(cv.EVT_SERIAL_CLOSE_SUC)
            return
        if self.port.isOpen():
            self.port.close()
            self.timer.stop()
            self.evt_serial_cmd.emit(cv.EVT_SERIAL_CLOSE_SUC)
            # print("serial closed")

            
    def handle_serial_error(self, error=None):
        """Serial port error"""
        # terminate connection
        print(error)


