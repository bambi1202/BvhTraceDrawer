import os
import pandas as pd



path = '0802/'
fileid = 1

hip_sets = []
for file in os.listdir(path):
    file_name = path + file
    # csv_input = pd.read_csv(filepath_or_buffer=path, sep=",")
    # self.readMyCsv(file_name)
    # rename PENG
    os.rename(file_name, (path + str(fileid) + '.bvh'))
    fileid = fileid + 1