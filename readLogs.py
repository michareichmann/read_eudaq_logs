#!/usr/bin/env python

# ====================================
# IMPORTS
# ====================================
import argparse
import functions
import json
from collections import OrderedDict

# ====================================
# PARSER
# ====================================
parser = argparse.ArgumentParser()
default_logs = "eudaq_logs/"
parser.add_argument("-l", "--logfile", nargs='?', default=default_logs, help="enter the filepath of the Keithley-log")
parser.add_argument("-r", "--run", nargs='?', default="-1", help="enter the runnumber without date information")
args = parser.parse_args()


# name of the file you want to create
filename = "runs_PSI_August_2015.json"

# set run_mode
run_mode = True
if args.run == "-1":
    run_mode = False

# print out which run you're looking at
if run_mode:
    print "Information for run:", args.run


# ====================================
# DEFAULT DICTIONARY
# ====================================
def_dict = OrderedDict(
    [("persons on shift", "none"),
     ("run info", "none"),
     ("type", "none"),
     ("configuration", "none"),
     ("mask", "none"),
     ("masked pixels", 0),
     ("diamond 1", "none"),
     ("diamond 2", "none"),
     ("hv dia1", -1),
     ("hv dia2", -1),
     ("fs11", -1),
     ("fsh13", -1),
     ("quadrupole", "none"),
     ("analogue current", -1),
     ("digital current", -1),
     ("begin date", "none"),
     ("trim time", "none"),
     ("config time", "none"),
     ("start time", "none"),
     ("trig accept time", "none"),
     ("opening time", "none"),
     ("open time", "none"),
     ("stop time", "none"),
     ("raw rate", -1),
     ("prescaled rate", -1),
     ("to TLU rate", -1),
     ("pulser accept rate", -1),
     ("cmspixel events", -1),
     ("drs4 events", -1),
     ("datacollector events", -1),
     ("aimed flux", -1),
     ("measured flux", -1),
     ("user comments", "none")
     ])


# ====================================
# GET FIRST AND LAST RUN FOR BEGIN AND END OF THE LOOP
# ====================================
start = 0
stop = 0
if not run_mode:
    start = functions.find_first_run(args.logfile)
    stop = functions.find_last_run(args.logfile) + 1
elif run_mode:
    start = int(args.run) - 1
    stop = start + 2


# ====================================
# LOOP OVER ALL RUNS
# ====================================
runs = {}

# save all the keys from the dict in a list
# workaround because "search_log" won't accept default dictionary
tags = []
for key in def_dict:
    tags.append(key)

for run in range(start, stop):

    print run
    # copy the default log_dict
    log_dict = def_dict.copy()

    # create an empty dict
    info = {}
    for key in tags:
        info[key] = ""

    if not run_mode:
        print "processing run", run

    # find the right logfile and show it
    logfile = functions.find_file(args.logfile, str(run))
    stripped_file = logfile.split("/")[-1]
    print "looking in logfile:", stripped_file

    # main function that searches the log and fills the empty dictionary
    functions.search_log(logfile, str(run), info)

    # copy all non empty entries to the log dictionary
    for key in info:
        if info[key] != "":
            log_dict[key] = info[key]

    # copy information from last run if run info "continued"
    if log_dict["run info"] == "Continued":
        functions.copy_last_run(log_dict, run, runs)

    # calculate the fluxes
    log_dict["aimed flux"] = functions.get_flux("PSI_May15", log_dict["fs11"], log_dict["fsh13"])
    log_dict["measured flux"] = functions.calc_flux(log_dict["masked pixels"], log_dict["raw rate"])

    # find persons that were on shift when the run was started
    # log_dict["persons on shift"] = functions.get_persons("PSI_May15", log_dict["start time"], log_dict["begin date"])

    # save only the runs where any value differs from default
    if log_dict != def_dict:
        runs[functions.convert_run(str(run))] = log_dict
    else:
        print "there are no information for this run"

    # take the same order as entered
    runs = OrderedDict(runs)


# ====================================
# SAVING // PRINTING THE INFORMATION
# ====================================
# save json to file
if not run_mode:
    f = open(filename, 'w')
    f.write(json.dumps(runs, indent=4))
    print "save rundata in file:", filename
    f.close()

# print out for single run mode
else:
    del runs[functions.convert_run(start)]
    print json.dumps(runs, indent=4)
