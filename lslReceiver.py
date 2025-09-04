# -*- coding: utf-8 -*-

import numpy as np
import pylsl
# import pyqtgraph as pg

from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import QObject , pyqtSignal



class Inlet:
    """Base class to represent a plottable inlet"""
    def __init__(self, info: pylsl.StreamInfo):
        # create an inlet and connect it to the outlet we found earlier.
        # max_buflen is set so data older the plot_duration is discarded
        # automatically and we only pull data new enough to show it

        # Also, perform online clock synchronization so all streams are in the
        # same time domain as the local lsl_clock()
        # (see https://labstreaminglayer.readthedocs.io/projects/liblsl/ref/enums.html#_CPPv414proc_clocksync)
        # and dejitter timestamps
        self.inlet = pylsl.StreamInlet(info, processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter)
        # store the name and channel count
        self.name = info.name()
        self.channel_count = info.channel_count()
        self.srate = info.nominal_srate()



class DataInlet(Inlet):
    """A DataInlet represents an inlet with continuous, multi-channel data that
    should be plotted as multiple lines."""
    dtypes = [[], np.float32, np.float64, None, np.int32, np.int16, np.int8, np.int64]

    def __init__(self, info: pylsl.StreamInfo,s):
        super().__init__(info)

        self.inlet_type = s
                # calculate the size for our buffer, i.e. two times the displayed data

        # bufsize = (2 * math.ceil(info.nominal_srate() * plot_duration), info.channel_count())
        bufsize = (8192, info.channel_count())

        self.buffer = np.empty(bufsize, dtype=self.dtypes[info.channel_format()])

        # print(bufsize)

        # print('--------*************---------------')
        # print(self.channel_count)
        # print(self.name)
        # print(self.srate)

        
    def pull_data(self):
        _, ts = self.inlet.pull_chunk(timeout=0.0,
                              max_samples=self.buffer.shape[0],
                              dest_obj=self.buffer)
        y = np.empty(shape=(0,0))
        if not ts:
            return ts,y

        ts = np.asarray(ts)
        y = self.buffer[0:ts.size, :]
        return ts,y


class MarkerInlet(Inlet):
    """A MarkerInlet shows events that happen sporadically as vertical lines"""

    dtypes = [[], np.float32, np.float64, None, np.int32, np.int16, np.int8, np.int64]

    def __init__(self, info: pylsl.StreamInfo,s):
        super().__init__(info)
        self.inlet_type = s

        bufsize = (512, info.channel_count())

        self.buffer = np.empty(bufsize, dtype=self.dtypes[info.channel_format()])

        # print(bufsize)

    # def pull_and_plot(self, plot_time, plt):
    #     # TODO: purge old markers
    #     strings, timestamps = self.inlet.pull_chunk(0)
    #     if timestamps:
    #         for string, ts in zip(strings, timestamps):
    #             plt.addItem(pg.InfiniteLine(ts, angle=90, movable=False, label=string[0]))

    def pull_data(self):
        _, ts = self.inlet.pull_chunk(timeout=0.0,
                              max_samples=self.buffer.shape[0],
                              dest_obj=self.buffer)
        y = np.empty(shape=(0,0))
        if not ts:
            return ts,y

        ts = np.asarray(ts)
        y = self.buffer[0:ts.size, :]
        return ts,y



