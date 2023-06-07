# OUSD-Literacy-Disparities

OUSD Literacy Analysis
Ahmed Muhammad | 6.6.2023

I created this code in order to analyze literacy data from
the Oakland Unified School District (OUSD). The goal of this 
project is to use a data-driven approach to determine if there
exists differences in educational outcomes in Oakland that 
are correlated with school zone (which are associated with race,
class, education level, life expectancy, and more).

The main functions to interact with are:

k_difference(zone1, zone2, parameter)
The parameters zone1 and zone2 can be any of the 15 zones, which are labeled
1-15. The parameter is a string that is either "Advanced Literacy", "Basic Literacy",
or "Interest". (Note: code also includes Basic Numeracy, but I have not been able to
access the data for this yet).

compare_zones_kindergarten(parameter)
The parameters are the same: "Advanced Literacy", "Basic Literacy", or "Interest". This code will compare all possible pairings of school zones and determine which zones have signficant statistical difference (using the method of bootstrapping that I learned fromCS 109!).

elem_difference(zone1, zone2, grade, parameter)
This is the elementary school version of k_difference. It compares elementary literacy rates
across two specified zones. The parameter is "Reading" (I haven't included math data yet).

kindergarten_zone_rankings(parameter)
Given a specific parameter ("Advanced Literacy", "Basic Literacy", or "Interest"), the program will visualize all of the zones and graph them in a stacked bar plot.

elementary_zone_rankings(grade)
Given a specific grade (3, 4, or 5) the program will visualize all of the zones and graph their corresponding literacy rates in a stacked bar plot.
