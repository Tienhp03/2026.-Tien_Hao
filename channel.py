import numpy as np
import math
from scipy import optimize, special
import scipy.integrate as integrate


def fso_eqn(x):
    return 1 / x - np.exp(-x) / (1 - np.exp(-x)) - fso_intensity_alpha_ratio


# FSO channel
fso_path_coe = {'clear_air':0.43e-3, 'haze': 4.3e-3, 'light_fog': 20e-3, 'moderate_fog': 42.2e-3, 'heavy_fog':125e-3}
# fso_visibility = 0.5  # km
fso_cloud_vertical = 0.01 # km
CLWC = 10 ** -3 # g/m3
N_c = 0.25 # cloud droplet number concentration (m3)
fso_ref_visibility = 550  # nm
fso_transmission_wavelength = 1550  # nm
fso_C_0_2 = 1e-14  # m^(-2/3)
fso_point_loss_omega_0 = 0.25e-3
fso_receiver_r = 10e-2
fso_gain1= 0 # dBi
fso_gain2 = 0
wind_speed = 20 # m
# the center of the beam footprint is outside the receiver lens in m
fso_receiver_u = 14e-2
fso_intensity_alpha_ratio = 0.25
fso_unique_mu = optimize.fsolve(fso_eqn, np.array([1]))[0]
# On the Capacity of Free-Space Optical Intensity Channels
# when FSO_ALPHA --> (0, 0.5)
if 0 < fso_intensity_alpha_ratio < 0.5:
    fso_k1 = np.exp(2 * fso_intensity_alpha_ratio * fso_unique_mu) / (2 * np.pi * np.exp(1)) \
             * ((1 - np.exp(-fso_unique_mu) / fso_unique_mu) ** 2) / fso_intensity_alpha_ratio ** 2
# when FSO_ALPHA --> [0.5, 1]
elif 0.5 <= fso_intensity_alpha_ratio <= 1:
    fso_k1 = 1 / (2 * np.pi * np.exp(1)) / fso_intensity_alpha_ratio ** 2
# fso_power = 10  # dBm allowed average-power
fso_bandwidth = 200  # MHz
# fso_noise =  -174 + np.log10(fso_bandwidth * 10^6)  # dBm
fso_noise = -30# dBm/Hz

# sub-THz channel
THz_vehicle_gain = 47 # dBi
THz_UAV_gain = 47 # dBi
THz_frequency = 120e9 # Hz
THz_bandwidth = 100 # MHz 
# THz_noise = -174 + np.log10(THz_bandwidth * 10^6) # dBm/Hz
THz_noise = -30 # dBm/Hz
THz_cloud_vertical = 0.01 # km
THz_divergence = 0.3 * 10 ** (-3) # rad
THz_detector_radius = 0.1 # m
THZ_fading_alpha = 2
THz_fading_gamma = 6 
rf_eta_los = 0.1  # dB
rf_eta_nlos = 21  # dB
rf_rician_K_db = 15  # dB

# Other Parametter
vehicle_nums = 5
cars_height = 2 # m
uav_height = 100 # m
light_speed = 3e8 # tốc độ ánh sáng
target_BER = 10 ** -6

