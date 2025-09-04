# -*- coding: utf-8 -*-

from matplotlib import mlab
import matplotlib.pyplot as plt

import numpy as np


class PLOTSOMEx:
    def __init__(self,nchannels,nsamples,fs):
        '''
        
        
        '''     
        self.nchannels = nchannels
        self.nsamples = nsamples
        self.fs = fs
     
        
    
    
    def psd(self,trials):
        '''
        Calculates for each trial the Power Spectral Density (PSD).
        
        Parameters
        ----------
        trials : 3d-array (channels x samples x trials)
            The EEG signal
        
        Returns
        -------
        trial_PSD : 3d-array (channels x PSD x trials)
            the PSD for each trial.  
        freqs : list of floats
            The frequencies for which the PSD was computed (useful for plotting later)
        '''
        nchannels = self.nchannels
        nsamples = self.nsamples
        fs = self.fs
        fft_result_num = int(nsamples/2+1)
                
        
        ntrials = trials.shape[2]
        trials_PSD = np.zeros((self.nchannels, fft_result_num, ntrials))
    
        # Iterate over trials and channels
        for trial in range(ntrials):
            for ch in range(nchannels):
                # Calculate the PSD
                (PSD, freqs) = mlab.psd(trials[ch,:,trial], NFFT=int(nsamples), Fs=fs)
                trials_PSD[ch, :, trial] = PSD
                    # .ravel()
        return trials_PSD, freqs
    
    

    def plot_psd(self,trials_PSD, freqs, chan_ind, chan_lab=None, maxy=None):
        '''
        Plots PSD data calculated with psd().
        
        Parameters
        ----------
        trials : 3d-array
            The PSD data, as returned by psd()
        freqs : list of floats
            The frequencies for which the PSD is defined, as returned by psd() 
        chan_ind : list of integers
            The indices of the channels to plot
        chan_lab : list of strings
            (optional) List of names for each channel
        maxy : float
            (optional) Limit the y-axis to this value
        '''
        plt.figure(figsize=(12,5))
        
        nchans = len(chan_ind)
        
        # Maximum of 3 plots per row
        nrows = int(np.ceil(nchans / 3))
        ncols = min(3, nchans)
        
        # Enumerate over the channels
        for i,ch in enumerate(chan_ind):
            # Figure out which subplot to draw to
            plt.subplot(nrows,ncols,i+1)
        
            # Plot the PSD for each class
            for cl in trials_PSD.keys():
                plt.plot(freqs, np.mean(trials_PSD[cl][ch,:,:], axis=1), label=cl)
        
            # All plot decoration below...
            
            plt.xlim(1,30)
            
            if maxy != None:
                plt.ylim(0,maxy)
        
            plt.grid()
        
            plt.xlabel('Frequency (Hz)')
            
            if chan_lab == None:
                plt.title('Channel %d' % (ch+1))
            else:
                plt.title(chan_lab[i])
    
            plt.legend()
            
        plt.tight_layout()
        plt.show(block=False)
        
    def plot_psd_simple(self,trials_csp_1,trials_csp_2):
        
        # print(trials_csp_1.shape)
        # print(trials_csp_2.shape)
        
        psd_r, freqs = self.psd(trials_csp_1)
        psd_f, freqs = self.psd(trials_csp_2)
        trials_PSD = {'cl1': psd_r, 'cl2': psd_f}
        
        # chan_ind : list of integers:             The indices of the channels to plot
        chan_ind = [0,1,2,3,4,5,6,7]
        
        # self.plot_psd(trials_PSD, freqs, chan_ind, chan_lab=['first component', 'middle component', 'last component'], maxy=0.75 )
        # self.plot_psd(trials_PSD, freqs, chan_ind, maxy=0.75 )
        self.plot_psd(trials_PSD, freqs, chan_ind)

        # self.plot_psd(trials_PSD, freqs, [0,28,-1],  maxy=0.75 )

        
        return 0





