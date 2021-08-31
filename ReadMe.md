# get_route.py
## 目標
* 為了生成trajectory轉fingerprint的資料
* input: None
* output: route.csv


# alignment.py
## 目標
* 為了合併turtlebot寫的三個csv檔
* input: gps.csv, imu.csv, wifi.csv
* output: output.csv


# preprocessing.py
## 目標
* 為了將合併的檔案切成一條一條的route
* input: output.csv
* output: output2.csv


# counting.py
## 目標
* 計算目前的route走了那些點多少次
* input: output2.csv
* output: None