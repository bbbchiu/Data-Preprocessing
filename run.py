from gps_preprocessing import GNSSlogger_transfer
from alignment import alignment

if __name__ == '__main__':
    print("\nStart GPS preprocessing~\n")
    #g = GNSSlogger_transfer(input_folder_path = "../data/0913/gnss_log/",output_folder_path = "../data/0913/",file_arr =["1.txt"])

    print("Start Alignment~\n")
    c = alignment(data_folder = "../data/0913/", imu_file_name = "imu_data.csv", gps_file_name = "gps_data.csv", wifi_file_name = "wifi_data.csv")

    print("Done~\n")


