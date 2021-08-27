import numpy as np
import csv
import time

class preprocessing():
    def __init__(self,data_folder,input_file_name):
        # declare objs
        self.data_folder = data_folder
        self.file_name = self.data_folder + input_file_name

        self.specific_keyword = ["wifi data","gps data","imu data","indoor gps data","outdoor gps data"]
        self.csv_content = []
        self.read_csv()

        self.cut_trajectory()
        self.data_combine()
        self.write_output_file()

    def read_csv(self):
        csv_pnt = open(self.file_name,'r',newline='')
        csv_reader = csv.reader(csv_pnt)

        self.csv_content = [i for i in csv_reader]

    def print_csv_content(self):
        for i in self.csv_content:
            print(i)

    def cut_trajectory(self):
        self.cut_route_arr = []
        self.cnt_route_pnt_arr = []
        temp_arr = []
        out_arr = []
        self.cutting_threshold = 7
        last_route = -1
        pnt_a_route = 0

        for i in self.csv_content:
            specific_flag = False
            for j in self.specific_keyword:
                if(i[0] == j):
                    specific_flag = True
                if(specific_flag):
                    break
            if(specific_flag):
                temp_arr.append(i)
                continue

            if(i[0] == "finish"):
                pnt_a_route += 1
                temp_arr.append(i)
                continue

            if(int(i[0]) != last_route):
                if(last_route == -1):
                    last_route = int(i[0])
                elif(int(i[0]) == -1):
                    pass
                else:
                    #[print(i) for i in temp_arr]
                    self.cnt_route_pnt_arr.append([last_route,pnt_a_route])
                    if(pnt_a_route < self.cutting_threshold):
                        self.cut_route_arr.append(last_route)
                    else:
                        out_arr += temp_arr
                    temp_arr = []
                    pnt_a_route = 0
                    last_route = int(i[0])
            temp_arr.append(i)

        print(self.cnt_route_pnt_arr)
        self.csv_content = out_arr

    def data_combine(self):
        route_num = -1
        step_num = 1
        last_route = -1
        wifi_final_data = -1
        gps_final_data = []
        imu_final_data = -1
        indoor_gps_final_data = []
        outdoor_gps_final_data = []
        self.output_arr = []

        wifi_flag = False
        gps_flag = False
        imu_flag = False
        indoor_gps_flag = False
        outdoor_gps_flag = False

        self.output_arr.append(["route num","step num","wifi data","gps data","imu data","indoor gps data","outdoor gps data"])
        for i in self.csv_content:
            if(i[0] == "wifi data"):
                wifi_flag = True
                gps_flag = False
                imu_flag = False
                indoor_gps_flag = False
                outdoor_gps_flag = False
                continue
            elif(i[0] == "gps data"):
                wifi_flag = False
                gps_flag = True
                imu_flag = False
                indoor_gps_flag = False
                outdoor_gps_flag = False
                continue
            elif(i[0] == "imu data"):
                wifi_flag = False
                gps_flag = False
                imu_flag = True
                indoor_gps_flag = False
                outdoor_gps_flag = False
                continue
            elif(i[0] == "indoor gps data"):
                wifi_flag = False
                gps_flag = False
                imu_flag = False
                indoor_gps_flag = True
                outdoor_gps_flag = False
                continue
            elif(i[0] == "outdoor gps data"):
                wifi_flag = False
                gps_flag = False
                imu_flag = False
                indoor_gps_flag = False
                outdoor_gps_flag = True
                continue
            elif(i[0] == "finish"):
                self.output_arr.append([route_num,step_num,wifi_final_data,gps_final_data,imu_final_data,indoor_gps_final_data,outdoor_gps_final_data])
                wifi_final_data = -1
                gps_final_data = []
                imu_final_data = -1
                indoor_gps_final_data = []
                outdoor_gps_final_data = []
                step_num += 1
                continue
            else:
                pass

            if(int(i[0]) != last_route):
                if(int(i[0]) == -1):
                    pass
                elif(last_route == -1):
                    last_route = int(i[0])
                    route_num = int(i[0])
                else:
                    route_num = int(i[0])
                    last_route = int(i[0])
                    step_num = 1
            
            if(wifi_flag):
                wifi_final_data = i[3]
                #print(wifi_final_data)
            if(gps_flag):
                gps_final_data.append(i[3])
                #print(gps_final_data)
            if(imu_flag):
                imu_final_data = -1
                #print(imu_final_data)
            if(indoor_gps_flag):
                indoor_gps_final_data.append(i[3])
                #print(indoor_gps_final_data)
            if(outdoor_gps_flag):
                outdoor_gps_final_data.append(i[3])
                #print(outdoor_gps_final_data)

    def write_output_file(self):
        with open(self.data_folder+'output2.csv', 'w', newline='') as csv_pnt:
            self.csv_writer = csv.writer(csv_pnt)
            for i in self.output_arr:
                self.csv_writer.writerow(i)

          
c = preprocessing(data_folder = "../data/0823/",input_file_name = "output.csv")
