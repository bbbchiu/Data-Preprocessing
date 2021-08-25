import numpy as np
import csv
import time

class alignment():
    def __init__(self,imu_file_name,wifi_file_name,gps_file_name):
        # declare objs
        self.wifi_obj = Wifi_data(wifi_file_name)
        self.imu_obj = IMU_data(imu_file_name)
        self.gps_obj = GPS_data(gps_file_name)

        self.data_front_threshold = 2.5
        self.data_back_threshold = 2.5      

        self.total_data = self.get_data_align()

    def get_data_align(self):
        # get wifi array
        self.wifi_time = self.wifi_obj.get_time_arr()
        # get route array
        self.wifi_route = self.wifi_obj.get_route_arr()

        # align sensors
        self.last_route = -1
        self.point_counter = 0
        self.trajectory_counter = 0
        self.point_t_counter = 0

        with open('output.csv', 'w', newline='') as csv_pnt:
            csv_writer = csv.writer(csv_pnt)
            for index,single_time in enumerate(self.wifi_time):
                wifi_content = self.wifi_obj.get_content(index)
                if(wifi_content == -1):
                    continue

                if(self.wifi_route[index] != self.last_route):
                    if(int(self.last_route) != -1 and self.point_t_counter != 0):
                        print("Trajectory: ",self.last_route)
                        print("point nums: ",self.point_t_counter)
                        print("Total trajectory: ",self.trajectory_counter)
                        print("Total point: ",self.point_counter)
                        print()
                        self.point_t_counter = 0
                    self.trajectory_counter += 1
                    self.gps_content = self.gps_obj.get_content_by_route(self.wifi_route[index])
                    self.imu_content = self.imu_obj.get_content_by_route(self.wifi_route[index])
                    self.last_route = self.wifi_route[index]

                if(self.gps_content == None or self.imu_content==None):
                    continue
                self.point_t_counter += 1
                self.total_content = self.get_time_content(single_time)

                if(self.total_content == None):
                    continue

                self.point_counter += 1
                csv_writer.writerow(wifi_content)
                for i in self.total_content:
                    csv_writer.writerow(i)
                csv_writer.writerow(["finish"])
            
    def get_time_content(self,single_time):
        total_content = []
        for i in self.gps_content:
            reply = self.compare_time(single_time,i[self.gps_obj.time_number])
            if reply == None:
                continue
            elif ((reply > 0 and reply <= self.data_front_threshold) or (reply <= 0 and reply >= -self.data_back_threshold)):
                total_content.append(i)
            else:
                pass
        if(len(total_content) == 0):
            return None
        for i in self.imu_content:
            reply = self.compare_time(single_time,i[self.imu_obj.time_number])
            if reply == None:
                continue
            elif ((reply > 0 and reply <= self.data_front_threshold) or (reply <= 0 and reply >= -self.data_back_threshold)):
                total_content.append(i)
            else:
                pass
        if(len(total_content) == 0):
            return None
        return total_content

    def compare_time(self,time_a,time_b):
        try:
            time_a_struct = time.strptime(time_a,"%Y-%m-%d, %H:%M:%S")
            time_b_struct = time.strptime(time_b,"%Y-%m-%d, %H:%M:%S")

            time_a = int(time.mktime(time_a_struct))
            time_b = int(time.mktime(time_b_struct))

            return time_a - time_b

        except:
            return None


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
        try:
            time_a_struct = time.strptime(time_a,"%Y-%m-%d, %H:%M:%S")
            time_b_struct = time.strptime(time_b,"%Y-%m-%d, %H:%M:%S")

            time_a = int(time.mktime(time_a_struct))
            time_b = int(time.mktime(time_b_struct))

            return time_a - time_b

        except:
            return None

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
        try:
            time_a_struct = time.strptime(time_a,"%Y-%m-%d, %H:%M:%S")
            time_b_struct = time.strptime(time_b,"%Y-%m-%d, %H:%M:%S")

            time_a = int(time.mktime(time_a_struct))
            time_b = int(time.mktime(time_b_struct))

            return time_a - time_b

        except:
            return None
          
c = alignment(imu_file_name = "imu_data.csv", gps_file_name = "gps_data.csv", wifi_file_name = "wifi_data.csv")
