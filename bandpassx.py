# -*- coding: utf-8 -*-

import numpy as np
import scipy.signal 


class BANDPASSx:
    def __init__(self, fs,lo,hi):
        '''
        Designs and applies a bandpass filter to the signal.
        
        Parameters
        ----------
        
        lo : float
            Lower frequency bound (in Hz)
        hi : float
            Upper frequency bound (in Hz)
        fs : float
            Sample rate of the signal (in Hz)
        '''

        self.fs = fs
        # self.nchannels = nchannels
        # self.nsamples = nsamples
        

        # The iirfilter() function takes the filter order: higher numbers mean a sharper frequency cutoff,
        # but the resulting signal might be shifted in time, lower numbers mean a soft frequency cutoff,
        # but the resulting signal less distorted in time. It also takes the lower and upper frequency bounds
        # to pass, divided by the niquist frequency, which is the sample rate divided by 2:
        self.a, self.b = scipy.signal.iirfilter(6, [lo/(fs/2.0), hi/(fs/2.0)])
        
    def apply_filter_2d(self,trial):
        '''
        trial2 : 2d-array (channels x samples)
            The EEGsignal
            
        Returns
        -------
        trials_filt : 2d-array (channels x samples)
            The bandpassed signal
            
        note that the filter will be executed on the axis=1 dimention
                
        '''        
        return scipy.signal.filtfilt(self.a, self.b, trial, axis=1)
        
    
    def apply_filter(self,trials):
        '''
        trials : 3d-array (channels x samples x trials)
            The EEGsignal
            
        Returns
        -------
        trials_filt : 3d-array (channels x samples x trials)
            The bandpassed signal
            
        note that the filter will be executed on the axis=1 dimention
                
        '''
        # Applying the filter to each trial
        ntrials = trials.shape[2]
        trials_filt = np.zeros(trials.shape)
        for i in range(ntrials):
            trials_filt[:,:,i] = self.apply_filter_2d(trials[:,:,i])
        
        return trials_filt
    

        
        