def get_fso_gain(nlos_flag: bool, uav_pos: np.ndarray, distance: np.ndarray, car_pos: np.ndarray) -> np.ndarray:

    shape = distance.shape
    # 1. Atmospheric loss (h_l)
    h_l = 10 ** (-fso_path_coe['light_fog'] * distance * 0.1)


    # 2. Cloud attenuation (h_c)
    q = 0 # sự phân bổ kích thước của các hạt tán xạ (Kim model)
    fso_visibility = 1002 / (CLWC * N_c) ** 0.6473
    cloud_coefficient = (3.91 / fso_visibility) * (fso_transmission_wavelength / 550) ** q # dB/km
    h_c = np.exp(-cloud_coefficient * fso_cloud_vertical)

    # 3. Atmospheric turbulence Fading (h_f)
    # Tính góc Zenith (phi_beam_z)
    r_dis = np.linalg.norm(car_pos[:, 0:-1] - uav_pos[0:-1], axis=1)
    phi_beam_z = np.arctan(r_dis / (uav_pos[-1] - cars_height))

    # C_n_2 = fso_C_0_2 * np.exp(-uav_pos[-1] / 100)  # m^(-2/3)
    k = (2 * np.pi) / fso_transmission_wavelength
    sec = 1 / np.cos(phi_beam_z)

    # Tính tích phân
    def integrand (h):
        return (0.00594 * (wind_speed / 27) ** 2 * (h * 10 ** -5) ** 10 * np.exp(-h / 1000) + \
                2.7 * 10 ** -16 * np.exp(-h / 1500) + fso_C_0_2 * np.exp(-h / 100)) * \
                    (h - cars_height) ** (5/6)
    integral_value,_ = integrate.quad(integrand, cars_height, uav_height)
    sigma_Rytov = 2.25 * (k ** (7/6)) * (sec ** (11/6)) * integral_value
    # Tính h_f
    h_f = np.random.lognormal(mean=-2*sigma_Rytov, sigma=2*np.sqrt(sigma_Rytov), size=shape)


    # 4. Pointing error loss
    # k = 2 * np.pi / (fso_transmission_wavelength * 1e-9)
    C_n_0 = 1e-14
    rho_l = (0.55 * C_n_0 * distance * k ** 2) ** (-3 / 5) # [m]
    omega_d = fso_point_loss_omega_0 * \
              np.sqrt(1 + (1 + (2 * fso_point_loss_omega_0 ** 2 / rho_l ** 2)) *
                      ((fso_transmission_wavelength * 1e-9 * distance) /
                       (np.pi * fso_point_loss_omega_0 ** 2)) ** 2)

    # if uav_pos[1] >= 0:
    theta_beam_xy_x = np.arccos(np.abs(uav_pos[0] - car_pos[:, 0]) / r_dis)
    # else:
    #     theta_beam_xy_x = -np.arccos(uav_pos[0] - car_pos[:, 0] / r_dis)

    niu_1 = np.sqrt(np.pi / 2) * fso_receiver_r / omega_d
    niu_2 = np.abs(np.sin(phi_beam_z) * np.cos(theta_beam_xy_x)) * niu_1

    A_0 = special.erf(niu_1) * special.erf(niu_2)

    k_g = np.sqrt(np.pi) / 4 * (special.erf(niu_1) / (niu_1 * np.exp(-niu_1 ** 2)) + special.erf(niu_2) / (
            np.sin(phi_beam_z) ** 2 * np.cos(theta_beam_xy_x) ** 2 * niu_2 * np.exp(-niu_2) ** 2))

    h_p = A_0 * np.exp(2 * fso_receiver_u ** 2 / (-k_g * omega_d ** 2))
    # print(h_a)

    #  FSO gain
    h = (h_l * h_f * h_p *h_c * (10 ** (fso_gain1 / 10) * (10 ** (fso_gain2 / 10)))) ** 2 * (1 - nlos_flag)
    # print(los_flag)

    return h


