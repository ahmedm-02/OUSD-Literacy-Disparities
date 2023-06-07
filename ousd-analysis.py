import csv
import numpy as np
import matplotlib.pyplot as plt
from operator import add

LEVEL_LIST = ["Mid-Above Grade","Early On Grade", "1 Grade Below", 
                      "2 Grades Below" ,"3 or More Grades Below", "Did not take"]

# resample is a helper function that randomy samples 'n' objects from a list 'sample'. 
# It returns the randomly sampled list.
def resample(sample, n):
    return np.random.choice(sample, n, replace = True)

# convert raw numbers into percentages for 3rd/4th/5th
def percentage(zone_dict):
    size = zone_dict["Size"] - zone_dict["Did not take"] # exclude those who did not take
    for level in LEVEL_LIST:
        zone_dict[level] = zone_dict[level]/size
    
    return zone_dict

# Calculate and store i-Ready score counts by Zone
def elementary_scores_by_zone(zone, grade):

    # Input values outside of range, error
    if (zone < 0 or zone > 15 or grade < 3 or grade > 5):
        raise Exception("Input values out of range")

    # store data
    data = {"Size": 0, "Mid-Above Grade": 0, "Early On Grade": 0, "1 Grade Below": 0, 
            "2 Grades Below": 0, "3 or More Grades Below": 0, "Did not take": 0}

    with open('i-ready-reading.csv', 'r') as I_READY_READING:
        score_reader = csv.DictReader(I_READY_READING)
        for row in score_reader: # specific school and grade level
            if row["Zone"] != str(zone): continue # not looking at zone of interest
            if row["Grade"] != str(grade): continue # not looking at grade of interest

            data["Size"] += int(row["Size"])
            for level in LEVEL_LIST:
                data[level] += int(row[level])

    num_above = data["Mid-Above Grade"] + data["Early On Grade"]
    num_below = data["1 Grade Below"] + data["2 Grades Below"] + data["3 or More Grades Below"]

    # print(f"Zone {zone}, Grade {grade}")
    # print("At or Above: ", num_above)
    # print("Below: ", num_below)
    # print(data, "\n")
    return data

# Creates list of size frequency with each index having specified value
def list_creator_repeat(value, frequency):
    ls = []
    for i in range(frequency):
        ls.append(value)
    return ls

# Create sample of 1s (ready), 0s (middle and not ready) to represent kindergarten readiness levels
def create_sample_kinder(row):
    # initialize dict
    sample_info = {"size": 0, "sample": []}

    # Determine number of Kindergarteners who are Ready vs. Else
    zone_size = int(row["Size"])
    num_ready = round(zone_size * (int(row["Ready"]) / 100)) # "Ready" given as percentage
    num_not_ready = zone_size - num_ready # number of students who are NOT Ready ("Middle", "Not Ready")

    # Create sample of zone1, with 1s representing those who are READY and 0s representing Else
    zone_sample_list = list_creator_repeat(1, num_ready) + list_creator_repeat(0, num_not_ready)

    # update values in sample dict
    sample_info["size"] = zone_size
    sample_info["sample"] = zone_sample_list
    return sample_info

# Creates sample of 1s (ready) and 0s from i-Ready, which gives raw numbers (not percentages)
def create_sample_elementary(row):
    # initialize dict
    sample_info = {"size": 0, "sample": []}

    # Determine number of Kindergarteners who are Ready vs. Else
    zone_size = row["Size"]
    num_ready = row["Ready"] # "Ready" includes Above and On Grade Level
    num_not_ready = row["Not Ready"] # one, two, or three grades below

    # Create sample of zone1, with 1s representing those who are Ready and 0s representing Not Ready
    zone_sample_list = list_creator_repeat(1, num_ready) + list_creator_repeat(0, num_not_ready)

    # update values in sample dict
    sample_info["size"] = zone_size
    sample_info["sample"] = zone_sample_list
    return sample_info

# Uses bootstrapping to calculate p-Values of two different input zone lists
def bootstrap(zone1, zone2):

    TRIAL_RANGE = 10000
    n = len(zone1)
    m = len(zone2)

    observed_difference = abs(np.mean(zone1) - np.mean(zone2))
    universal_sample = zone1 + zone2
    count = 0

    for trials in range(TRIAL_RANGE):
        zone1_resample = resample(universal_sample, n)
        zone2_resample = resample(universal_sample, m)
        mu1 = sum(zone1_resample)/n
        mu2 = sum(zone2_resample)/m

        diff = abs(mu2 - mu1)
        if diff >= observed_difference:
            count += 1

    pValue = count/TRIAL_RANGE
    # print("Observed Difference: ", observed_difference)
    # print("P-value: ", pValue, "\n")
    return pValue

