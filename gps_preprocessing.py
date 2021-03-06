import numpy as np
import pandas as pd
import os
import glob
from datetime import datetime
import csv
import time

class GNSSlogger_transfer():
    def __init__(self,file_pnt,input_folder_path,output_folder_path,file_arr):
        self.folder_path = output_folder_path
        with open(output_folder_path+'gps_data.csv', file_pnt, newline='') as csv_pnt:
            pass

        for i in file_arr:
            self.write_csv(input_folder_path+i)

    def write_csv(self,file_path):
        f = open(file_path)
        data = f.readlines()
        f.close()

        rawlist = []
        get_time = []
        for i in range(len(data)):
            if data[i].find('Raw') != -1 and data[i].find('# Raw')==-1 :
                rawlist.append(i)
                get_time.append((float(data[i].split(',')[2]) - float(data[i].split(',')[5]))*1e-6)

        with open(self.folder_path+'gps_data.csv', 'a', newline='') as csv_pnt:
            csv_writer = csv.writer(csv_pnt)
            
            for index, i in enumerate(get_time):
                time_out = self.gps2utc(i)[0]
                time_str = str(int(time_out[0]))+"-"+str(int(time_out[1]))+"-"+str(int(time_out[2]))+", "+str(int(time_out[3]))+":"+str(int(time_out[4]))+":"+str(round(time_out[5],3))
                data[rawlist[index]] = "".join(data[rawlist[index]].split('\r\n'))
                temp = [time_str,data[rawlist[index]]]
                csv_writer.writerow(temp)

    def JulianDay(self,time_temp):
        y = time_temp[0]
        m = time_temp[1]
        d = time_temp[2]
        h = time_temp[3] + time_temp[4]/60 + time_temp[5]/3600
        if m<=2: #index into months <=2
            m = m + 12
            y = y - 1
        return np.floor(365.25*y) + np.floor(30.6001*(m+1)) -15 + 1720996.5 + d + h/24

    def LeapSeconds(self,utcTime):
        utcTable = [[1982, 1, 1, 0, 0, 0],
                [1982, 7, 1, 0, 0, 0],
                [1983, 7, 1, 0, 0, 0],
                [1985, 7, 1, 0, 0, 0],
                [1988, 1, 1, 0, 0, 0],
                [1990, 1, 1, 0, 0, 0],
                [1991, 1, 1, 0, 0, 0],
                [1992, 7, 1, 0, 0, 0],
                [1993, 7, 1, 0, 0, 0],
                [1994, 7, 1, 0, 0, 0],
                [1996, 1, 1, 0, 0, 0],
                [1997, 7, 1, 0, 0, 0],
                [1999, 1, 1, 0, 0, 0],
                [2006, 1, 1, 0, 0, 0],
                [2009, 1, 1, 0, 0, 0],
                [2012, 7, 1, 0, 0, 0],
                [2015, 7, 1, 0, 0, 0],
                [2017, 1, 1, 0, 0, 0]
            ]
        tableJDays=[]
        GPSEPOCHJD = 2444244.5
        DAYSEC = 86400
        for ut in utcTable:
            tableJDays.append(self.JulianDay(ut)- GPSEPOCHJD)
        tableSeconds = np.array(tableJDays) * DAYSEC
        jDays = []
        for ut in utcTime:
            jDays = self.JulianDay(ut)- GPSEPOCHJD
        timeSeconds = np.array(jDays)*DAYSEC
        leapSecs= np.zeros(1)
        return np.sum(timeSeconds>=tableSeconds)

    def Fct2Ymdhms(self,svtest): 
        HOURSEC = 3600
        MINSEC = 60
        monthDays=[31,28,31,30,31,30,31,31,30,31,30,31]
        DAYSEC = 86400
        days = np.array(np.floor(svtest/DAYSEC)+6)
        years = np.zeros([days.size])+1980
        leap = np.ones([days.size])
        time_temp  = np.zeros([days.size,6])
        while((days > leap+365).any()):
            I = np.where(days > (leap+365),1,0)
            days = days - I * (leap + 365)
            years =years + I
            leap = leap*(1-I) + np.where(years%4 == 0,1,0)
        time_temp[:,0] = years
        
        for i in range(days.size):
            month = 1
            if (years[i]%4 == 0):  #This works from 1901 till 2099
                monthDays[1]=29 #Make February have 29 days in a leap year
            else:
                monthDays[1]=28
            while (days[i] > monthDays[month]):
                days[i] = days[i]-monthDays[month-1]
                month = month+1
                if month == 12:
                    break
            time_temp[i,1] = month
        
        time_temp[:,2] = days
        sinceMidnightSeconds = svtest % DAYSEC
        time_temp[:,3] = np.floor(sinceMidnightSeconds/HOURSEC) - 7
        lastHourSeconds = sinceMidnightSeconds % HOURSEC
        time_temp[:,4] = np.floor(lastHourSeconds/MINSEC)
        time_temp[:,5] = lastHourSeconds%MINSEC
        return time_temp

    def gps2utc(self,allRxMills):
        svtest = 1e-3*np.array(allRxMills)
        time_temp = self.Fct2Ymdhms(svtest)
        ls = self.LeapSeconds(time_temp)
        timeMLs = self.Fct2Ymdhms(svtest-ls)
        ls1 = self.LeapSeconds(timeMLs)
        if (ls1==ls):
            utcTime = timeMLs
        else:
            utcTime = self.Fct2Ymdhms(fctSeconds-ls1)
        return utcTime