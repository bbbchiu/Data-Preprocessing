import numpy as np
import csv
import time
from datetime import datetime

class alignment():
    def __init__(self,data_folder,imu_file_name,wifi_file_name,gps_file_name,indoor_gps_file_name = None, outdoor_gps_file_name = None):
        # declare objs and set files
        self.data_folder = data_folder
        self.imu_file_name = imu_file_name
        self.wifi_file_name = wifi_file_name
        self.gps_file_name = gps_file_name
        self.indoor_gps_file_name = indoor_gps_file_name
        self.outdoor_gps_file_name = outdoor_gps_file_name

        if(self.indoor_gps_file_name != None):
            self.indoor_gps_obj = GPS_data(self.data_folder+self.indoor_gps_file_name)
        if(self.outdoor_gps_file_name != None):
            self.outdoor_gps_obj = GPS_data(self.data_folder+self.outdoor_gps_file_name)

        self.wifi_obj = Wifi_data(self.data_folder+self.wifi_file_name)
        self.imu_obj = IMU_data(self.data_folder+self.imu_file_name)
        self.gps_obj = GPS_data(self.data_folder+self.gps_file_name)

        # print("data folder: ",self.data_folder)
        # print("imu file: ",self.imu_file_name)
        # print("wifi file: ",self.wifi_file_name)
        # print("gps file: ",self.gps_file_name)
        # print("indoor gps file: ",self.indoor_gps_file_name)
        # print("outdoor gps file: ",self.outdoor_gps_file_name)

        self.data_front_threshold = 0.5
        self.data_back_threshold = 0.5

        self.total_data = self.get_data_align()

    def get_data_align(self):
        # get wifi array
        self.wifi_time = self.wifi_obj.get_time_arr()
        #print(self.wifi_time)
        
        # get route array
        self.wifi_route = self.wifi_obj.get_route_arr()
        #print(self.wifi_route)
   
        # align sensors
        self.last_route = -1
        self.point_counter = 0
        self.trajectory_counter = 0
        self.point_t_counter = 0

        with open(self.data_folder+'output.csv', 'w', newline='') as csv_pnt:
            pass

        for index,single_time in enumerate(self.wifi_time):
            self.wifi_content = self.wifi_obj.get_content(index)
            #print(self.wifi_content)
            
            if(self.wifi_content == -1):
                continue

            if(int(self.wifi_route[index]) > self.last_route):
                if(self.last_route != -1 and self.point_t_counter != 0):
                    self.trajectory_counter += 1
                    print("Trajectory: ",self.last_route)
                    print("point nums: ",self.point_t_counter)
                    print("Total trajectory: ",self.trajectory_counter)
                    print("Total point: ",self.point_counter)
                    print()

                    self.point_t_counter = 1
                    
            if(self.indoor_gps_file_name != None):
                self.indoor_gps_content = self.indoor_gps_obj.get_content_by_route(int(self.wifi_route[index]))
                if(self.indoor_gps_content == None):
                    continue
            else:
                self.indoor_gps_content = None

            if(self.outdoor_gps_file_name != None):
                self.outdoor_gps_content = self.outdoor_gps_obj.get_content_by_route(int(self.wifi_route[index]))
                if(self.outdoor_gps_content == None):
                    continue
            else:
                self.outdoor_gps_content = None

            self.gps_content = self.gps_obj.get_content_by_route(self.wifi_route[index])
            self.imu_content = self.imu_obj.get_content_by_route(self.wifi_route[index])
            self.last_route = int(self.wifi_route[index])

            if(self.gps_content == None or self.imu_content==None):
                continue
            if(self.get_time_content(single_time) == -1):
                continue

            self.point_t_counter += 1
            self.point_counter += 1

        self.trajectory_counter += 1
        print("Trajectory: ",self.last_route)
        print("point nums: ",self.point_t_counter)
        print("Total trajectory: ",self.trajectory_counter)
        print("Total point: ",self.point_counter)
        print()
        self.point_t_counter = 0
            
    def get_time_content(self,single_time):
        with open(self.data_folder+'output.csv', 'a', newline='') as csv_pnt:
            self.csv_writer = csv.writer(csv_pnt)
            self.write_arr = []
            self.write_arr.append(["wifi data"])
            self.write_arr.append(self.wifi_content)
            total_content = []
            for i in self.gps_content:
                reply = self.compare_time(single_time,i[self.gps_obj.time_number])
                if reply == None:
                    continue
                elif ((reply > 0 and reply <= self.data_front_threshold) or (reply <= 0 and reply >= -self.data_back_threshold)):
                    total_content.append(i)
                else:
                    pass
            if(len(total_content) != 0):
                self.write_arr.append(["gps data"])
                for i in total_content:
                    self.write_arr.append(i)
            else:
                #print("gps: ",single_time)
                return -1

            total_content = []
            for i in self.imu_content:
                reply = self.compare_time(single_time,i[self.imu_obj.time_number])
                if reply == None:
                    continue
                elif ((reply > 0 and reply <= self.data_front_threshold) or (reply <= 0 and reply >= -self.data_back_threshold)):
                    total_content.append(i)
                else:
                    pass
            if(len(total_content) != 0):
                self.write_arr.append(["imu data"])
                for i in total_content:
                    self.write_arr.append(i)
            else:
                #print("imu: ",single_time)
                return -1

            total_content = []
            #print(self.indoor_gps_file_name,self.indoor_gps_content)
            if(self.indoor_gps_file_name != None and self.indoor_gps_content != None):
                for i in self.indoor_gps_content:
                    reply = self.compare_time(single_time,i[self.indoor_gps_obj.time_number])
                    if reply == None:
                        continue
                    elif ((reply > 0 and reply <= self.data_front_threshold) or (reply <= 0 and reply >= -self.data_back_threshold)):
                        total_content.append(i)
                    else:
                        pass
                if(len(total_content) != 0):
                    self.write_arr.append(["indoor gps data"])
                    for i in total_content:
                        self.write_arr.append(i)
                else:
                    #print("indoor gps: ",single_time)
                    return -1

            total_content = []
            #print(self.outdoor_gps_file_name,self,outdoor_gps_content)
            if(self.outdoor_gps_file_name != None and self.outdoor_gps_content != None):
                for i in self.outdoor_gps_content:
                    reply = self.compare_time(single_time,i[self.outdoor_gps_obj.time_number])
                    if reply == None:
                        continue
                    elif ((reply > 0 and reply <= self.data_front_threshold) or (reply <= 0 and reply >= -self.data_back_threshold)):
                        total_content.append(i)
                    else:
                        pass
                if(len(total_content) != 0):
                    self.write_arr.append(["outdoor gps data"])
                    for i in total_content:
                        self.write_arr.append(i)
                else:
                    #print("outdoor gps: ",single_time)
                    return -1
            self.write_arr.append(["finish"])

            for i in self.write_arr:
                self.csv_writer.writerow(i)

            return 0

    def compare_time(self,time_a,time_b):        
        time_a_struct = datetime.strptime(time_a,"%Y-%m-%d, %H:%M:%S.%f")
        time_b_struct = datetime.strptime(time_b,"%Y-%m-%d, %H:%M:%S.%f")

        time_a = int(time.mktime(time_a_struct.timetuple())*1000 + time_a_struct.microsecond/1000.0)/1000.0
        time_b = int(time.mktime(time_b_struct.timetuple())*1000 + time_b_struct.microsecond/1000.0)/1000.0

        return time_a - time_b

