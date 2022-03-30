# Realizable Accessibility: Evaluating the Reliability of Public Transit Accessibility using High-resolution Real-time Data 
 
This repository hosts the scripts of the paper "Realizable Accessibility: Evaluating the Reliability of Public Transit Accessibility using High-resolution Real-time Data". 

## Abstract
The widespread availability of high spatial and temporal resolution public transit data is improving the measurement and analysis of public transit-based accessibility to crucial community resources such as jobs and healthcare. A common approach is leveraging transit route and schedule data published by transit agencies.  However, this often results in accessibility overestimations due to endemic delays due to traffic and incidents in bus systems.   Retrospective real-time accessibility measures calculated using real-time bus location data attempt to reduce overestimation by capturing the actual performance of the transit system. These measures also overestimate accessibility since they assume that riders had perfect information on systems operations as they occurred.  In this paper, we introduce realizable real-time accessibility based on space-time prisms (STP) as a more conservative and realistic measure. We moreover define accessibility unreliability to measure overestimation of schedule-based and retrospective accessibility measures. Using high-resolution General Transit Feed Specification (GTFS) real-time data, we conduct a case study in the Central Ohio Transit Authority (COTA) bus system in Columbus, Ohio, USA. Our results prove that realizable accessibility is the most conservative of the three accessibility measures. We also explore the spatial and temporal patterns in the unreliability of both traditional measures.  These patterns are consistent with prior findings of the spatial and temporal patterns of bus delays and risk of missing transfers. Realizable accessibility is a more practical, conservative, and robust measure to guide transit planning.

## Scripts
All scripts that are used to generate results for the paper are stored in /scr folder. Below I describe what each script is for.

- BasicSolver.py: the parent class that contains all methods and data structure to sustain the computation.
- transfer_tools.py: obselete script that serves the same purposes as BasicSolver but for non-OOP programming. 
- DijkstraSolver.py: routing engine based on time-dependent Dijkstra algorithm. The results include scheduled-based and retrospective-based (see Wessel, N., & Farber, S. (2019)) travel time.
- RevisitSolver.py: after getting the schedule-based and retrospective-based travel time, this script will revisit the schedule-based route with actual real-time timetable. Find the paper for more information.

The input data are feeded from a MongoDB database, including col_stop_time and col_stops in DijkstraSolver.py. These data are preprocessed by me from GTFS static and GTFS real-time trip update. Find scripts in /gtfs_realtime in [this repository](https://github.com/luyuliu/data) to process the data.

The output is a record-based OD matrix; each record has origin stop(*startStopID*), destination stop (*receivingStopID*), prior stop just before the destination stop (generatingStopID), and different time. There are three travel times; SC means scheduled, RT means retrospective real-time, and RV means realizable real-time.

- /scr/analysis: the scripts to generate space-time prisms for different scenarios.
- /scr/geoanalysis: the scripts to generate maps. Includes some arcpy codes.
- /scr/timeanalysis: the scripts to generate temporal analyses, including daily, hourly, and days of week.



Reference:
Wessel, N., & Farber, S. (2019). On the accuracy of schedule-based GTFS for measuring accessibility. Journal of Transport and Land Use, 12(1), 475-500.
