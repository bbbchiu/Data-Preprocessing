import numpy as np
import random
import math
import time
import csv

class route_generator():
    def __init__(self,width = 5,indoor_height = 5,outdoor_height = 5):
        self.width = width
        self.indoor_height = indoor_height
        self.outdoor_height = outdoor_height
        self.route_setting()

    def route_setting(self):
        self.route_min_step = 10
        self.route_max_step = 21
        self.bfs_route_arr = []
        self.route_step = []
        self.start_pnt = [0,0]
        self.end_pnt = [0,0]
        self.total_height = self.indoor_height+self.outdoor_height
        self.map_size = (self.total_height,self.width)
        self.route_out_arr = []
        self.warning_indoor_x = 4        
        self.warning_outdoor_x = 5
        self.warning_x = self.warning_indoor_x

    def gen_point(self):
        x = random.randint(0,self.total_height-1)
        y = random.randint(0,self.width-1)
        z = random.randint(0,3)
        if(z == 0):
            x = 0
        elif(z==1):
            x = self.total_height-1
        elif(z==2):
            y = 0
        else:
            y = self.width -1
        return [x,y]

    def gen_route(self):
        # generate start point and end point
        self.start_pnt = [0,0]
        self.end_pnt = [0,0]
        distance = 3

        # get rid of distance less than distance
        while(self.get_pnt_distance(self.start_pnt,self.end_pnt) < distance or self.start_pnt == self.end_pnt):
            self.start_pnt = self.gen_point()
            self.end_pnt = self.gen_point()

        # print("start_pnt: ",self.start_pnt)
        # print("end_pnt: ",self.end_pnt)
        # print()

#        print("warning_indoor_x: ",self.warning_indoor_x)
#        print("warning_outdoor_x: ",self.warning_outdoor_x)
#        print()

        route_step = []
        rand_dir = random.randint(0,1)
#        print("rand_dir: ",rand_dir)
#        print()

        temp_step_arr = []
        step_arr = [self.start_pnt]
        if(self.start_pnt[rand_dir] > self.end_pnt[rand_dir]):
            for i in range(self.end_pnt[rand_dir],self.start_pnt[rand_dir]+1):
                if(rand_dir == 0):
                    # if(i==self.warning_indoor_x or i == self.warning_outdoor_x):
                    #     continue
                    # else:
                    temp_step_arr.append([i,random.randint(0,self.width-1)])
                else:
                    # x = self.warning_x
                    # while(x==self.warning_x):
                    x = random.randint(0,self.total_height-1)
                    temp_step_arr.append([x,i])
            temp_step_arr.reverse()
        else:
            for i in range(self.start_pnt[rand_dir],self.end_pnt[rand_dir]+1):
                if(rand_dir == 0):
                    # if(i==self.warning_indoor_x or i == self.warning_outdoor_x):
                    #     continue
                    # else:
                    temp_step_arr.append([i,random.randint(0,self.width-1)])
                else:
                #     x = self.warning_x
                #     while(x==self.warning_x):
                    x = random.randint(0,self.total_height-1)
                    temp_step_arr.append([x,i])

        if(len(temp_step_arr)>1):
            step_arr.extend(temp_step_arr[1:len(temp_step_arr)-1])
        else:
            step_arr.extend(temp_step_arr)   

        step_arr.append(self.end_pnt)         
        for i in step_arr:
            if((i[0]==4 and i[1] ==1) or ((i[0]==4 and i[1] ==2))):
               # print("hit")
                step_arr.remove(i)

        #return step_arr
#        print("temp step arr: ",temp_step_arr)
        #print("step arr: ",step_arr)
#        print()

        rand_dir = random.randint(0,1)
  #      print("rand_dir: ",rand_dir)
  #      print()

        route_arr = [step_arr[0]]
        current_step = step_arr[0]

        dis_cnt = 0
        last_pnt = -1
        for i in step_arr:
            if(last_pnt == -1):
                last_pnt = i
                continue
            dis_cnt += self.get_pnt_distance(i,last_pnt)
            last_pnt = i
        #print("dis_cnt: ",dis_cnt)

        if(rand_dir): # 1 -> left/right
            for i in step_arr[1:]:
                while(current_step[0]!=i[0]):
                    if(current_step[0] > i[0]):
                        current_step = [current_step[0]-1,current_step[1]]
                    else:
                        current_step = [current_step[0]+1,current_step[1]]
                    route_arr.append(current_step)
                while(current_step[1]!=i[1]):
                    if(current_step[1] > i[1]):
                        current_step = [current_step[0],current_step[1]-1]
                    else:
                        current_step = [current_step[0],current_step[1]+1]
                    route_arr.append(current_step)
        else: # 0 -> up/down
            for i in step_arr[1:]:
                while(current_step[1]!=i[1]):
                    if(current_step[1] > i[1]):
                        current_step = [current_step[0],current_step[1]-1]
                    else:
                        current_step = [current_step[0],current_step[1]+1]
                    route_arr.append(current_step)
                while(current_step[0]!=i[0]):
                    if(current_step[0] > i[0]):
                        current_step = [current_step[0]-1,current_step[1]]
                    else:
                        current_step = [current_step[0]+1,current_step[1]]
                    route_arr.append(current_step)

        for i in route_arr:
            if((i[0]==4 and i[1] ==1) or ((i[0]==4 and i[1] ==2))):
               # print("hit")
                route_arr.remove(i)
        return route_arr

    def inBoundary(self,pnt):
        if(pnt[0] < self.total_height and pnt[0]>=0 and pnt[1]>=0 and pnt[1]< self.width):
            return True
        else:
            return False
        
    def get_pnt_distance(self,pnt1,pnt2):
        return math.sqrt(pow(pnt1[0]-pnt2[0],2)+pow(pnt1[1]-pnt2[1],2))

if __name__ == "__main__":
    width = 4
    in_h = 5
    out_h = 5
    r = route_generator(width=width,indoor_height=in_h,outdoor_height=out_h)

    position_arr = np.zeros((width,in_h+out_h))

    pnt_num = 200
    position_arr[1][4] = pnt_num
    position_arr[2][4] = pnt_num

    cnt_route = 0
    route_arr = []

    while(np.min(position_arr) < pnt_num):
        # print(position_arr)
        # print()
        # time.sleep(0.5)
        route = r.gen_route()
        for i in route:
            if((i[0]==4 and i[1]==1) or (i[0]==4 and i[1]==2)):
                try:
                    route.index([4,1])
                    break
                except ValueError:
                    pass

                try:
                    route.index([4,2])
                    break
                except ValueError:
                    pass
                
            position_arr[i[1]][i[0]] += 1
        #break
        route_arr.append(route)
        cnt_route += 1

    with open('../data/route.csv', 'w', newline='') as csv_pnt:
        csv_writer = csv.writer(csv_pnt)
        for index,i in enumerate(route_arr):
            temp = []
            for j in i:
                temp.append([j[0],j[1]])
            csv_writer.writerow(temp)

    print("cnt_route: ",cnt_route)
    print(position_arr)