class Wifi_data():
    def __init__(self,file_name):
        self.file_name = file_name
        self.parameter_declare()

        self.read_csv()

    def parameter_declare(self):
        self.csv_content = []
        self.route_number = 0
        self.content_number = 3
        self.time_number = 4

    def read_csv(self):
        csv_pnt = open(self.file_name,'r',newline='')
        csv_reader = csv.reader(csv_pnt)

        self.csv_content = [i for i in csv_reader]

    def print_csv_content(self):
        print(self.csv_content)

    def get_time_arr(self):
        time_arr = [i[self.time_number] for i in self.csv_content]
        return time_arr

    def get_content(self,index):
        content_arr = [i for i in self.csv_content[index]]
        if content_arr[self.content_number] != "":
            return content_arr
        else:
            return -1

    def get_route_arr(self):
        route_arr = [i[self.route_number] for i in self.csv_content]
        return route_arr


class IMU_data():
    def __init__(self,file_name):
        self.file_name = file_name
        self.parameter_declare()

        self.read_csv()

    def parameter_declare(self):
        self.csv_content = []
        self.route_number = 0
        self.time_number = 12

    def read_csv(self):
        csv_pnt = open(self.file_name,'r',newline='')
        csv_reader = csv.reader(x.replace('\0', '') for x in csv_pnt)

        last_route = -1
        total_content = []
        for i in csv_reader:
            try:
                if(last_route == int(i[self.route_number])):
                    total_content.append(i)
                elif(last_route < int(i[self.route_number])):
                    self.csv_content.append(total_content)
                    last_route = int(i[self.route_number])
                    total_content = [i]
                else:
                    continue
            except:
                continue

    def print_csv_content(self):
        print(self.csv_content)

    def get_content(self,single_time,threshold_f,threshold_b):
        total_content = []
        for i in self.csv_content:
            reply = self.compare_time(single_time,i[self.time_number])
            if reply == None:
                continue
            elif ((reply > 0 and reply <= threshold_f) or (reply <= 0 and reply >= -threshold_b)):
                total_content.append(i)
            else:
                pass
        return total_content

    def get_content_by_route(self,route_num):
        for i in self.csv_content:
            for j in i:
                if (j[self.route_number] != route_num):
                    break
                else:
                    return i

    def compare_time(self,time_a,time_b):
        time_a_struct = datetime.strptime(time_a,"%Y-%m-%d, %H:%M:%S.%f")
        time_b_struct = datetime.strptime(time_b,"%Y-%m-%d, %H:%M:%S.%f")

        time_a = int(time.mktime(time_a_struct.timetuple())*1000 + time_a_struct.microsecond/1000.0)
        time_b = int(time.mktime(time_b_struct.timetuple())*1000 + time_b_struct.microsecond/1000.0)

        return time_a - time_b

