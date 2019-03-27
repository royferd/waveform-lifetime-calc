# -*- coding: utf-8 -*-
"""
date: 11/4/2018
Author: Roy Ready, roy.r.phys@gmail.com

This program will calculate (dis)charging current parameters for the Spinlab
HV test apparatus.

"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import math
from scipy.optimize import curve_fit
import glob, os
import gc


def func(x,c,a,tau):
    return c + a*np.exp(-x/tau)

def parse_wv_file(filename,voltage_scale):
    str2date_first_column = lambda x: datetime.strptime(x.decode("utf-8"),"%m/%d/%Y %H:%M:%S.%f")
    
    data = np.genfromtxt(filename,delimiter='\t',converters = {0: str2date_first_column})
    initial_date = datetime(1970,1,1,0,0,0,0)
        
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
    
    dt = []
    dt = np.append(dt,0.0)
    print(type(dt))
    waveform = []
    waveform = np.append(waveform,data[0][4])
    voltage = []
    voltage = np.append(voltage,data[0][2])
    
    for i in range(1,nonzero_data):
        delta = (data[i][0] - data[0][0]).total_seconds()
        delta = float(delta)
        dt = np.append(dt,delta)
        waveform = np.append(waveform,data[i][4])
        voltage = np.append(voltage,data[i][2])
        
    sign_voltage = 1
    
    if data[0][7] > 1.0:
        sign_voltage = -1
    
    index_max_waveform = np.argmax(np.abs(waveform[0:6000]))

    voltage_gradient = voltage[len(voltage)-1]-voltage[0]
    
    if voltage_gradient > 0.0 :
        voltage_mag = np.average(voltage[len(voltage)-11:len(voltage)-1])
        ramp_str = ' ramp up to'
    elif voltage_gradient < 0.0 :
        voltage_mag = np.average(voltage[0:10])
        ramp_str = ' ramp down from'
    
    voltage_setting = sign_voltage*voltage_scale*voltage_mag
    
    waveform_trim = waveform[index_max_waveform:]
    dt_trim = dt[index_max_waveform:]
    timestamp = data[0][0]
    
    return dt,dt_trim,waveform,waveform_trim,voltage_setting,timestamp,ramp_str

def main(data_directory):
    root_directory = os.getcwd()
#    data_directory = "./18kv-ramp-down-neg/"
    
    os.chdir(data_directory)
    file_ = []
    for string in glob.glob("*output-1.txt"):
            file_ = np.append(file_,string)
    print('files loaded: ')
    print(file_)
    waveform_scale = 200.0/(-10.0) # assumes 200 nA fixed range, gives units of nA
    voltage_scale = 30.0/10.0 # assumes Applied Kilovolts 30 kV power supply, gives units of kV

    
    for i in range(len(file_)):
        
        dt,dt_trim,waveform,waveform_trim,voltage_setting,timestamp,ramp_str = parse_wv_file(file_[i],voltage_scale)
    
        popt, pcov  = curve_fit(func,dt_trim,waveform_trim)
        
        date = str(timestamp)
        date = date.replace(" ","-")
        date = date.replace(":","")
        partdate = date.partition(".")
        date = partdate[0]
        
        save_image_fn = date + '.png'
        save_image_res_fn = date + '-res.png'
        
        print('timestamp: ', date)
        print('high voltage sign and magnitude: %.1f kV' %voltage_setting)
        print('fitted offset: %.6f nA' %popt[0])
        print('fitted amplitude: %.6f nA' %popt[1])
        print('fitted lifetime: %.6f s' %popt[2])
        print('covariance matrix:')
        print(pcov)
        print('')
        
        number_fit_points = 100
        dt_avg_step= (np.max(dt_trim)-np.min(dt_trim))/float(number_fit_points)
        dt_fit = []
        dt_fit = np.append(dt_fit,dt_trim[0])
        
        for i in range(1,number_fit_points):
            dt_fit = np.append(dt_fit,dt_fit[i-1]+dt_avg_step)
            
        residual = []
        for i in range(0,len(dt_trim)):
            residual = np.append(residual, np.multiply(waveform_trim[i] - func(dt_trim[i],*popt),waveform_scale))
            
        zero_y = [0.0, 0.0]
        zero_x = [dt_trim[0], dt_trim[len(dt_trim)-1]]
            
        
        offset = str(popt[0]*waveform_scale)
        offset_err = str(abs(np.sqrt(pcov[0][0])*waveform_scale))
        amplitude = str(popt[1]*waveform_scale)
        amplitude_err= str(abs(np.sqrt(pcov[1][1])*waveform_scale))
        lifetime = str(popt[2])
        lifetime_err = str(abs(np.sqrt(pcov[2][2])))
        date = str(date)
        voltage_string = str(voltage_setting)
        
        output_file_header = data_directory.replace('./','')
        output_file_header = output_file_header.replace('/','-')
        os.chdir(root_directory)
        f = open(output_file_header+'waveform-parameters.txt',"a")
        f.write(date + "\t" + voltage_string + "\t" + offset + "\t" + offset_err + "\t" + amplitude + "\t" + amplitude_err + "\t" + lifetime + "\t" + lifetime_err + "\n")
        f.close()
        os.chdir(data_directory)

        font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

        plt.rc('font', **font)

        plt.rc('text', usetex=True)         
        eqn_str = r'$I_{\mathrm{ramp}} = (%.2f \pm  %.2f)  + (%.1f \pm %.1f) \mathrm{exp}\left(\frac{-t }{ %.3f \pm %.3f}\right)$' %(float(offset),float(offset_err),float(amplitude),float(amplitude_err),float(lifetime),float(lifetime_err))
        eqn_res_str = r'$I_{\mathrm{raw}} - \left[%.2f \pm  %.2f)  + (%.1f \pm %.1f) \mathrm{exp}\left(\frac{-t }{ %.3f \pm %.3f}\right)\right]$' %(float(offset),float(offset_err),float(amplitude),float(amplitude_err),float(lifetime),float(lifetime_err))
        

        plt.figure(figsize=[12.0,8.0])
        plt.scatter(dt,np.multiply(waveform,waveform_scale),facecolors='none',edgecolor="black")
        plt.plot(dt_fit,np.multiply(func(dt_fit,*popt),waveform_scale),'r-')
        ax = plt.gca
        plt.xlabel('time (s)')
        plt.ylabel('picoammeter current (nA)')
        plt.title(date + ramp_str + ' %.1f kV' %voltage_setting)
        plt.annotate(eqn_str,xy=(0.225,0.5),xycoords='axes fraction' )
        plt.savefig(save_image_fn)
        #plt.show()
        plt.close()

        plt.figure(figsize=[12.0,8.0])
        plt.plot(zero_x,zero_y,'b--')
        plt.scatter(dt_trim,residual,facecolors='none',edgecolor="black")
        ax = plt.gca
        plt.xlabel('time (s)')
        plt.ylabel('picoammeter current (nA)')
        plt.title(date + ramp_str + ' %.1f kV residuals' %voltage_setting)
        plt.annotate(eqn_res_str,xy=(0.2,0.9),xycoords='axes fraction' )
        plt.savefig(save_image_res_fn)
        #plt.show()
        plt.close()
        
    os.chdir(root_directory)
    
    gc.collect()
    
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
    