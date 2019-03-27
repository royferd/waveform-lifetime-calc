# -*- coding: utf-8 -*-
"""
date: 11/4/2018
Author: Roy Ready, roy.r.phys@gmail.com

This program will compute sample averages and sample deviations from the output
file from parse-hv-waveform-output.py

"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import math
from scipy.optimize import curve_fit
import glob, os


def func(x,c,a,tau):
    return c + a*np.exp(-x/tau)

def hv_ramp_plot(x1,y1,yerr1,x2,y2,yerr2,yaxislabel,title,save_image_fn):
        font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

        plt.rc('font', **font)

        plt.rc('text', usetex=True)                 

        plt.figure(figsize=[12.0,8.0])
        plt.errorbar(x1,y1,yerr1,capsize=5,markersize=10,markerfacecolor='none',markeredgecolor="red",fmt='ro')
        if len(x2) > 0:
            plt.errorbar(x2,y2,yerr2,capsize=5,markersize=10,markerfacecolor='none',markeredgecolor="blue",fmt='bx')
#        plt.plot(dt_fit,np.multiply(func(dt_fit,*popt),waveform_scale),'r-')
        ax = plt.gca
        plt.xlabel('voltage (kV)')
        plt.ylabel(yaxislabel)
        plt.title(title)
        lgd = plt.legend(('$- \mathrm{ve}$','$+\mathrm{ve}$'),bbox_to_anchor=(1.2,1.0))
        #plt.annotate(eqn_str,xy=(0.225,0.5),xycoords='axes fraction' )
        plt.savefig(save_image_fn,bbox_extra_artists=(lgd,), bbox_inches='tight')
        #plt.show()
        plt.close()

def parse_param_samples(filename):
    str2date_first_column = lambda x: datetime.strptime(x.decode("utf-8"),"%m-%d-%Y-%H%M%S")
    
    data = np.genfromtxt(filename,delimiter='\t')
        
    length_data = len(data)
    count = []
    array_ones = []
    for i in range(0,length_data):
        x = float(data[i][3]) 
        if math.isnan(x) == True:
            count = np.append(count,i)
            array_ones = np.append(array_ones,1)
    
    for i in range(0,len(count)):
        data = np.delete(data,count[i],0)
        count = np.subtract(count,array_ones)
    
    nonzero_data = length_data - len(count)
    print(nonzero_data)
    
    voltage_neg = []
    voltage_pos = []
    time_const_neg = []
    time_const_pos = []
    time_const_stdev_neg = []
    time_const_stdev_pos = []
    amplitude_neg = []
    amplitude_pos = []
    amplitude_stdev_neg = []
    amplitude_stdev_pos = []
    
    for i in range(0,nonzero_data):
        if data[i][0] < 0:
            voltage_neg = np.append(voltage_neg,data[i][0])
            time_const_neg = np.append(time_const_neg,data[i][1])
            time_const_stdev_neg = np.append(time_const_stdev_neg,data[i][2])
            amplitude_neg = np.append(amplitude_neg,data[i][3])
            amplitude_stdev_neg = np.append(amplitude_stdev_neg,data[i][4])
        else:
            voltage_pos = np.append(voltage_pos,data[i][0])
            time_const_pos = np.append(time_const_pos,data[i][1])
            time_const_stdev_pos = np.append(time_const_stdev_pos,data[i][2])
            amplitude_pos = np.append(amplitude_pos,data[i][3])
            amplitude_stdev_pos = np.append(amplitude_stdev_pos,data[i][4])           
    
    return voltage_neg,voltage_pos,time_const_neg,time_const_pos,time_const_stdev_neg,time_const_stdev_pos,amplitude_neg,amplitude_pos,amplitude_stdev_neg,amplitude_stdev_pos

def main(yaxislabel1,title1,yaxislabel2,title2):
    
    file_ = []
    for string in glob.glob("avg-values.txt"):
            file_ = np.append(file_,string)
    print(file_)
    
    for i in range(len(file_)):
        
        voltage_neg,voltage_pos,time_const_neg,time_const_pos,time_const_stdev_neg,time_const_stdev_pos,amplitude_neg,amplitude_pos,amplitude_stdev_neg,amplitude_stdev_pos = parse_param_samples(file_[i])
        
        hv_ramp_plot(np.abs(voltage_neg),time_const_neg,time_const_stdev_neg,voltage_pos,time_const_pos,time_const_stdev_pos,yaxislabel1,title1,"decay_plot_lifetime.png")
        hv_ramp_plot(np.abs(voltage_neg),amplitude_neg,amplitude_stdev_neg,voltage_pos,amplitude_pos,amplitude_stdev_pos,yaxislabel2,title2,"decay_plot_amplitude.png")
        
        amplitude_neg_wt = []
        amplitude_pos_wt = []
        time_const_neg_wt = []
        time_const_pos_wt = []
        
        '''calculate weights'''
        for i in range(len(voltage_neg)):
            amplitude_neg_wt = np.append(amplitude_neg_wt,1/(amplitude_stdev_neg[i]**2))
            amplitude_pos_wt = np.append(amplitude_pos_wt,1/(amplitude_stdev_pos[i]**2))
            time_const_neg_wt = np.append(time_const_neg_wt,1/(time_const_stdev_neg[i]**2))
            time_const_pos_wt = np.append(time_const_pos_wt,1/(time_const_stdev_pos[i]**2))
        
        '''find weighted total averages'''
        amplitude_neg_sample_mean = np.average(amplitude_neg,weights=amplitude_neg_wt)
        amplitude_pos_sample_mean = np.average(amplitude_pos,weights=amplitude_pos_wt)
        time_const_neg_sample_mean = np.average(time_const_neg,weights=time_const_neg_wt)
        time_const_pos_sample_mean = np.average(time_const_pos,weights=time_const_pos_wt)
        
        '''find total stdev'''
        amplitude_neg_sample_stdev = np.power(np.sqrt(sum(amplitude_neg_wt)),-1)
        amplitude_pos_sample_stdev = np.power(np.sqrt(sum(amplitude_pos_wt)),-1)
        time_const_neg_sample_stdev = np.power(np.sqrt(sum(time_const_neg_wt)),-1)
        time_const_pos_sample_stdev = np.power(np.sqrt(sum(time_const_pos_wt)),-1)
        
        '''convert to strings for output'''
        
        amplitude_neg_sample_mean_str = str(amplitude_neg_sample_mean)
        amplitude_pos_sample_mean_str = str(amplitude_pos_sample_mean)
        amplitude_neg_sample_stdev_str = str(amplitude_neg_sample_stdev)
        amplitude_pos_sample_stdev_str = str(amplitude_pos_sample_stdev)
        time_const_neg_sample_mean_str = str(time_const_neg_sample_mean)
        time_const_pos_sample_mean_str = str(time_const_pos_sample_mean)
        time_const_neg_sample_stdev_str = str(time_const_neg_sample_stdev)
        time_const_pos_sample_stdev_str = str(time_const_pos_sample_stdev)
        
        print("avg neg amplitude (nA):" + "\t" + amplitude_neg_sample_mean_str + " +/- " + amplitude_neg_sample_stdev_str + "\n")
        print("avg pos amplitude (nA):" + "\t" + amplitude_pos_sample_mean_str + " +/- " + amplitude_pos_sample_stdev_str + "\n")
        print("avg neg time const(s):" + "\t" + time_const_neg_sample_mean_str + " +/- " + time_const_neg_sample_stdev_str + "\n")
        print("avg pos time const(s):" + "\t" + time_const_pos_sample_mean_str + " +/- " + time_const_pos_sample_stdev_str + "\n")

        f = open('total-weighted-averages.txt',"a")
        f.write("avg neg amplitude (nA):" + "\t" + amplitude_neg_sample_mean_str + "\t" + amplitude_neg_sample_stdev_str + "\n")
        f.write("avg pos amplitude (nA):" + "\t" + amplitude_pos_sample_mean_str + "\t" + amplitude_pos_sample_stdev_str + "\n")
        f.write("avg neg time const(s):" + "\t" + time_const_neg_sample_mean_str + "\t" + time_const_neg_sample_stdev_str + "\n")
        f.write("avg pos time const(s):" + "\t" + time_const_pos_sample_mean_str + "\t" + time_const_pos_sample_stdev_str + "\n")
        f.close()
        
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
    