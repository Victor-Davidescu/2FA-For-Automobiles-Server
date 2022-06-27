################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import psutil
import time
import csv

LOG_FILE_PATH = 'logs/cpu_memory_usage.csv'

def Main():
    print("Started logging the cpu and memory usage...")
    print("Press CTRL-C to cancel it")

    with open(LOG_FILE_PATH, 'w', newline='') as fileHandler:
        writer = csv.writer(fileHandler)
        writer.writerow(["CPU Usage(%)","Memory Usage(%)"])

        try:
            while True:
                time.sleep(1)
                writer.writerow([psutil.cpu_percent(), psutil.virtual_memory().percent])

        except KeyboardInterrupt: print("Created {0} successfuly.".format(LOG_FILE_PATH))
        fileHandler.close()

################################################################################
#   STARTING POINT
################################################################################
if __name__ == "__main__": Main()
