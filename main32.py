# Fig: So sánh tốc độ với UAV bay sử dụng chuyển mạch cứng vs mềm
import numpy as np
from matplotlib import pyplot as plt


# Tính tốc độ trung bình cho UAV chuyển mạch cứng
data_HS = np.load(r'C:\Users\dinhk\Desktop\UAV_FSO_RF_DRL-main\output\speed_10\0\flydata\rate_1200.npy', allow_pickle=True).item()
all_rate = data_HS['all_rate']
average_rate_HS = [np.mean(arr) for arr in all_rate]

# Tính tốc độ trung bình cho UAV chuyển mạch mềm
data_SS = np.load(r'C:\Users\dinhk\Desktop\UAV_FSO_RF_DRL-main\output_moder\speed_10\0\flydata\rate_1200.npy', allow_pickle=True).item()
all_rate = data_SS['all_rate']
average_rate_SS = [np.mean(arr) for arr in all_rate]

# Tính tốc độ UAV cung cấp trên giây 
Mbps_HS = np.sum(average_rate_HS) / 300 # Mbps
Mbps_SS = np.sum(average_rate_SS) / 300 # Mbps
print(Mbps_HS, Mbps_SS)

# Vẽ đồ thị
x = np.arange(0, min(len(average_rate_HS), len(average_rate_SS))) 
y1 = average_rate_HS[:len(x)] # UAV di chuyển
y2 = average_rate_SS[:len(x)] # UAV đứng yên

plt.figure(figsize=(12, 6))
plt.plot(x, y1, linestyle='-', color='blue', label='tốc độ nếu sử dụng chuyển mạch cứng')
plt.plot(x, y2, linestyle='-', color='red', label=' Tôc đó nếu sử dụng chuyển mạch mềm')
plt.title('Tốc độ trung bình của 8 phương tiện bay theo thuật toán sử dụng chuyển mạch cứng và chuyển mạch mềm')
plt.xlabel('Timeslot n')
plt.ylabel('Channel Capacity [Mbps]')
plt.legend()
plt.grid()
plt.show()
