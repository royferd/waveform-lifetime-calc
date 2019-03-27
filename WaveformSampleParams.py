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

def parse_param_output(filename):
    str2date_first_column = lambda x: datetime.strptime(x.decode("utf-8"),"%m-%d-%Y-%H%M%S")
    
    data = np.genfromtxt(filename,delimiter='\t',converters = {0: str2date_first_column})
        
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
    
    timestamp = []
    voltage = []
    time_const = []
    time_const_wt = []
    amplitude = []
    amplitude_wt = []
    
    for i in range(0,nonzero_data-1):
        timestamp = np.append(timestamp,data[i][0])
        voltage = np.append(voltage,data[i][1])
        time_const = np.append(time_const,data[i][6])
        time_const_wt = np.append(time_const_wt,np.power(data[i][7],-2))
        amplitude = np.append(amplitude,data[i][4])
        amplitude_wt = np.append(amplitude_wt,np.power(data[i][5],-2))
    
    return timestamp,voltage,time_const,time_const_wt,amplitude,amplitude_wt

def main():
    
    file_ = []
    for string in glob.glob('*waveform-parameters.txt'):
            file_ = np.append(file_,string)
    print(file_)
    
    for i in range(len(file_)):
        
        timestamp,voltage,time_const,time_const_wt,amplitude,amplitude_wt = parse_param_output(file_[i])
        
        time_const_avg = np.average(time_const,weights=time_const_wt)
        time_const_stdev = np.std(time_const,ddof=1)
        
        amplitude_avg = np.average(amplitude,weights=amplitude_wt)
        amplitude_stdev = np.std(amplitude,ddof=1)
        
        sign_voltage = 1
        if voltage[0]< 0:
            sign_voltage = -1
            
        voltage_max = sign_voltage*max(abs(voltage))
        
        voltage_str = str(voltage_max)
        time_const_avg_str = str(time_const_avg)
        time_const_stdev_str = str(time_const_stdev)
        amplitude_avg_str = str(amplitude_avg)
        amplitude_stdev_str = str(amplitude_stdev)
        
        f = open('avg-values.txt',"a")
        f.write(voltage_str + "\t" + time_const_avg_str + "\t" + time_const_stdev_str + "\t" + amplitude_avg_str + "\t" + amplitude_stdev_str + "\n")
        f.close()
    
if __name__ == "__main__":
    main()