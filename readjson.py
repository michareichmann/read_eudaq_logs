import json
import functions
import argparse
from collections import OrderedDict


parser = argparse.ArgumentParser()
default_file = "runs_PSI_May_2015.json"
parser.add_argument("-f", "--jsonfile", nargs='?', default=default_file, help="enter the file you want to analyse")
parser.add_argument("-r", "--run", nargs='?', default="0", help="enter the runnumber without date information")

args = parser.parse_args()

filename = args.jsonfile

f = open(filename, 'r')
data = json.load(f, object_pairs_hook=OrderedDict)


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

for run in range(first_run, last_run + 1):
    print run, data[functions.convert_run(run)]["type"]#, data[functions.convert_run(run)]["fsh13"],data[functions.convert_run(run)]["quadrupole"]