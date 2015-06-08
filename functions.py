import glob
from datetime import datetime, time
import re


# converts the entered run number
def convert_run(number):
    run_number = ""
    number = int(number)
    if number >= 1000:
        print "The entered run number has to be lesser then 1000"
        exit()
    elif number >= 100:
        run_number = "150500" + str(number)
    elif number >= 10:
        run_number = "1505000" + str(number)
    else:
        run_number = "15050000" + str(number)
    return run_number

# find the right logfile:
def find_file(log, run):
    start_tag =  "Starting Run " + convert_run(run)
    filename = ""
    got_start = ""
    eudaq_log_dir = str(log) + "2015-*"
    for name in glob.glob(eudaq_log_dir):
        logfile = open(name, 'r')
        for line in logfile:
            data = line.split("\t")
            if len(data) > 1:
                if data[1].startswith(start_tag):
                    got_start = data[2]
        filename = name
        if len(got_start) > 3:
            break
        logfile.close()
    return filename

# loop over logs
def search_log(log, run, info):
    start_tag   = "Starting Run " + convert_run(run)
    stop_tag    = "End of run " + convert_run(run)
    trig_tag    = "Trigger are now"
    conf_tag    = "Configured"
    logfile = open(log, 'r')
    for line in logfile:
        data = line.split("\t")
        if len(data) > 1:
            if data[1].startswith(start_tag):
                info["start"] = make_time(data[2])
                dia = data[1].replace("(", " ").replace(")", " ").replace(":", " ").replace(";", " ").split()
                if len(dia) > 3:
                    info["dia1"]    = dia[4]
                    info["hv1"]     = dia[5]
                    info["dia2"]    = dia[7]
                    info["hv2"]     = dia[8]
                    info["type"]    = dia[-1]
                    info["fs11"]    = dia[10]
                    info["fsh13"]   = dia[12]
                    info["quad"]    = dia[13]
                else:
                    print "user entered no specific run data"
            if "opening" in data[1]:
                info["opening"] = make_time(data[2])
            if "open" in data[1]:
                info["open"] = make_time(data[2])
            if data[1].startswith(trig_tag):
                info["trig"] = make_time(data[2])
            if data[1].startswith(conf_tag):
                info["config"] = data[1].replace("("," ").replace(")", " ").split()[-1] + " " + make_time(data[2])
            if data[1].startswith(stop_tag):
                info["stop"] = make_time(data[2])
        if len(info["stop"]) > 1:
            break
    logfile.close()
    return info

# convert time
def make_time(string):
    time = datetime.strptime(string, "%Y-%m-%d %H:%M:%S.%f").strftime("%m/%d %H:%M:%S")
    return time
