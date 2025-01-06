f_count1 = 1000000   # number of rows in fact tables for the first data set
f_count2 = 100000   # number of rows in fact tables for the second data set

center_count = 1000     # number of rows in ski centers dimension table in both data sets

c_count1 = 50000    # number of rows in clients dimension table for the first data set
c_count2 = 5000     # number of rows in clients dimension table for the second data set
c_sample_size = 2000    # number of randomly chosen rows in clients dimension table
# from first data set that will appear in the second

g_count1 = 100000   # number of rows in gear dimension table for the first data set
g_count2 = 10000    # number of rows in gear dimension table for the second data set
g_sample_size = 5000    # number of randomly chosen rows in gear dimension table
# from first data set that will appear in the second

start_year = 2023
start_month = 1
start_day = 1

periods1 = 10   # number of periods into which the first data set will be divided
periods2 = 2   # number of periods into which the second data set will be divided

span1 = 30  # number of days each period will span in the first data set
span2 = 30  # number of days each period will span in the second data set

suffix1 = 'T1'  # suffix for csv files' filenames for the first data set
suffix2 = 'T2'  # suffix for csv files' filenames for the second data set

id_length = 9   # length of generated ids
