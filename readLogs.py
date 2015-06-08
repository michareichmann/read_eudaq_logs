import argparse
import functions


parser = argparse.ArgumentParser()
default_logs = "../readkeithleycurrent/eudaq_logs/"
parser.add_argument("-l", "--logfile", nargs='?', default=default_logs, help="enter the filepath of the Keithley-log")
parser.add_argument("-r", "--run", nargs='?', default="0", help="enter the runnumber without date information")

args = parser.parse_args()

if args.run != "0":
    print "Information for run:", args.run

tags = ["type", "start","stop", "dia1", "dia2", "hv1", "hv2", "fs11", "fsh13", "quad", "config", "trig", "opening", "open"]
info = {}
for key in tags:
    info[key] = []

logfile = functions.find_file(args.logfile, args.run)
stripped_file = logfile.split("/")[-1]
print "looking in logfile:", stripped_file

functions.search_log(logfile, args.run, info)

for key in tags:
    print key, "\t", info[key]