# Calculates the difference in kindergarten readiness levels between zones
def k_difference(zone1, zone2, parameter):

    # file names with associated parameters
    data_files = {"Advanced Literacy": "edi-advanced-literacy.csv", "Basic Literacy": "edi-basic-literacy.csv",
                  "Basic Numeracy": "edi-basic-numeracy.csv", "Interest": "edi-interest.csv"}
    population_1 = []
    population_2 = []

    # print(f"Analyzing EDI Data for {parameter} for pair ({zone1, zone2})")
    with open(data_files[parameter], 'r') as FILE:
        score_reader = csv.DictReader(FILE)
        for row in score_reader:
            # Create sample for Zone 1
            if (row["Zone"] == str(zone1)): # Zone 1
                population_1 = create_sample_kinder(row).get("sample")
                # mu1 = np.mean(population_1)
                # print(f"(Zone {zone1}) mean: ", mu1)

            # Create sample for Zone 2
            elif (row["Zone"] == str(zone2)): # Zone 2
                population_2 = create_sample_kinder(row).get("sample")
                # mu2 = np.mean(population_2)
                # print(f"(Zone {zone2}) mean: ", mu2)

        pValue = bootstrap(population_1, population_2)
        print("pValue: ", pValue)
        return pValue

# Compare all zones using EDI Data
def compare_zones_kindergarten(parameter):

    # file names with associated parameters
    data_files = {"Advanced Literacy": "advanced-literacy-comparison.csv", "Basic Literacy": "basic-literacy-comparison.csv",
                  "Basic Numeracy": "basic-numeracy-comparison.csv", "Interest": "interest-comparison.csv"}
    
    count = 0
    with open(data_files[parameter], 'w') as FILE: # write to CSV, store data
        writer = csv.writer(FILE)
        writer.writerow(["Zone A", "Zone B", "p-Value"])

        # analyze each zone pairing, store if statistically significant
        for zone1 in range (1, 16):
            for zone2 in range (zone1 + 1, 16):
                if zone1 == zone2: continue
                pVal = k_difference(zone1, zone2, parameter)
                if (pVal > 0.05):
                    print(f"({zone1}, {zone2}): {pVal}")
                    writer.writerow([zone1, zone2, pVal])
                    count += 1

    print("No difference: ", count)

# is there a significant difference between given zone and grade (for reading or math)
def elem_difference(zone1, zone2, grade, parameter):
    # file names with associated parameters
    data_files = {"Reading": "i-ready-reading.csv", "Math": "math csv name"} # TODO: Change name for math

    # initialize data storage
    zone1_totals = {"Ready": 0, "Not Ready": 0, "Size": 0}
    zone2_totals = {"Ready": 0, "Not Ready": 0, "Size": 0}
    population_1 = []
    population_2 = []

    with open(data_files[parameter], 'r') as FILE:
        score_reader = csv.DictReader(FILE)
        for row in score_reader:
            # Total up values from all schools in Zone 1 for specified grade
            if row["Zone"] == str(zone1) and row["Grade"] == str(grade): # Zone 1
                # Update totals in Zone 1
                zone1_totals["Ready"] += int(row["Mid-Above Grade"]) + int(row["Early On Grade"])
                zone1_totals["Not Ready"] += int(row["1 Grade Below"]) + int(row["2 Grades Below"]) + int(row["3 or More Grades Below"])
                zone1_totals["Size"] += zone1_totals["Ready"] + zone1_totals["Not Ready"]

            # Total up values from all schools in Zone 2 for specified grade
            elif (row["Zone"] == str(zone2) and row["Grade"] == str(grade)): # Zone 2
                # Update totals in Zone 2
                zone2_totals["Ready"] += int(row["Mid-Above Grade"]) + int(row["Early On Grade"])
                zone2_totals["Not Ready"] += int(row["1 Grade Below"]) + int(row["2 Grades Below"]) + int(row["3 or More Grades Below"])
                zone2_totals["Size"] += zone2_totals["Ready"] + zone2_totals["Not Ready"]

        # create samples and bootstrap
        population_1 = create_sample_elementary(zone1_totals).get("sample")
        population_2 = create_sample_elementary(zone2_totals).get("sample")
        pValue = bootstrap(population_1, population_2)
        print(f"Zone 1: {zone1}, Zone 2: {zone2}, Grade: {grade}")
        print("pValue: ", pValue)
        if pValue <= 0.05:
            print("Significant difference")
        return pValue
    
