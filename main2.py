import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.set_printoptions(threshold=np.inf)

data_1 = np.load(r'C:\Users\dinhk\Desktop\UAV_FSO_RF_DRL-main\output\speed_10\0\flydata\rate_3200.npy',allow_pickle=True).item()
# data_2 = np.load(r'C:\Users\dohuy\Desktop\Code Aizu\output\speed_10\0\flydata\uav_550.npy',allow_pickle=True).item()
# data_3 = np.load(r'C:\Users\dohuy\Desktop\Code Aizu\output\speed_10\0\flydata\car_550.npy',allow_pickle=True).item()
# data_15 = np.load(r'C:\Users\dohuy\Desktop\Code Aizu\output\speed_15\0\flydata\rate_550.npy',allow_pickle=True).item()


# In ra fso_rate của phương tiện 5
all_fso_rate = data_1['real_rate']
fso_rate = [arr[1] for arr in all_fso_rate]
# fso_rate = all_fso_rate
# print(fso_rate)
x = np.arange(len(fso_rate))
y = fso_rate
# Hình FSO Rate của phương tiện thứ 5
plt.figure(figsize=(12, 4))
plt.plot(x, y, linestyle='-', color='blue', label='FSO Rate')
plt.title('FSO Rate của phương tiện thứ 5')
plt.xlabel('Timeslot n')
plt.ylabel('Channel Capacity')
plt.legend()
plt.grid()
plt.show()


# # In ra rf_rate của phương tiện 5
# all_rf_rate = data_1['rf_rate']
# rf_rate = [arr[4] for arr in all_rf_rate]
# # print(rf_rate)
# x = np.arange(len(rf_rate))
# y = rf_rate
# # Hình RF Rate của phương tiện thứ 5
# plt.figure(figsize=(12, 4))
# plt.plot(x, y, linestyle='-', color='red', label='RF Rate')
# plt.title('RF Rate của phương tiện thứ 5')
# plt.xlabel('Timeslot n')
# plt.ylabel('Channel Capacity')
# plt.legend()
# plt.grid()
# plt.show()


# In ra all_rate của phương tiện 5
# all_rf_rate = data_1['all_rate']
# rf_rate = [arr[4] for arr in all_rf_rate]
# # print(rf_rate)
# x = np.arange(len(rf_rate))
# y = rf_rate
# # Hình Rate của phương tiện thứ 5
# plt.figure(figsize=(12, 4))
# plt.plot(x, y, linestyle='-', color='red', label='Total Rate')
# plt.title('Total Rate của phương tiện thứ 5')
# plt.xlabel('Timeslot n')
# plt.ylabel('Channel Capacity')
# plt.legend()
# plt.grid()
# plt.show()


# In ra average rate của tất cả các phương tiện VD_max = 10m/s
# all_rate = data_1['all_rate']
# average_all_rate = [np.mean(arr) for arr in all_rate]
# # print(fso_rate)
# x = np.arange(len(average_all_rate))
# y = average_all_rate
# plt.figure(figsize=(12, 4))
# plt.plot(x, y, linestyle='-', color='blue', label='average rate of all vehicle')
# plt.title('average rate of all vehicle')
# plt.xlabel('Timeslot n')
# plt.ylabel('Channel Capacity')
# plt.legend()
# plt.grid()
# plt.show()


# # In ra average rate của tất cả các phương tiện V_max = 15 m/s
# aerage_all_rate
# ll_rate = data_15['all_rate']
# average_all_rate = [np.mean(arr) for arr in all_rate]
# # print(fso_rate)
# x = np.arange(len(average_all_rate))
# y = av
# plt.figure(figsize=(12, 4))
# plt.plot(x, y, linestyle='-', color='blue', label='Vmax = 15m/s')
# plt.title('average rate of all vehicle')
# plt.xlabel('Timeslot n')
# plt.ylabel('Channel Capacity')
# plt.legend()
# plt.grid()
# plt.show()