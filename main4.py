# Tốc độ của chuyển mạch cứng và tỷ lệ chuyển mạch giữa 2 liên kết FSo và sub-THz
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.set_printoptions(threshold=np.inf)

data_1 = np.load(r'C:\Users\dinhk\Desktop\UAV_FSO_RF_DRL-main\output\speed_10\0\flydata\rate_1200.npy',allow_pickle=True).item()
# data_2 = np.load(r'C:\Users\dohuy\Desktop\Code Aizu\output\speed_10\0\flydata\uav_550.npy',allow_pickle=True).item()
# data_3 = np.load(r'C:\Users\dohuy\Desktop\Code Aizu\output\speed_10\0\flydata\car_550.npy',allow_pickle=True).item()
# data_15 = np.load(r'C:\Users\dohuy\Desktop\Code Aizu\output\speed_15\0\flydata\rate_550.npy',allow_pickle=True).item()


# Đếm số timeslot sử dụng FSO link
count_fso = data_1['count_fso']
column_sums = np.sum(count_fso[:300], axis=0) / 300 * 100 # tính ra phần trăm
print(column_sums)

# Tốc độ của 1 phương tiện
rate = data_1['real_rate']
rate = [arr[2] for arr in rate]
# fso_rate = all_fso_rate
# print(fso_rate)
x = np.arange(len(rate))
y_rate = rate

# Vẽ biểu đồ cột phần trăm sử dụng FSO của 8 phương tiện
# plt.figure(figsize=(8, 6))
# bars = plt.bar(range(1, 6), column_sums, color='b', alpha=0.7)
# # Thêm giá trị phần trăm trên đầu mỗi cột
# for bar in bars:
#     yval = bar.get_height()
#     plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.1f}%', ha='center', va='bottom')
# # Thêm thông tin biểu đồ
# plt.xlabel(" Phương tiện")
# plt.ylabel("Phần trăm sử dụng liên kết FSO")
# plt.title("Tỷ lệ phần trăm các phương tiện sử dụng liên kết chính - FSO")
# plt.xticks(range(1, 6))
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.show()




# Hình Rate của một phương tiện
plt.figure(figsize=(12, 4))
plt.plot(x, y_rate, linestyle='-', color='blue', label='FSO Rate')
plt.title('FSO Rate của phương tiện thứ 5')
plt.xlabel('Timeslot n')
plt.ylabel('Channel Capacity')
plt.legend()
plt.grid()
plt.show()