def get_thz_gain(nlos_flag: bool, uav_pos: np.ndarray, car_pos: np.ndarray, distance: np.ndarray) -> np.ndarray:

    # shape = distance.shape
    # 1. Path loss and Cloud attenuation (h_l)
    # Path loss (L_p) - ko xét block building
    r_dis = np.linalg.norm(car_pos[:, 0:-1] - uav_pos[0:-1], axis=1)
    phi_beam_z = np.arctan(r_dis / (uav_pos[-1] - cars_height)) # Tính góc Zenith (phi_beam_z)
    # # distance = (uav_height - cars_height) / np.cos(phi_beam_z)
    # L_p =  light_speed / (4 * np.pi * THz_frequency * distance)

    
    # 1. Path Loss - Blockage model
    num = distance.shape[0]
    # coef
    PL = 20 * np.log10(distance) + 20 * np.log10(THz_frequency) + 20 * np.log10(4 * np.pi / light_speed)
    # small-scale
    # NLOS--Rayleigh fading
    h_rayleigh = np.sqrt(1 / 2) * (np.random.randn(num) + np.random.randn(num) * 1j)

    # LOS--Rician fading with 15-dB Rician factor
    K = 10 ** (rf_rician_K_db / 10)
    h_rician = np.sqrt(K / (K + 1)) + np.sqrt(1 / (K + 1)) * h_rayleigh
    # when LOS
    # rician fading
    path_loss_los = PL + rf_eta_los
    h_small_scale_los = h_rician
    # rayleigh fading
    path_loss_nlos = PL + rf_eta_nlos
    h_small_scale_nlos = h_rayleigh

    path_loss = path_loss_los * (1 - nlos_flag) + path_loss_nlos * nlos_flag
    h_small_scale = h_small_scale_los * (1 - nlos_flag) + h_small_scale_nlos * nlos_flag
    # 平方后
    L_p = 10 ** (-path_loss / 20) * np.abs(h_small_scale)


    # Cloud (L_c)
    elevation = np.pi/2 - phi_beam_z
    tem_C = 0
    tem_K = tem_C + 273
    phi = 300 / tem_K
    e_0 = 77.66 + 103.3 * (phi - 1)
    e_1 = 0.0671 * e_0
    e_2 = 3.52
    f_THz = 120 # GHz
    f_p = 20.20 - 146 * (phi - 1) + 316 * (phi - 1) * (phi -1)
    f_s = 39.8 * f_p
    e_f_1 = (e_0 - e_1) / (1 + (f_THz / f_p) ** 2) + (e_1 - e_2) / (1 + (f_THz / f_s) ** 2) + e_2
    e_f_2 = f_THz * (e_0 - e_1) / (f_p * (1 + (f_THz / f_p) ** 2)) + f_THz * (e_1 - e_2) / (f_s * (1 + (f_THz / f_s) ** 2))
    n = (2 + e_f_1) / e_f_2 # 1.2
    atenuation_coe = 0.819 * f_THz / (e_f_2 * (1 + n ** 2))
    # atenuation_coe = 5.97# hệ số suy giảm đám mây
    L_c = 10 **(-atenuation_coe * (THz_cloud_vertical / 10 * np.sin(elevation)))
    
    # h_l = THz_UAV_gain * THz_vehicle_gain * L_p * L_c
    h_l = L_p * L_c


    # 2. Pointing error model (h_p)
    THz_wavelength = light_speed / (THz_frequency)
    beam_waist = (2 * THz_wavelength) / (np.pi * THz_divergence)
    v_t = np.sqrt(np.pi) * THz_detector_radius / (np.sqrt(2) * beam_waist)
    beam_width = (beam_waist ** 2) * np.sqrt(np.pi) * math.erf(v_t) / (2 * v_t * math.exp(-v_t ** 2))
    A = math.erf(v_t) ** 2 # công suất nhận được tại bán kính = 0
    r_t = 0 #  bán kính giữa chùm beam và đầu máy dò
    h_p = A * math.exp((-2 * r_t ** 2) / (beam_width))


    # Fading effect (h_f)
    # alpha =2 => Nakagami-k
    Omega = 1 # công suất trung bình của kênh (Omega = E[R^2])
    G = np.random.gamma(shape=THz_fading_gamma, scale=Omega/THz_fading_gamma, size=1)
    h_f = np.sqrt(G)

    
    # Tính sub-THz gain
    h = (h_l * h_p * h_f * 10 ** (THz_vehicle_gain / 10 ) * 10 ** (THz_UAV_gain / 10 )) ** 2
    # h = (h_l * h_f) ** 2
    # h = h / a
    return h
    


    
def get_capacity(mode: str, tx_power: np.ndarray, gain: np.ndarray) -> np.ndarray:
    """
    :param mode: 
    :param tx_power: [dBm] 10 * log10(x/1000 [mw])
    :param gain: ndarray
    :return:  [Mbps]
    """
    if mode == "FSO":
        snr = fso_k1 * (10 ** ((tx_power - fso_noise) * 2 / 10)) * gain
        # in Mbps
        rate = fso_bandwidth / 2 * np.log2(1 + snr)
    elif mode == "sub-THz":
        snr = (10 ** ((tx_power - fso_noise) / 10)) * gain
        # in Mbps
        rate = THz_bandwidth * np.log2(1 + snr)
    else:
        raise ValueError("FSO sub-THz")

    return rate