class LSLReceiver(QObject):
    """docstring for LSLReceiver"""

    evt_lslRcv = pyqtSignal(str,np.ndarray,np.ndarray)


    def __init__(self, wanted_inlets=None):
        super(LSLReceiver, self).__init__()
        self.wanted_inlets = wanted_inlets

        self.inlets: List[Inlet] = []

        self.info_names=[]

        self.search_new_inlet()

        self.start_time = pylsl.local_clock() 

        # create a timer that will pull and add new data occasionally
        self.pull_timer = QtCore.QTimer()
        self.pull_timer.timeout.connect(self.update)
        self.pull_timer.start(10)


    def get_additional_marker_inlet(self):
        # if 'psycho_marker' in self.info_names:
        #     return 's'
        new_add_marker_inlets=[]
        streams = pylsl.resolve_streams()
        # print(len(streams))
        for info in streams:
            if info.name() in self.info_names:
                continue
            if info.type() == 'Markers':
                if info.nominal_srate() != pylsl.IRREGULAR_RATE \
                        or info.channel_format() != pylsl.cf_string:
                        print('Invalid marker stream ' + info.name())
                print('Adding marker inlet: ' + info.name())
                self.inlets.append(MarkerInlet(info,'Markers'))
                self.info_names.append(info.name())
                new_add_marker_inlets.append(info.source_id())
                
        return new_add_marker_inlets

    def search_new_inlet(self):
        print("looking for streams")
        streams = pylsl.resolve_streams()
        for info in streams:
            if self.wanted_inlets is not None: # if not none, then only search for this specific inlet; if is none, then search all
                if info.source_id() in self.wanted_inlets:
                    print('Adding inlet: ' + info.name())
                    if info.type() == 'Markers':
                        self.inlets.append(MarkerInlet(info,'Markers'))
                        self.info_names.append(info.name())
                    else:
                        self.inlets.append(DataInlet(info,'Signals'))
                        self.info_names.append(info.name())
            else:
                if info.name() in self.info_names:
                    continue

                if info.type() == 'Markers':
                    if info.name()[:13] == 'psycho_marker':
                        print('Adding marker inlet: ' + info.name())
                        self.inlets.append(MarkerInlet(info,'Markers'))
                        self.info_names.append(info.name())

                    elif info.name()[:14] == 'predict_marker':
                        print('Adding marker inlet: ' + info.name())
                        self.inlets.append(MarkerInlet(info,'Markers'))
                        self.info_names.append(info.name())

                elif info.nominal_srate() != pylsl.IRREGULAR_RATE \
                        and info.channel_format() != pylsl.cf_string:
                    if (info.name()!=None):
                        if(info.name()=='mi_eeg'):
                            print('add data inlet: mi_eeg')
                            self.inlets.append(DataInlet(info,'Signals'))
                            self.info_names.append(info.name())
  
                        if(info.name()=='mi_acc'):
                            print('add data inlet: mi_acc')
                            self.inlets.append(DataInlet(info,'Signals'))
                            self.info_names.append(info.name())

                        if(info.name()=='hb_eeg'):
                            print('add data inlet: hb_eeg')
                            self.inlets.append(DataInlet(info,'Signals'))
                            self.info_names.append(info.name())

                else:
                    print('Don\'t know what to do with stream ' + info.name())

    def update(self):

        for inlet in self.inlets:

            ts,y = inlet.pull_data()

            if not len(ts)>0:
                continue

            # elapsed_time = ts-self.start_time
            # elapsed_time = elapsed_time

            if inlet.inlet_type == 'Signals':
                # print(inlet.name)
                if inlet.name == 'mi_eeg':
                    if y.shape[1]== inlet.channel_count:
                        # self.deal_with_data_inlet(elapsed_time,y)
                        # self.evt_lslRcv.emit(inlet.name,elapsed_time,y)
                        self.evt_lslRcv.emit(inlet.name,ts,y)
                    else:
                        print(y.shape[1])
                        print(inlet.channel_count)
                        print('maybe something wrong')

                if inlet.name == 'mi_acc':
                    if y.shape[1]== inlet.channel_count:
                        # self.evt_lslRcv.emit(inlet.name,elapsed_time,y)
                        self.evt_lslRcv.emit(inlet.name,ts,y)
                        # self.deal_with_data_acc_inlet(elapsed_time,y)
                    else:
                        print(y.shape[1])
                        print(inlet.channel_count)
                        print('maybe something wrong')

                if inlet.name == 'hb_eeg':
                    if y.shape[1]== inlet.channel_count:
                        # self.evt_lslRcv.emit(inlet.name,elapsed_time,y)
                        self.evt_lslRcv.emit(inlet.name,ts,y)
                        # self.deal_with_data_acc_inlet(elapsed_time,y)
                    else:
                        print(y.shape[1])
                        print(inlet.channel_count)
                        print('maybe something wrong')
                        
            if inlet.inlet_type == 'Markers':
                if inlet.name[:13] == 'psycho_marker':
                    # self.evt_lslRcv.emit(inlet.name,elapsed_time,y)
                    self.evt_lslRcv.emit(inlet.name,ts,y)