class GPS_data():
    def __init__(self,file_name):
        self.file_name = file_name
        self.parameter_declare()

        self.read_csv()

    def parameter_declare(self):
        self.csv_content = []
        self.route_number = 0
        self.time_number = 4

    def read_csv(self):
        try:
            csv_pnt = open(self.file_name,'r',newline='')
            self.csv_reader = csv.reader(x.replace('\0', '') for x in csv_pnt)

            last_route = -1
            total_content = []
            for i in self.csv_reader:
                try:
                    if(last_route == int(i[self.route_number])):
                        total_content.append(i)
                    elif(last_route < int(i[self.route_number])):
                        self.csv_content.append(total_content)
                        last_route = int(i[self.route_number])
                        total_content = [i]
                    else:
                        continue
                except:
                    continue
        except:
            pass

    def print_csv_content(self):
        print(self.csv_content)

    def get_content(self,single_time,threshold_f,threshold_b):
        total_content = []
        for i in self.csv_content:
            reply = self.compare_time(single_time,i[self.time_number])
            if reply == None:
                continue
            elif ((reply > 0 and reply <= threshold_f) or (reply <= 0 and reply >= -threshold_b)):
                total_content.append(i)
            else:
                pass
        return total_content

    def get_content_by_route(self,route_num):
        for i in self.csv_content:
            for j in i:
                if (j[self.route_number] != route_num):
                    break
                else:
                    return i

    def compare_time(self,time_a,time_b):
        time_a_struct = datetime.strptime(time_a,"%Y-%m-%d, %H:%M:%S.%f")
        time_b_struct = datetime.strptime(time_b,"%Y-%m-%d, %H:%M:%S.%f")

        time_a = int(time.mktime(time_a_struct.timetuple())*1000 + time_a_struct.microsecond/1000.0)
        time_b = int(time.mktime(time_b_struct.timetuple())*1000 + time_b_struct.microsecond/1000.0)

        return time_a - time_b
          
c = alignment(data_folder = "../data/0830/", imu_file_name = "imu_data.csv", gps_file_name = "gps_data.csv", wifi_file_name = "wifi_data.csv")
