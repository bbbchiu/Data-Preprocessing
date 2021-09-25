import numpy as np
import csv
import time
from datetime import datetime

class alignment():
    def __init__(self,data_folder,imu_file_name,wifi_file_name,gps_file_name):
        # declare objs and set files
        self.data_folder = data_folder
        self.imu_file_name = imu_file_name
        self.wifi_file_name = wifi_file_name
        self.gps_file_name = gps_file_name

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
          self.csv_writer = csv.writer(csv_pnt)
          self.csv_writer.writerow(["route num","step num","x","y","wifi data","gps data","imu data"])

        self.gps_content = self.gps_obj.get_all_content()

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
            total_content = []

            total_content.append(str(self.wifi_content[0]))  # route num
            total_content.append(str(self.point_t_counter))  # step num
            total_content.append(str(self.wifi_content[1]))  # x
            total_content.append(str(self.wifi_content[2]))  # y
            total_content.append(str(self.wifi_content[3]))  # wifi data

            # GPS
            gps_str = ""
            for index,i in enumerate(self.gps_content):
                reply = self.compare_time(single_time,i[self.gps_obj.time_number])
                if reply == None:
                    continue
                elif ((reply > 0 and reply <= self.data_front_threshold) or (reply <= 0 and reply >= -self.data_back_threshold)):
                    gps_str += i[1]
                    self.gps_content.remove(i) # not allow overlap
                elif ((reply <= 0 and reply < -self.data_back_threshold)):
                  break
                else:
                    pass

            if (gps_str != ""):
                total_content.append(gps_str)
            else:
                #print("gps: ",single_time)
                return -1

            # IMU
            mag_arr = [0,0,0]
            cnt = 0
            for i in self.imu_content:
                reply = self.compare_time(single_time,i[self.imu_obj.time_number])
                if reply == None:
                    continue
                elif ((reply > 0 and reply <= self.data_front_threshold) or (reply <= 0 and reply >= -self.data_back_threshold)):
                    mag_arr[0] += float(i[9])
                    mag_arr[1] += float(i[10])
                    mag_arr[2] += float(i[11])
                    cnt += 1
                elif ((reply <= 0 and reply < -self.data_back_threshold)):
                  break
                else:
                    pass
            if (cnt != 0):
                mag_arr = [str(i/cnt) for i in mag_arr]
                total_content.append(mag_arr)
            else:
                #print("imu: ",single_time)
                return -1

            self.write_arr.append(total_content)
            total_content = []

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
        csv_pnt = open(self.file_name,'r',newline='', encoding='utf-8')
        csv_reader = csv.reader(csv_pnt)

        #self.csv_content = [i for i in csv_reader]
        self.csv_content = []
        try:
            for index,i in enumerate(csv_reader):
                self.csv_content.append(i)
        except:
            pass
            #print(index)
            #print(i)

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
        self.time_number = 0

    def read_csv(self):
        try:
            csv_pnt = open(self.file_name,'r',newline='')
            self.csv_reader = csv.reader(x.replace('\0', '') for x in csv_pnt)
            for i in self.csv_reader:
                self.csv_content.append(i)
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

    def get_all_content(self):
        return self.csv_content

    def compare_time(self,time_a,time_b):
        time_a_struct = datetime.strptime(time_a,"%Y-%m-%d, %H:%M:%S.%f")
        time_b_struct = datetime.strptime(time_b,"%Y-%m-%d, %H:%M:%S.%f")

        time_a = int(time.mktime(time_a_struct.timetuple())*1000 + time_a_struct.microsecond/1000.0)
        time_b = int(time.mktime(time_b_struct.timetuple())*1000 + time_b_struct.microsecond/1000.0)

        return time_a - time_b
          
