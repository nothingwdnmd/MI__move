# -*- coding: utf-8 -*-

import numpy as np
import scipy.signal 


class CALCSPx:
    def __init__(self):
        '''
        csp
        
        '''     
        pass
     
        
    def cov_trials(self,trials):
        ''' Calculate the covariance for each trial and return their average '''
        ntrials = trials.shape[2]
        covs = [ np.cov(trials[:,:,i]) for i in range(ntrials) ]
        return np.mean(covs, axis=0)
    
    def get_csp_w(self,trials_cl1, trials_cl2):
        '''
        Calculate the CSP transformation matrix W.
        arguments:
            trials_cl1,trials_cl2 - Array (channels x samples x trials) 
        returns:
            Mixing matrix W  - Array (channels x channels) 
        '''
        cov_1 = self.cov_trials(trials_cl1)
        cov_2 = self.cov_trials(trials_cl2)

        [L,W_tmp] = scipy.linalg.eigh(cov_1, cov_2)
        sidx  = np.argsort(L)[::-1]
        W = W_tmp[:,sidx]  
            
        return W

    def apply_csp_single_trial(self, W, trial):
        ''' 
        Apply a mixing matrix to each trial (basically multiply W with the EEG signal matrix)
        the trials data should be : Array (channels x samples) 
        '''
        return  W.T.dot(trial)
    
    def apply_csp(self, W, trials):
        ''' 
        Apply a mixing matrix to each trial (basically multiply W with the EEG signal matrix)
        the trials data should be : Array (channels x samples x trials) 
        '''
        ntrials = trials.shape[2]
        trials_csp = np.zeros((trials.shape))
        for i in range(ntrials):
            trials_csp[:,:,i] = W.T.dot(trials[:,:,i])
        return trials_csp
    
    def get_apply_csp(self,trials_cl1, trials_cl2):
        w=self.get_csp_w(trials_cl1, trials_cl2)
        # trials_csp = {'cl1': self.apply_csp(w, trials_cl1),
        #               'cl2': self.apply_csp(w, trials_cl2)}
        return [self.apply_csp(w, trials_cl1),self.apply_csp(w, trials_cl2)]
    
    
    