#1. Hard - switching
def power_distribute(p_thz: float, h_thz: np.ndarray,
                     p_fso: np.ndarray, h_fso: np.ndarray,
                     target_rate: float):
    # SNR ngưỡng
    fso_snr_threshold = 20 # dB
    fso_snr_th = 10 ** (fso_snr_threshold / 10)
    thz_snr_threshold = 8.13 # dB
    thz_snr_th = 10 ** (thz_snr_threshold / 10)
    # Phân bổ đều công suất cho các phương tiện
    fso_power = p_fso / vehicle_nums
    thz_power = p_thz / vehicle_nums
    # Tính snr tức thời nhận được của FSO và sub-THz
    fso_snr = fso_k1 * (10 ** ((fso_power - fso_noise) * 2 / 10)) * h_fso
    thz_snr = (10 ** ((thz_power - fso_noise) / 10)) * h_thz
    # Tính toán rate 
    FSO_rate = get_capacity(mode="FSO", tx_power=fso_power, gain=h_fso)
    THz_rate = get_capacity(mode="sub-THz", tx_power=thz_power, gain=h_thz)
    rate = np.zeros_like(FSO_rate)
    real_rate = np.zeros_like(FSO_rate)
    # Tạo biến đếm số lần sử dụng 2 liên kết
    count_fso = np.zeros_like(fso_snr)
    count_thz = np.zeros_like(thz_snr)
    #Chuyển mạch cứng
    for i in range(len(fso_snr)):
        if fso_snr[i] >= fso_snr_th:
            rate[i] = FSO_rate[i]
            count_fso[i] += 1
        elif fso_snr[i] < fso_snr_th and thz_snr[i] > thz_snr_th:
            rate[i] = THz_rate[i]
            count_thz[i] += 1
        elif fso_snr[i] < fso_snr_th and thz_snr[i] < thz_snr_th:
            rate[i] = 0

        real_rate[i] = rate[i]
        if rate[i] > target_rate:
            rate[i] = target_rate
    return rate, FSO_rate, THz_rate, real_rate, count_fso, count_thz


# 2. Soft - switching 
# def power_distribute(p_thz: float, h_thz: np.ndarray,
#                      p_fso: np.ndarray, h_fso: np.ndarray,
#                      target_rate: float):
#     # SNR ngưỡng & thông số
#     fso_snr_SW = 20 # dB # snr FSO chuyển xuống cùng sub-THz
#     fso_snr_sw = 10 ** (fso_snr_SW / 10)
#     snr_OUT = 8.13 # dB
#     snr_out = 10 ** (snr_OUT / 10)
#     # Điều chế
#     j = np.array([0, 1, 2, 3, 4, 5, 6, 7]) # [no modulation, BPSK, QPSK, 8-QAM, 16-QAM, 32-QAM]
#     snr_th_modulation = 2/3 * (2 ** j - 1) * np.log(1 / (5 * target_BER))
#     basic_rate = 400 # Msps
#     transmit_rate = basic_rate * j
#     # Phân bổ đều công suất cho các phương tiện
#     fso_power = p_fso / vehicle_nums
#     thz_power = p_thz / vehicle_nums
#     # Tính snr tức thời nhận được của FSO và sub-THz
#     fso_snr = fso_k1 * (10 ** ((fso_power - fso_noise) * 2 / 10)) * h_fso
#     thz_snr = (10 ** ((thz_power - fso_noise) / 10)) * h_thz
#     # Tính toán rate 
#     FSO_rate = get_capacity(mode="FSO", tx_power=fso_power, gain=h_fso)
#     THz_rate = get_capacity(mode="sub-THz", tx_power=thz_power, gain=h_thz)
#     rate = np.zeros_like(FSO_rate)
#     real_rate = np.zeros_like(FSO_rate)
#     # Tạo biến đếm số lần sử dụng 2 liên kết
#     snr_sc = np.zeros_like(fso_snr)
#     count_primary = np.zeros_like(fso_snr)
#     count_backup = np.zeros_like(thz_snr)
#     count_outage = np.zeros_like(thz_snr)
#     #Chuyển mạch cứng
#     for i in range(len(fso_snr)):
#         # Tính snr_sc
#         snr_sc[i] = np.maximum(fso_snr[i], thz_snr[i])
        
#         # primary link
#         if fso_snr[i] >= fso_snr_sw:
#             rate[i] = FSO_rate[i]
#             count_primary[i] += 1
        
#         # backup link
#         elif fso_snr[i] < fso_snr_sw and snr_sc[i] > snr_out:
#             count_backup[i] += 1
#             if snr_sc[i] >= snr_th_modulation[6]: # 64-QAM
#                 rate[i] = transmit_rate[6]
#             elif snr_sc[i] >= snr_th_modulation[5] and snr_sc[i] < snr_th_modulation[6]: # 32-QAM
#                 rate[i] = transmit_rate[5]
#             elif snr_sc[i] >= snr_th_modulation[4] and snr_sc[i] < snr_th_modulation[5]: # 16-QAM
#                 rate[i] = transmit_rate[4]
#             elif snr_sc[i] >= snr_th_modulation[3] and snr_sc[i] < snr_th_modulation[4]: # 8-QAM
#                 rate[i] = transmit_rate[3]
#             elif snr_sc[i] >= snr_th_modulation[2] and snr_sc[i] < snr_th_modulation[3]: # 4-QAM
#                 rate[i] = transmit_rate[2]
#             elif snr_sc[i] >= snr_th_modulation[1] and snr_sc[i] < snr_th_modulation[2]: # 4-QAM
#                 rate[i] = transmit_rate[1]

