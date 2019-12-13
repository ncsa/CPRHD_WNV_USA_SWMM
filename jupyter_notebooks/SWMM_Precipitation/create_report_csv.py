import glob
import csv
import re

daily_reports = sorted(glob.glob('./daily/simulation_files/dry_only_test/*.rpt'))
hourly_reports = sorted(glob.glob('./hourly/simulation_files/dry_only_test/*.rpt'))
prism_reports = sorted(glob.glob('./prism/simulation_files/dry_only_test/*.rpt'))

variables = ['Total Precipitation', 'Evaporation Loss', 'Surface Runoff', 'Infiltration Loss', 'Final Storage', 'Continuity Error']

csv_file = csv.writer(open('./dry_only_report.csv', 'w'))

for daily, hourly, prism in zip(daily_reports, hourly_reports, prism_reports):
    daily_file = open(daily, 'r')
    hourly_file = open(hourly, 'r')
    prism_file = open(prism, 'r')

    # Format the name of the report file
    name = daily[daily.rfind('/')+1:daily.rfind('_')]
    name = name[:name.rfind('_')]
    name = name[0].upper() + name[1:]

    csv_file.writerow([name, '3-Hourly', 'Daily', 'PRISM'])

    # Exit when we hit the first 'Continuity Error' because there are multiple in the report file
    done = False

    for daily_line, hourly_line, prism_line in zip(daily_file, hourly_file, prism_file):
        for var in variables:
            if var in daily_line and not done:
                first_int = re.search('\d', daily_line).start(0)

                daily_line = daily_line[first_int:first_int + 6]
                hourly_line = hourly_line[first_int:first_int + 6]
                prism_line = prism_line[first_int:first_int + 6]

                csv_file.writerow([var, hourly_line, daily_line, prism_line])

                if var == 'Continuity Error':
                    done = True
    csv_file.writerow([])
    csv_file.writerow([])
