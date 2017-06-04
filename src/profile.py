#import cProfile
import os
#import pstats
import sys 

import line_profiler

# Import function for profiling
def import_test():
    # Standard library imports
    import json
    import logging.config
    import os
    import sys
    import time
    import traceback
    
    # Start logging temporarily with file object
    sys.stderr = open("../logs/error.log", "w")
    info_log = open("../logs/info.log", "w")
    info_log.close()
    date_format = time.strftime("%m/%d/%Y %H:%M:%S %p ")
    sys.stderr.write(date_format + " - root - [WARNING] - ")
      
    # Third-party library imports
    import numpy as np
    import pandas as pd
    import yaml
    
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import r2_score
    from sklearn.metrics import mean_squared_error

    # Local imports
    # New modules - marco.pritoni@gmail.com
    from preprocessor import DataPreprocessor
    from pi_datalink import PIDatalink
    
    print "import_test done"

"""
# Function-level profiling
with open("profile-func.txt", "w") as file:
    cProfile.run("execfile(\"mv_model.py\")", "profile")
    stats = pstats.Stats("profile", stream=file)
    stats.sort_stats('cumulative').print_stats()
    os.remove("profile")
"""

# Line-by-line profiling
# See https://github.com/rkern/line_profiler for more details       
with open("profile-line.txt", "w") as profile:
    profiler = line_profiler.LineProfiler(import_test)
    profiler.runcall(import_test)
    
    # import here to prevent import_test from being affected
    import mv_model
    profiler.add_function(mv_model.main)
    
    #import test 
    #profiler.add_function(test.cache_point)
    
    with open("output.txt", "w") as output:
        sys.stdout = output
        sys.argv = ["", "@test_input.txt"]
        profiler.runcall(mv_model.main)
        #profiler.runcall(test.cache_point, "NSRDB.136708.OAT.TMY")
        
    os.remove("output.txt")  
    profiler.print_stats(stream=profile)
    