#         # outage
#         elif fso_snr[i] < fso_snr_sw and snr_sc[i] < snr_out:
#             rate[i] = 0
#             count_outage[i]+=1

#         real_rate[i] = rate[i]
#         if rate[i] > target_rate:
#             rate[i] = target_rate
#     return rate, FSO_rate, THz_rate, real_rate, count_primary, count_outage


# # 3. Only sub-THz
# # def power_distribute(p_thz: float, h_thz: np.ndarray,
# #                      p_fso: np.ndarray, h_fso: np.ndarray,
# #                      target_rate: float):
# #     # SNR ngưỡng
# #     fso_snr_threshold = 20 # dB
# #     fso_snr_th = 10 ** (fso_snr_threshold / 10)
# #     out_snr_threshold = 8.13 # dB
# #     out_snr_th = 10 ** (out_snr_threshold / 10)
# #     # Phân bổ đều công suất cho các phương tiện
# #     fso_power = p_fso / vehicle_nums
# #     thz_power = p_thz / vehicle_nums
# #     # Tính snr tức thời nhận được của FSO và sub-THz
# #     fso_snr = fso_k1 * (10 ** ((fso_power - fso_noise) * 2 / 10)) * h_fso
# #     thz_snr = (10 ** ((thz_power - fso_noise) / 10)) * h_thz
# #     # Tính toán rate 
# #     FSO_rate = get_capacity(mode="FSO", tx_power=fso_power, gain=h_fso)
# #     THz_rate = get_capacity(mode="sub-THz", tx_power=thz_power, gain=h_thz)
# #     rate = np.zeros_like(FSO_rate)
# #     real_rate = np.zeros_like(FSO_rate)
# #     # Tạo biến đếm số lần sử dụng 2 liên kết
# #     count_fso = np.zeros_like(fso_snr)
# #     count_thz = np.zeros_like(thz_snr)
# #     #Chuyển mạch cứng
# #     for i in range(len(thz_snr)):
# #         if thz_snr[i] >= fso_snr_th:
# #             rate[i] = THz_rate[i]
# #             count_thz[i] += 1
# #         elif thz_snr[i] < out_snr_th:
# #             rate[i] = 0

# #         real_rate[i] = rate[i]
# #         if rate[i] > target_rate:
# #             rate[i] = target_rate
# #     return rate, FSO_rate, THz_rate, real_rate, count_fso, count_thz


# # ONly FSO
# # def power_distribute(p_thz: float, h_thz: np.ndarray,
# #                      p_fso: np.ndarray, h_fso: np.ndarray,
# #                      target_rate: float):
# #     # SNR ngưỡng
#     fso_snr_threshold = 20 # dB
#     fso_snr_th = 10 ** (fso_snr_threshold / 10)
#     out_snr_threshold = 8.13 # dB
#     out_snr_th = 10 ** (out_snr_threshold / 10)
#     # Phân bổ đều công suất cho các phương tiện
#     fso_power = p_fso / vehicle_nums
#     thz_power = p_thz / vehicle_nums
#     # Tính snr tức thời nhận được của FSO và sub-THz
#     fso_snr = fso_k1 * (10 ** ((fso_power - fso_noise) * 2 / 10)) * h_fso
#     thz_snr = (10 ** ((thz_power - fso_noise) / 10)) * h_thz
#     # Tính toán rate 
#     FSO_rate = get_capacity(mode="FSO", tx_power=fso_power, gain=h_fso)
#     THz_rate = get_capacity(mode="sub-THz", tx_power=thz_power, gain=h_thz)
#     rate = np.zeros_like(FSO_rate)
#     real_rate = np.zeros_like(FSO_rate)
#     # Tạo biến đếm số lần sử dụng 2 liên kết
#     count_fso = np.zeros_like(fso_snr)
#     count_thz = np.zeros_like(thz_snr)
#     #Chuyển mạch cứng
#     for i in range(len(thz_snr)):
#         if fso_snr[i] >= fso_snr_th:
#             rate[i] = FSO_rate[i]
#             count_fso[i] += 1
#         elif fso_snr[i] < out_snr_th:
#             rate[i] = 0

#         real_rate[i] = rate[i]
#         if rate[i] > target_rate:
#             rate[i] = target_rate
#     return rate, FSO_rate, THz_rate, real_rate, count_fso, count_thz
