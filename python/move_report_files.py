import glob
import shutil

report_files = glob.glob('./data/*.rpt')  # Select all .rpt files

for file in report_files:
    print('Moving ' + file[7:] + ' to /data/report_files')
    shutil.move(file, './data/report_files/' + file[7:])  # Move all .rpt files
