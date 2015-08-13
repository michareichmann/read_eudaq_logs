import json
import functions
import argparse
from collections import OrderedDict
import ROOT
from datetime import datetime


parser = argparse.ArgumentParser()
default_file = "runs_PSI_May_2015.json"
parser.add_argument("-f", "--jsonfile", nargs='?', default=default_file, help="enter the file you want to analyse")
parser.add_argument("-r", "--run", nargs='?', default="0", help="enter the runnumber without date information")
parser.add_argument("-i", "--info", nargs='?', default="type", help="enter info you look for")

args = parser.parse_args()

filename = args.jsonfile

f = open(filename, 'r')
data = json.load(f, object_pairs_hook=OrderedDict)





def convert_to_min(x):
    event = x.hour*60 + x.minute + float(x.second)/60
    return event

# find first and last run
first_run = data.iterkeys().next()
last_run = data.iterkeys().next()
for run in data:
    if first_run > run:
        first_run = run
    if run > last_run:
        last_run = run
last_run = int(str(last_run)[4:])
first_run = int(str(first_run)[4:])

if args.run != "0":
    print "json for run", args.run
    run = functions.convert_run(args.run)
    print json.dumps(data[run], indent=4)

# for run in range(first_run, last_run + 1):
#     print run, data[functions.convert_run(run)][args.info]

length_run = []
for run in range(first_run,last_run + 1):
    bla =functions.convert_run(run)
    # pr[functions.convert_run(run)][args.info]

    start = data[functions.convert_run(run)]["start time"]
    stop = data[functions.convert_run(run)]["stop time"]
    try:
        start = datetime.strptime(start, "%H:%M:%S")
        stop = datetime.strptime(stop, "%H:%M:%S")
    except ValueError:
        continue
    start = convert_to_min(start)
    stop = convert_to_min(stop)
    # print start
    if stop - start > 20:
        print run, data[bla]["measured flux"]

    #     diff = stop - start
    # else:
    #     diff = 24*60 - start + stop
    # length_run.append(diff)

# # print length_run
# c = ROOT.TCanvas("c", "run-length", 700, 300)
# low = min(length_run)
# high = max(length_run)
# h = ROOT.TH1F("h", "length", 300, 0, 50)
# # h.SetBit(ROOT.TH1.kCanRebin)
# for i in length_run:
#     h.Fill(i)
# h.Draw()
# raw_input()

