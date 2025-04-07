import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import tkinter as tk
from tkinter import simpledialog

def read_voltage_file(filename):
    """Đọc dữ liệu điện áp từ file txt"""
    with open(filename, 'r') as f:
        voltage_data = list(map(int, f.read().strip().split()))
    return voltage_data

def unipolar_decoding(voltage_data, img_size):
    """Giải mã Unipolar về dữ liệu pixel"""
    binary_data = ''.join(str(bit) for bit in voltage_data)
    pixel_values = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
    return np.array(pixel_values, dtype=np.uint8).reshape(img_size)

def nrzl_decoding(voltage_data, img_size):
    """Giải mã NRZ-L về dữ liệu pixel"""
    binary_data = ''.join('1' if level == -1 else '0' for level in voltage_data)
    pixel_values = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
    return np.array(pixel_values, dtype=np.uint8).reshape(img_size)

def manchester_decoding(voltage_data, img_size):
    """Giải mã Manchester về dữ liệu pixel"""
    binary_data = []
    for i in range(0, len(voltage_data), 2):
        if voltage_data[i] == -1 and voltage_data[i+1] == 1:
            binary_data.append('1')
        elif voltage_data[i] == 1 and voltage_data[i+1] == -1:
            binary_data.append('0')
        else:
            raise ValueError("Lỗi tín hiệu Manchester: Không phải sự thay đổi hợp lệ!")
    
    pixel_values = [int(''.join(binary_data[i:i+8]), 2) for i in range(0, len(binary_data), 8)]
    return np.array(pixel_values, dtype=np.uint8).reshape(img_size)

def ami_decoding(voltage_data, img_size):
    """Giải mã AMI về dữ liệu pixel"""
    binary_data = []
    last_polarity = 1  # Khởi tạo với +1 cho bit 1 đầu tiên
    for level in voltage_data:
        if level == 0:
            binary_data.append('0')  # Bit 0 là 0
        elif level == last_polarity:
            binary_data.append('1')  # Bit 1
            last_polarity = -last_polarity  # Chuyển đổi giữa +1 và -1 cho mỗi bit 1
        else:
            raise ValueError("Lỗi tín hiệu AMI: Dữ liệu không hợp lệ!")
    
    pixel_values = [int(''.join(binary_data[i:i+8]), 2) for i in range(0, len(binary_data), 8)]
    return np.array(pixel_values, dtype=np.uint8).reshape(img_size)

def two_b_one_q_decode(signal):
    """Giải mã tín hiệu 2B1Q thành chuỗi bit nhị phân theo mức tín hiệu trước đó."""
    decoded_bits = []
    
    # Mapping based on previous level dependency
    reverse_transition_table = {
        (1, 1): "00",  
        (3, 1): "00",  
        (-1, -1): "00",  
        (-3, -1): "00",
        (1, 3): "01",  
        (3, 3): "01", 
        (-1, -3): "01",  
        (-3, -3): "01",
        (1, -1): "10",  
        (3, -1): "10",  
        (-1, 1): "10",  
        (-3, 1): "10",
        (1, -3): "11",  
        (3, -3): "11",  
        (-1, 3): "11",  
        (-3, 3): "11"
    }
    
    previous_level = 1  # Start with a default positive level

    for current_level in signal:
        # Lookup transition using (previous_level, current_level)
        current_bits = reverse_transition_table.get((previous_level, current_level), "")
        
        if current_bits == "":
            raise ValueError(f"Không tìm thấy giá trị {current_level} với mức trước đó {previous_level}.")
        
        decoded_bits.append(current_bits)  # Append decoded bits
        
        # Update previous level for next iteration
        previous_level = current_level
    
    return ''.join(decoded_bits)

def two_b_one_q_decoding(voltage_data, img_size):
    """Giải mã tín hiệu 2B1Q thành dữ liệu pixel"""
    # Giải mã tín hiệu 2B1Q thành chuỗi bit nhị phân
    binary_data = two_b_one_q_decode(voltage_data)
    
    # Chuyển đổi chuỗi nhị phân thành dữ liệu pixel
    pixel_values = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
    return np.array(pixel_values, dtype=np.uint8).reshape(img_size)

def decode_image():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    voltage_file = os.path.join(script_dir, "encoded_image.txt")
    size_file = os.path.join(script_dir, "image_size.npy")
    
    if not os.path.exists(voltage_file) or not os.path.exists(size_file):
        print("❌ Không tìm thấy file mã hóa hoặc file kích thước ảnh!")
        return
    
    voltage_data = read_voltage_file(voltage_file)
    img_size = tuple(np.load(size_file))
    
    root = tk.Tk()
    root.withdraw()
    decode_choice = simpledialog.askinteger("Lựa chọn giải mã", "Nhập kiểu giải mã (1: Unipolar, 2: NRZ-L, 3: Manchester, 4: AMI, 5: 2B1Q):")
    if decode_choice not in [1, 2, 3, 4, 5]:
        print("❌ Lựa chọn không hợp lệ! Hãy nhập 1 (Unipolar), 2 (NRZ-L), 3 (Manchester), 4 (AMI) hoặc 5 (2B1Q).")
        return
    
    if decode_choice == 1:
        img_array = unipolar_decoding(voltage_data, img_size)
    elif decode_choice == 2:
        img_array = nrzl_decoding(voltage_data, img_size)
    elif decode_choice == 3:
        img_array = manchester_decoding(voltage_data, img_size)
    elif decode_choice == 4:
        img_array = ami_decoding(voltage_data, img_size)
    else:
        img_array = two_b_one_q_decoding(voltage_data, img_size)
    
    img = Image.fromarray(img_array)
    plt.figure(figsize=(6,6))
    plt.imshow(img)
    plt.axis('off')
    plt.title("Ảnh giải mã")
    plt.show()
    
    save_path = os.path.join(script_dir, "decoded_image.png")
    img.save(save_path)
    print(f"✅ Ảnh đã được lưu tại: {save_path}")

if __name__ == "__main__":
    decode_image()