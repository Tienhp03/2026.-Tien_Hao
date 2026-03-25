# Fig: So sánh tốc độ với UAV đứng yên - chuyển mạch cứng và mềm
import numpy as np
from matplotlib import pyplot as plt
from arg_data import CarsPath
from channel import get_thz_gain, get_fso_gain, power_distribute

# Khởi tạo dữ liệu
np.random.seed(20205598)
car_speed = 10
car_force = 5
car_num = 5
uav_height = 100
total_time = 300
thz_power = 15  # in dBm each
fso_power = 15  # in dBm each aver
target_rate = 1400

CarsPath = CarsPath()
temp_car_init_pos = CarsPath.load(car_speed, car_force, car_num)
uav_pos = np.array([0, 0, uav_height]) # vị trí cố định của UAV tại trung tâm
# uav_pos = np.mean(temp_car_init_pos, axis=0) + np.array([0, 0., uav_height])
r_all_fix = []

# Tính toán r_all cho UAV cố định
for time in range(total_time):
    inter_index, cars_pos_list, distance = CarsPath.get_inter_distance(time=time, point=uav_pos)
    # print (distance)
    cars_pos_list = np.array(cars_pos_list)
    h_fso = get_fso_gain(inter_index, uav_pos, distance, cars_pos_list)
    h_thz = get_thz_gain(inter_index, uav_pos, cars_pos_list, distance)
    # print(np.sqrt(h_thz))

    # p_thz_max = thz_power + 10 * np.log10(car_num)
    p_thz_max = thz_power 
    # p_fso_max = fso_power * np.ones(shape=(car_num,))
    p_fso_max = fso_power  
    # thay chuyển mạch cứng và chuyển mạch mềm
    rate, fso_rate, thz_rate, real_rate, count_fso, count_thz = power_distribute(p_thz=p_thz_max, h_thz=h_thz, 
                                                p_fso=p_fso_max, h_fso=h_fso, 
                                                target_rate=target_rate)
    # print(fso_rate)
    r_all_fix.append(fso_rate)
    # Đếm số lần sử dụng FSO
    print(count_fso)


r_all = np.array(r_all_fix) 
# print(r_all)
# tính tốc độ trung bình của UAV fix
average_rate_FixUAV = [np.mean(arr) for arr in r_all]


# Tính tốc độ trung bình cho UAV di chuyển
# data_NotFixUAV = np.load(r'C:\Users\dohuy\Desktop\UAV_FSO_THz\UAV_FSO_RF_DRL-main\output 2.6 gbps SS\speed_10\4\flydata\rate_2600.npy', allow_pickle=True).item()
# all_rate = data_NotFixUAV['all_rate']
# average_rate_NotFix = [np.mean(arr) for arr in all_rate]

# Vẽ đồ thị
x = np.arange(0, min(len(average_rate_FixUAV), len(average_rate_FixUAV))) 
# y1 = average_rate_NotFix[:len(x)] # UAV di chuyển
y2 = average_rate_FixUAV[:len(x)] # UAV đứng yên
# Vẽ đồ thị
plt.figure(figsize=(12, 6))
# plt.plot(x, y1, linestyle='-', color='blue', label='UAV bay theo thuật toán')
plt.plot(x, y2, linestyle='-', color='red', label='UAV đứng yên')
plt.title('So sánh tốc độ dữ liệu UAV cung cấp khi bay theo thuật toán và đứng yên')
plt.xlabel('Timeslot n')
plt.ylabel('Channel Capacity [Mbps]')
plt.legend()
plt.grid()
plt.show()
