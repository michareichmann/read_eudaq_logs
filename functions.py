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
    start_tag = "Starting Run " + convert_run(run)
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


# find the last run
def find_last_run(log):
    eudaq_log_dir = str(log) + "2015-*"
    logs = []
    last_run = 0
    for name in glob.glob(eudaq_log_dir):
        logs.append(name)
    logs = sorted(logs)
    logfile = open(logs[-1],'r')
    ind = -1
    while True:
        data = logfile.readlines()[ind].split("\t")
        if data[1].startswith("Stopping"):
            last_run = data[1].split()[2]
            break
        logfile.seek(0)
        ind -= 1
    logfile.close()
    last_run = int(str(last_run)[4:])
    return last_run


# loop over logs
def search_log(log, run, info):
    found_start = False
    look_for_start = True
    look_for_stop = True
    count = False
    stop_loop = 0
    begin_tag = "Stopping Run " + convert_run(int(run) - 1)
    start_tag = "Starting Run " + convert_run(run)
    stop_tag = "Stopping Run " + convert_run(run)
    end_tag = "Starting Run " + convert_run(int(run) + 1)
    event_tag = "Run " + convert_run(run)
    trig_tag = "Trigger are now"
    conf_tag = "Configured"
    trim_tag = "Trimming success"
    ia_tag = "Analog current"
    id_tag = "Digital current"
    mask_tag = "Using maskfile"
    rate_tag = "rate"
    mask_pix_tag = "--> masked"
    logfile = open(log, 'r')
    for line in logfile:
        data = line.split("\t")
        if len(data) > 1:
            # start looking when:
            if data[1].startswith(begin_tag):
                found_start = True
                look_for_start = False
            elif data[1].startswith(start_tag) and look_for_start:
                found_start = True
                look_for_start = False
                logfile.seek(0)
            # stop looking when:
            if len(info["stop time"]) > 1:
                count = True
                look_for_stop = False
            elif data[1].startswith(end_tag)  and look_for_stop:
                break
            if count:
                stop_loop += 1
            if stop_loop == 7:
                break
            # searching fo information
            if found_start:
                find_run(start_tag, data, info)
                if "opening" in data[1]:
                    info["opening time"] = make_time(data[2])
                if "open" in data[1]:
                    info["open time"] = make_time(data[2])
                find_time(trig_tag, data, info, "trig accept time")
                find_time(trim_tag, data, info, "trim time")
                find_conf(conf_tag, data, info)
                find_time(stop_tag, data, info, "stop time")
                find_current(ia_tag, data, info, "analogue current")
                find_current(id_tag, data, info, "digital current")
                find_mask(mask_tag, data, info)
                find_rate(rate_tag, data, info)
                find_events(event_tag, data, info)
                find_masked_pixels(mask_pix_tag, data, info)
                find_comments(data, info)
    logfile.close()
    return info


# convert time
def make_time(string):
    date_time = datetime.strptime(string, "%Y-%m-%d %H:%M:%S.%f").strftime("%H:%M:%S")
    return date_time


def find_time(tag, data, info, key):
    if data[1].startswith(tag):
        info[key] = make_time(data[2])
    return info


def find_current(tag, data, info, key):
    if data[1].startswith(tag):
        current = float(data[1].split()[2][:-2])
        info[key] = current
    return info


def find_events(tag, data, info):
    if data[1].startswith(tag):
        events = data[1].split()
        if events[2] == "ended":
            info["drs4 events"] = int(events[4])
        elif events[2] == "EORE":
            info["datacollector events"] = int(events[4])
        elif events[2] == "detector":
            cms = events[6].strip("()").split("/")
            info["cmspixel events"] = int(cms[0])
    return info


def find_rate(tag, data, info):
    if data[1].lower().startswith(tag):
        rate = data[1]
        if len(rate) < 2:
            rate = data[1].split()
        rate = rate.replace("/", " ").replace(",", " ").replace(";", " ").replace(":", " ").split()
        if len(rate) == 7:
            del rate[2]
            del rate[1]
        # check if last entry isnt an int
        try:
            int(rate[-1])
        except ValueError:
            rate = []
        if len(rate) > 4:
            rate[1] = rate[1].lower().strip("k")
            info["raw rate"] = int(rate[1]) if not "." in rate[1] else int(float(rate[1])*1e3)
            info["prescaled rate"] = int(rate[2])
            info["to TLU rate"] = int(rate[3])
            info["pulser accept rate"] = int(rate[4])
        elif len(rate) > 3:
            info["raw rate"] = int(rate[1])
            info["prescaled rate"] = int(rate[2])
            info["to TLU rate"] = int(rate[3])
    return info


def find_mask(tag, data, info):
    if data[1].startswith(tag):
        conv_data = data[1].split()[-1].split("/")[-1]
        info["mask"] = conv_data
    return info