# Stacked bar graph of kindergarten zones based off of specified parameter    
def kindergarten_zone_rankings(parameter):
    # file names with associated parameters
    data_files = {"Advanced Literacy": "edi-advanced-literacy.csv", "Basic Literacy": "edi-basic-literacy.csv",
                  "Basic Numeracy": "edi-basic-numeracy.csv", "Interest": "edi-interest.csv"}
    
    num_zones = 15
    ind = np.arange(num_zones) 
    width = 0.25
    
    ready_vals = []
    middle_vals = []
    not_ready_vals = []

    with open(data_files[parameter], 'r') as FILE:
        score_reader = csv.DictReader(FILE)
        for row in score_reader:
            ready_vals.append(int(row["Ready"]))
            middle_vals.append(int(row["Middle"]))
            not_ready_vals.append(int(row["Not Ready"]))

        zones = (
            'Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5', 
            'Zone 6', 'Zone 7', 'Zone 8', 'Zone 9', 'Zone 10', 
            'Zone 11', 'Zone 12', 'Zone 13', 'Zone 14', 'Zone 15'
        )

        scores = {
            "Ready": ready_vals,
            "Middle": middle_vals,
            "Not Ready": not_ready_vals,
        }

        mean_readiness = np.mean(ready_vals)
        var_readiness = np.var(ready_vals)
        print(f"Readiness Vals: {ready_vals}")
        print(f"Mean Readiness: {mean_readiness}")
        print(f"Variance (Readiness): {var_readiness}")

        width = 0.5

        fig, ax = plt.subplots()
        bottom = np.zeros(15)
        red = "#fb3640"
        green = "#3caa57"
        yellow = "#f1d302"
        colors = [green, yellow, red]

        i = 0
        for boolean, weight_count in scores.items():
            p = ax.bar(zones, weight_count, width, label=boolean, bottom=bottom, color = colors[i],)
            bottom += weight_count
            i = (i + 1) % 3

        ax.set_title(f"Kindergarten Readiness Levels: {parameter}")
        plt.xlabel("Zones")
        plt.ylabel("Percentage")
        ax.axhline(y = mean_readiness, color = 'b', linestyle = '--')
        ax.legend(loc="upper right")

        plt.show()

    return

# rank elementary schools reading levels by specified grade
def elementary_zone_rankings(grade):
    ready_vals = []
    not_ready_vals = []
    for i in range(1, 16):
        print(f"Zone {i}")
        data = elementary_scores_by_zone(i, grade)
        ready = data["Mid-Above Grade"] + data["Early On Grade"]
        not_ready = data["1 Grade Below"] + data["2 Grades Below"] + data["3 or More Grades Below"]

        ready_vals.append(ready/(ready + not_ready))
        not_ready_vals.append(not_ready/(ready + not_ready))
        print(f"% Ready: {ready/(ready + not_ready)}")
        print(f"% Not ready: {not_ready/(ready + not_ready)} \n")

    mean_readiness = np.mean(ready_vals)
    var_readiness = np.var(ready_vals)
    print(f"Readiness Vals: {ready_vals}")
    print(f"Mean Readiness: {mean_readiness}")
    print(f"Variance (Readiness): {var_readiness}")

    zones = (
        'Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5', 
        'Zone 6', 'Zone 7', 'Zone 8', 'Zone 9', 'Zone 10', 
        'Zone 11', 'Zone 12', 'Zone 13', 'Zone 14', 'Zone 15'
    )

    scores = {
        "Ready": ready_vals,
        "Not Ready": not_ready_vals,
    }

    mean_readiness = np.mean(ready_vals)
    var_readiness = np.var(ready_vals)
    print(f"Readiness Vals: {ready_vals}")
    print(f"Mean Readiness: {mean_readiness}")
    print(f"Variance (Readiness): {var_readiness}")

    width = 0.5

    fig, ax = plt.subplots()
    bottom = np.zeros(15)
    red = "#fb3640"
    green = "#3caa57"
    yellow = "#f1d302"
    colors = [green, red]

    i = 0
    for boolean, weight_count in scores.items():
        p = ax.bar(zones, weight_count, width, label=boolean, bottom=bottom, color = colors[i],)
        bottom += weight_count
        i = (i + 1) % 2

    ax.set_title(f"Elementary Reading Levels by Percentage: Grade {grade}")
    ax.axhline(y = mean_readiness, color = 'b', linestyle = '--')
    ax.legend(loc="upper right")

    plt.xlabel("Zones")
    plt.ylabel("Percentage")
    plt.show()

    return

def main():
    # compare_zones_kindergarten("Interest")
    # kindergarten_zone_rankings("Interest")
    elementary_zone_rankings(5)
    # elem_difference(3, 9, 3, "Reading")

    
if __name__ == '__main__':
    main()

