# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 13:09:08 2018

@author: ready
"""
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import math
from scipy.optimize import curve_fit
import glob, os
import ParseHVWaveformOutput
import WaveformSampleParams
import PlotAverageValues

def main():
    '''
    ParseHVWaveformOutput.main("./14kv-ramp-up-neg/")
    ParseHVWaveformOutput.main("./15kv-ramp-up-neg/")
    ParseHVWaveformOutput.main("./16kv-ramp-up-neg/")
    ParseHVWaveformOutput.main("./17kv-ramp-up-neg/")
    ParseHVWaveformOutput.main("./17kv-2-ramp-up-neg/")
    ParseHVWaveformOutput.main("./17p5kv-ramp-up-neg/")
    ParseHVWaveformOutput.main("./18kv-ramp-up-neg/")
    
    ParseHVWaveformOutput.main("./14kv-ramp-up-pos/")
    ParseHVWaveformOutput.main("./15kv-ramp-up-pos/")
    ParseHVWaveformOutput.main("./16kv-ramp-up-pos/")
    ParseHVWaveformOutput.main("./17kv-ramp-up-pos/")
    ParseHVWaveformOutput.main("./17kv-2-ramp-up-pos/")
    ParseHVWaveformOutput.main("./17p5kv-ramp-up-pos/")
    ParseHVWaveformOutput.main("./18kv-ramp-up-pos/")   

    WaveformSampleParams.main() 
    '''
    PlotAverageValues.main("time constant (s)","HV Ramp down charging current","amplitude (nA)","HV ramp down charging current")
    
if __name__ == "__main__":
    main()