def find_masked_pixels(tag, data, info):
    if data[1].startswith(tag):
        mask = data[1].split()
        if int(mask[2]) > 10:
            info["masked pixels"] = int(mask[2])
    return info


def find_conf(tag, data, info):
    if data[1].startswith(tag):
        conv_data = data[1].replace("(", " ").replace(")", " ").split()[-1]
        info["configuration"] = conv_data
        info["config time"] = make_time(data[2])


def find_run(tag, data, info):
    if data[1].startswith(tag):
        info["start time"] = make_time(data[2])
        info["begin date"] = datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S.%f").strftime("%m/%d/%Y")
        dia = find_run_info(tag, data, info)

        if len(dia) > 13:
            try:
                info["diamond 1"] = make_dia_nice(dia[4])
                info["hv dia1"] = int(dia[5].strip("V"))
                info["diamond 2"] = make_dia_nice(dia[7])
                info["hv dia2"] = int(dia[8].strip("V"))
                info["type"] = dia[-1]
                info["fs11"] = int(dia[10])
                info["fsh13"] = int(dia[12]) if dia[12] != "0.5" else float(dia[12])
                info["quadrupole"] = dia[13]
            except ValueError:
                pass
        else:
            print "user entered no specific run data"
    return info

def find_run_info(tag, data, info):
    dia = data[1].replace("(", " ").replace(")", " ").replace(":", " ")
    dia = dia.replace(";", " ").replace(",", " ").split()
    ind = 0
    if len(dia) > 0:
        for i in dia:
            if i.lower() == "v":
                del dia[ind]
            ind += 1
    if len(dia) > 14:
        if "beam" in dia[11]:
            del dia[11:14]
        if "beam" in dia[15]:
            del dia[15:18]
        if dia[11].startswith("quad"):
            if dia[12].startswith("sett"):
                del dia[12]
            dia.insert(11,dia[15])
            dia.insert(11,dia[15])
    if len(dia) > 5:
        if "ramp" in dia[5]:
            del dia[6]
            del dia[5]
        if dia[3].startswith("dia") and ("signal" in dia[-1] or "ped" in dia[-1]):
            info["run info"] = "infos extracted"
        else:
            info["run info"] = data[1].lstrip(tag).lstrip(":").strip()
    else:
            info["run info"] = data[1].lstrip(tag).lstrip(":").strip()
    return dia

def find_comments(data, info):
    if data[0] == "USER" and not data[1].startswith("Run 1") and not "masked pixels in" in data[1]:
        if not "rate" in data[1] and not "/" in data[1]:
            if not "Successfully read" in data[1] and not "to USB" in data[1]:
                if not "scope output" in data[1] and not "pxar v" in data[1]:
                    info["user comments"] += data[1] + " // "
    return info


# unificate diamond style styles
def make_dia_nice(string):
    dia = string.replace("-", "").lower()
    last = dia[-1].upper()
    if dia[0] == "p":
        dia = dia[:-1]
        dia = dia + "-" + last
    if dia.startswith("ii"):
        dia = dia.strip("i")
        dia = "II-" + dia[0] + "-" + dia[1:3]
    if dia.startswith("s"):
        dia = dia.upper()
    if len(dia) == 2 and dia.isalnum():
        dia = "II-6-" + dia
    return dia


def get_flux(test, fs11, fsh13):
    flux = {
        "PSI_May15": {
            (15, 65): 20,
            (0.5, 65): 20,
            (10, 70): 70,
            (1, 70): 70,
            (70, 80): 700,
            (50, 80): 700,
            (70, 110): 2000,
            (50, 110): 2000,
            (148, 160): 5000
        }}
    if fs11 == -1 or fsh13 == -1:
        flux = -1
    else:
        try:
            flux = flux[test][(fsh13, fs11)]
        except KeyError:
            print "unknown shutter values"
            flux = -2
    return flux


def calc_flux(pixels, rate):
    area = ((80 * 52 - pixels) * 15e-5)
    flux = rate / area / 1e3
    if rate == -1:
        flux = -1
    else:
        flux = int(round(flux, 0))
    return flux

def copy_last_run(test, run, runs):
    test["diamond 1"] = runs[convert_run(run - 1)]["diamond 1"]
    test["diamond 2"] = runs[convert_run(run - 1)]["diamond 2"]
    test["hv dia1"] = runs[convert_run(run - 1)]["hv dia1"]
    test["hv dia2"] = runs[convert_run(run - 1)]["hv dia2"]
    test["fs11"] = runs[convert_run(run - 1)]["fs11"]
    test["fsh13"] = runs[convert_run(run - 1)]["fsh13"]
    test["quadrupole"] = runs[convert_run(run - 1)]["quadrupole"]
    test["type"] = runs[convert_run(run - 1)]["type"]
    test["configuration"] = runs[convert_run(run - 1)]["configuration"]
    test["mask"] = runs[convert_run(run - 1)]["mask"]
    test["masked pixels"] = runs[convert_run(run - 1)]["masked pixels"]
