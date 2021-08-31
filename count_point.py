import numpy as np
import csv
import time
from datetime import datetime

class count_pnt():
    def __init__(self,data_folder,input_file_name):
        # declare objs and set files
        self.data_folder = data_folder
        self.input_file_name = data_folder+input_file_name
        
        self.csv_content = []
        self.read_csv()

        self.counting()

    def read_csv(self):
        csv_pnt = open(self.input_file_name,'r',newline='')
        csv_reader = csv.reader(csv_pnt)

        self.csv_content = [i for i in csv_reader]

    def counting(self):
        width = 4
        in_h = 5
        out_h = 5

        position_arr = np.zeros((width,in_h+out_h))

        pnt_num = 200
        position_arr[1][4] = pnt_num
        position_arr[2][4] = pnt_num

        cnt_route = 0
        cnt_step = 0
        route_arr = []

        route_num = -1
        step_num = -1
        x = -1
        y = -1

        for i in self.csv_content:
            if(i[0] == "route num"):
                continue
            if(route_num != i[0]):
                route_num = i[0]
                cnt_route += 1

            if(i[4]=="-1" or i[5]=="-1" or i[6]=="-1"):
                continue

            x = i[2]
            y = i[3]

            position_arr[round(float(y))][round(float(x))] += 1
            cnt_step += 1
            
        print(position_arr)
        print()
        print("cnt_route: ",cnt_route)
        print("cnt_step: ",cnt_step)
    
c = count_pnt(data_folder = "../data/0828/",input_file_name = "output2.csv")
