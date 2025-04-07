import numpy as np
import matplotlib.pyplot as plt
import os

# === CHUYỂN ĐỔI VĂN BẢN ===
def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(c, 2)) for c in chars)

# === CÁC KIỂU MÃ HÓA ===
def Unipolar(bits):
    return np.array([1 if bit == '1' else 0 for bit in bits])

def NRZL(bits):
    return np.array([-1 if bit == '1' else 1 for bit in bits])

def NRZI(bits):
    signal, level = [], 1
    for bit in bits:
        if bit == '1':
            level = -level
        signal.append(level)
    return np.array(signal)

def RZ(bits):
    signal = []
    for bit in bits:
        if bit == '1':
            signal.extend([1, 0])
        else:
            signal.extend([-1, 0])
    return np.array(signal, dtype=np.int8)

def Manchester(bits):
    return np.array([val for bit in bits for val in ([-1, 1] if bit == '1' else [1, -1])])

def Diffmanchester(bits):
    signal, level = [], 1
    for bit in bits:
        if bit == '0':
            level = -level
        signal.append(level)
        level = -level
        signal.append(level)
    return np.array(signal)

def AMI(bits):
    signal, level = [], 1
    for bit in bits:
        if bit == '1':
            signal.append(level)
            level = -level
        else:
            signal.append(0)
    return np.array(signal)

def Pseudoternary(bits):
    signal, level = [], 1
    for bit in bits:
        if bit == '0':
            signal.append(level)
            level = -level
        else:
            signal.append(0)
    return np.array(signal)

def two_b_one_q(bits):
    signal, level = [], 1
    transition_table = {'00': {'pos': 1, 'neg': -1}, '01': {'pos': 3, 'neg': -3},
                        '10': {'pos': -1, 'neg': 1}, '11': {'pos': -3, 'neg': 3}}
    for i in range(0, len(bits), 2):
        pair = bits[i:i+2]
        prev_state = 'pos' if level > 0 else 'neg'
        level = transition_table.get(pair, {'pos': 0, 'neg': 0})[prev_state]
        signal.append(level)
    return np.array(signal)

# === LƯU FILE ===
def save_signal_to_file(filename, signal):
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    np.savetxt(file_path, signal, fmt='%d')
    print(f"💾 Đã lưu tín hiệu vào {file_path}")

# === VẼ ĐỒ THỊ ===
def plot_signal_standard(original_text, encoded_signal, encoding_type, bit_stream):
    plt.figure(figsize=(12, 4))
    plt.rcParams['font.family'] = 'Times New Roman'
    
    x = range(len(encoded_signal) + 1)
    y = np.append(encoded_signal, encoded_signal[-1])
    plt.step(x, y, where='post', linewidth=2, color='black')
    plt.xlim(0, len(encoded_signal))
    
    for i, bit in enumerate(bit_stream):
        plt.text(i + 0.5, encoded_signal[i] + 0.2, bit, ha='center', va='bottom', fontsize=10,
                 bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0'))
    
    plt.ylim(min(encoded_signal) - 1, max(encoded_signal) + 1)
    plt.ylabel("Điện áp")
    plt.xticks([]) 
    plt.grid(True, linestyle='dashed')
    plt.title(f"Mã hóa {encoding_type} cho văn bản: {original_text}")
    plt.gca().spines['top'].set_color('none')
    plt.gca().spines['right'].set_color('none')
    plt.show()

def plot_signal_special(original_text, encoded_signal, encoding_type, bit_stream):
    plt.figure(figsize=(12, 4))
    plt.rcParams['font.family'] = 'Times New Roman'
    
    x = range(len(encoded_signal) + 1)
    y = np.append(encoded_signal, encoded_signal[-1])
    plt.step(x, y, where='post', linewidth=2, color='black')
    plt.xlim(0, len(encoded_signal))
    
    for i in range(0, len(encoded_signal) - 1, 2):
        mid_x = i + 1
        mid_y = (encoded_signal[i] + encoded_signal[i + 1]) / 2
        bit = bit_stream[i // 2] if i // 2 < len(bit_stream) else ''
        plt.text(mid_x, mid_y + 0.2, bit, ha='center', va='top', fontsize=10,
                 bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.3'))
    
    plt.ylim(min(encoded_signal) - 1, max(encoded_signal) + 1)
    plt.ylabel("Điện áp")
    plt.xticks([]) 
    plt.grid(True, linestyle='dashed')
    plt.title(f"Mã hóa {encoding_type} cho văn bản: {original_text}")
    plt.gca().spines['top'].set_color('none')
    plt.gca().spines['right'].set_color('none')
    plt.show()

# === VẼ ĐỒ THỊ DÀNH RIÊNG CHO 2B1Q ===
def plot_2b1q_signal(original_text, encoded_signal):
    plt.figure(figsize=(12, 4))
    plt.rcParams['font.family'] = 'Times New Roman'

    # Cập nhật các mức điện áp
    transition_table = {'00': 1, '01': 3, '10': -1, '11': -3}

    x = range(len(encoded_signal) + 1)
    y = np.append(encoded_signal, encoded_signal[-1])
    plt.step(x, y, where='post', linewidth=2, color='black')
    plt.xlim(0, len(encoded_signal))

    plt.ylim(min(encoded_signal) - 1, max(encoded_signal) + 1)
    plt.ylabel("Điện áp")
    plt.xticks([]) 
    plt.grid(True, linestyle='dashed')
    plt.title(f"Mã hóa 2B1Q cho văn bản: {original_text}")
    plt.gca().spines['top'].set_color('none')
    plt.gca().spines['right'].set_color('none')
    plt.show()

# === CHƯƠNG TRÌNH CHÍNH ===
def main():
    text = input("Nhập văn bản: ")
    bit_stream = text_to_bits(text)
    print(f"Chuỗi bit sau khi chuyển đổi: {bit_stream}")

    encoding_methods = {
        1: ("Unipolar", Unipolar),
        2: ("NRZ-L", NRZL),
        3: ("NRZ-I", NRZI),
        4: ("RZ", RZ),
        5: ("Manchester", Manchester),
        6: ("Diffmanchester", Diffmanchester),
        7: ("AMI", AMI),
        8: ("Pseudoternary", Pseudoternary),
        9: ("2b1q", two_b_one_q),
    }

    print("\nChọn kiểu mã hóa:")
    for num, (name, _) in encoding_methods.items():
        print(f"{num}. {name.upper()}")

    choice = int(input("Nhập số (1-9): "))

    if choice in encoding_methods:
        encoding_name, encode_function = encoding_methods[choice]
        encoded_signal = encode_function(bit_stream)
        filename = f"{choice}.{encoding_name}.txt"
        save_signal_to_file(filename, encoded_signal)
        
        # Nếu chọn 2b1q, vẽ đồ thị đặc biệt cho mã hóa này
        if encoding_name == "2b1q":
            plot_2b1q_signal(text, encoded_signal)
        elif encoding_name in ["RZ", "Manchester", "Diffmanchester"]:
            plot_signal_special(text, encoded_signal, encoding_name.upper(), bit_stream)
        else:
            plot_signal_standard(text, encoded_signal, encoding_name.upper(), bit_stream)
    else:
        print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()