import argparse
import functions
import json
from collections import OrderedDict

parser = argparse.ArgumentParser()
default_logs = "../readkeithleycurrent/eudaq_logs/"
parser.add_argument("-l", "--logfile", nargs='?', default=default_logs, help="enter the filepath of the Keithley-log")
parser.add_argument("-r", "--run", nargs='?', default="0", help="enter the runnumber without date information")

args = parser.parse_args()

if args.run != "0":
    print "Information for run:", args.run

arguments = OrderedDict(
    [("run info", "none"),
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

last_run = functions.find_last_run(args.logfile)

runs = {}

tags = []
for key in arguments:
    tags.append(key)

start = int(args.run) - 1
stop = start + 2
if args.run == "0":
    start = 1
    stop = last_run + 1

filename = "runs_PSI_May_2015.json"

for run in range(start, stop):

    test = arguments.copy()
    info = {}
    for key in tags:
        info[key] = ""

    print "processing run", run
    logfile = functions.find_file(args.logfile, str(run))
    stripped_file = logfile.split("/")[-1]
    print "looking in logfile:", stripped_file

    functions.search_log(logfile, str(run), info)

    for key in info:
        if info[key] != "":
            test[key] = info[key]


    # copy information from last run if run info continued
    if test["run info"] == "Continued":
        functions.copy_last_run(test, run, runs)

    test["aimed flux"] = functions.get_flux("PSI_May15", test["fs11"], test["fsh13"])
    test["measured flux"] = functions.calc_flux(test["masked pixels"], test["raw rate"])

    if test != arguments:
        runs[functions.convert_run(str(run))] = test
    else:
        print "there are no information for this run"
    runs = OrderedDict(runs)



if args.run == "0":
    f = open(filename, 'w')
    f.write(json.dumps(runs, indent=4))
    print "save rundata in file:", filename
    f.close()
else:
    # f = json.dumps(runs, indent=4)
    print json.dumps(runs, indent=4)
