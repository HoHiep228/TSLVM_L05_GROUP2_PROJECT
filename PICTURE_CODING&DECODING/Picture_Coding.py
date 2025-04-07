import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, simpledialog

def image_to_binary(image_path):
    """Chuyển đổi ảnh thành chuỗi nhị phân (BGR)"""
    img = Image.open(image_path)
    img_data = np.array(img)
    binary_data = ''.join(format(pixel, '08b') for row in img_data for col in row for pixel in col)
    return binary_data, img_data.shape

def unipolar_encoding(binary_data):
    """Mã hóa Unipolar từ dữ liệu nhị phân"""
    encoded_signal = [1 if bit == '1' else 0 for bit in binary_data]
    return encoded_signal

def nrzl_encoding(binary_data):
    """Mã hóa NRZ-L từ dữ liệu nhị phân"""
    encoded_signal = [-1 if bit == '1' else 1 for bit in binary_data]
    return encoded_signal

def manchester_encoding(binary_data):
    """Mã hóa Manchester từ dữ liệu nhị phân"""
    encoded_signal = []
    for bit in binary_data:
        if bit == '1':
            encoded_signal.extend([-1, 1])  # Bit 1: -1 -> +1
        else:
            encoded_signal.extend([1, -1])  # Bit 0: +1 -> -1
    return encoded_signal

def ami_encoding(binary_data):
    """Mã hóa AMI từ dữ liệu nhị phân"""
    encoded_signal = []
    last_polarity = 1  # Khởi tạo với +1 cho bit 1 đầu tiên
    for bit in binary_data:
        if bit == '1':
            encoded_signal.append(last_polarity)
            last_polarity = -last_polarity  # Chuyển đổi giữa +1 và -1 cho mỗi bit 1
        else:
            encoded_signal.append(0)  # Bit 0 là 0
    return encoded_signal

def two_b_one_q(binary_data):
    """Mã hóa 2B1Q từ dữ liệu nhị phân"""
    signal, level = [], 1
    transition_table = {'00': {'pos': 1, 'neg': -1}, '01': {'pos': 3, 'neg': -3},
                        '10': {'pos': -1, 'neg': 1}, '11': {'pos': -3, 'neg': 3}}
    
    # Mã hóa từng cặp bit
    for i in range(0, len(binary_data), 2):
        pair = binary_data[i:i+2]
        prev_state = 'pos' if level > 0 else 'neg'
        level = transition_table.get(pair, {'pos': 0, 'neg': 0})[prev_state]
        signal.append(level)
    return np.array(signal)

def save_signal_to_file(signal, filename):
    """Lưu tín hiệu điện áp vào file text"""
    with open(filename, 'w') as f:
        f.write('\n'.join(map(str, signal)))

def encode_image():
    root = tk.Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename(title="Chọn file ảnh", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    
    if not image_path:
        print("❌ Không có file nào được chọn!")
        return
    elif not os.path.exists(image_path):
        print("❌ Lỗi: Không tìm thấy file ảnh!")
        return
    
    encoding_choice = simpledialog.askinteger("Lựa chọn mã hóa", "Nhập kiểu mã hóa (1: Unipolar, 2: NRZ-L, 3: Manchester, 4: AMI, 5: 2B1Q):")
    if encoding_choice not in [1, 2, 3, 4, 5]:
        print("❌ Lựa chọn không hợp lệ! Hãy nhập 1 (Unipolar), 2 (NRZ-L), 3 (Manchester), 4 (AMI) hoặc 5 (2B1Q).")
        return

    binary_data, img_size = image_to_binary(image_path)
    print(f"✅ Ảnh đã chuyển thành {len(binary_data)} bit dữ liệu!")
    
    if encoding_choice == 1:
        encoded_signal = unipolar_encoding(binary_data)
        plot_signal(encoded_signal[:100], "Mã hóa Unipolar (100 bit đầu)", [0, 1], ['0', '1'])
    elif encoding_choice == 2:
        encoded_signal = nrzl_encoding(binary_data)
        plot_signal(encoded_signal[:100], "Mã hóa NRZ-L (100 bit đầu)", [-1, 1], ['-1', '+1'])
    elif encoding_choice == 3:
        encoded_signal = manchester_encoding(binary_data)
        plot_signal(encoded_signal[:100], "Mã hóa Manchester (100 bit đầu)", [-1, 1], ['-1', '+1'])
    elif encoding_choice == 4:
        encoded_signal = ami_encoding(binary_data)
        plot_signal(encoded_signal[:100], "Mã hóa AMI (100 bit đầu)", [-1, 0, 1], ['-1', '0', '+1'])
    else:
        encoded_signal = two_b_one_q(binary_data)
        plot_signal(encoded_signal[:100], "Mã hóa 2B1Q (100 bit đầu)", [-3, -1, 1, 3], ['-3', '-1', '1', '3'])
    
    # Lưu dữ liệu
    script_dir = os.path.dirname(os.path.abspath(__file__))
    signal_file = os.path.join(script_dir, "encoded_image.txt")
    size_file = os.path.join(script_dir, "image_size.npy")
    
    save_signal_to_file(encoded_signal, signal_file)
    np.save(size_file, img_size)
    print(f"✅ Dữ liệu điện áp đã được lưu vào '{signal_file}' và thông tin kích thước ảnh được lưu vào '{size_file}'")

def plot_signal(signal, title, yticks, ylabels):
    """Vẽ đồ thị tín hiệu mã hóa"""
    plt.figure(figsize=(12, 4))
    plt.rcParams['font.family'] = 'Times New Roman'  # Đổi font chữ

    # Vẽ đồ thị bước
    plt.step(range(len(signal)), signal, where='post', linewidth=2, color='black')  # Đường biểu đồ màu đen

    # Điều chỉnh trục tung để không bị che tín hiệu
    plt.ylim(min(yticks) - 0.1, max(yticks) + 0.1)
    plt.yticks(yticks, ylabels)
    
    # Bỏ trục hoành
    plt.xticks([])

    # Thiết lập nhãn trục và tiêu đề
    plt.xlabel("Thời gian (mẫu)")
    plt.ylabel("Điện áp")
    plt.title(title)

    # Hiển thị lưới đứt đoạn
    plt.grid(True, linestyle='dashed')

    # Loại bỏ khung trên và bên phải
    plt.gca().spines['top'].set_color('none')
    plt.gca().spines['right'].set_color('none')

    # Hiển thị đồ thị
    plt.show()


if __name__ == "__main__":
    encode_image()