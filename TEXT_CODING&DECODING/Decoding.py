import numpy as np
import os

# === CHUYỂN ĐỔI VĂN BẢN ===
def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(c, 2)) for c in chars)

# === GIẢI MÃ CÁC KIỂU MÃ HÓA ===
def unipolar_decode(signal):
    """Giải mã Unipolar (0V → 0, V → 1)"""
    return ''.join('1' if v == 1 else '0' for v in signal)

def nrz_l_decode(signal):
    """Giải mã NRZ-L"""
    return ''.join('1' if v == -1 else '0' for v in signal)

def nrz_i_decode(signal):
    """Giải mã NRZ-I"""
    decoded_bits = []
    level = 1
    for v in signal:
        if v == level:
            decoded_bits.append('0')
        else:
            decoded_bits.append('1')
            level = -level
    return ''.join(decoded_bits)

def rz_decode(signal):
    """Giải mã RZ"""
    decoded_bits = []
    for i in range(0, len(signal), 2):
        decoded_bits.append('1' if signal[i] == 1 else '0')
    return ''.join(decoded_bits)

def manchester_decode(signal):
    """Giải mã Manchester"""
    decoded_bits = []
    for i in range(0, len(signal), 2):
        if signal[i] == -1 and signal[i+1] == 1:
            decoded_bits.append('1')
        elif signal[i] == 1 and signal[i+1] == -1:
            decoded_bits.append('0')
    return ''.join(decoded_bits)

def differential_manchester_decode(signal):
    """Giải mã Differential Manchester"""
    decoded_bits = []
    level = 1  # Bắt đầu với mức tín hiệu đầu tiên

    for i in range(0, len(signal), 2):  # Duyệt qua từng cặp giá trị tín hiệu
        start_level = signal[i]
        mid_level = signal[i+1]

        # Bit '0' xảy ra khi có sự đảo trạng thái ngay đầu chu kỳ
        if start_level != level:
            decoded_bits.append('0')
        else:  # Bit '1' xảy ra khi không có sự đảo trạng thái đầu chu kỳ
            decoded_bits.append('1')

        # Cập nhật mức tín hiệu cho lần lặp tiếp theo (lấy giá trị giữa chu kỳ)
        level = mid_level  

    return ''.join(decoded_bits)

def ami_decode(signal):
    """Giải mã AMI"""
    return ''.join('1' if v != 0 else '0' for v in signal)

def pseudoternary_decode(signal):
    """Giải mã Pseudoternary"""
    return ''.join('0' if v != 0 else '1' for v in signal)

def two_b_one_q_decode(signal):
    """Giải mã tín hiệu 2B1Q thành chuỗi bit nhị phân theo mức tín hiệu trước đó."""
    decoded_bits = []
    
    # Mapping based on **previous level dependency**
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


# === CHƯƠNG TRÌNH CHÍNH GIẢI MÃ ===
def main():
    # Danh sách các tên file tương ứng với mỗi phương pháp giải mã
    files = {
        1: "1.Unipolar.txt",
        2: "2.NRZ-L.txt",
        3: "3.NRZ-I.txt",
        4: "4.RZ.txt",
        5: "5.Manchester.txt",
        6: "6.Diffmanchester.txt",
        7: "7.AMI.txt",
        8: "8.Pseudoternary.txt",
        9: "9.2b1q.txt"
    }

    print("\nChọn kiểu giải mã:")
    print("1. Unipolar")
    print("2. NRZ-L")
    print("3. NRZ-I")
    print("4. RZ")
    print("5. Manchester")
    print("6. Differential Manchester")
    print("7. AMI")
    print("8. Pseudoternary")
    print("9. 2B1Q")

    choice = int(input("Nhập số (1-9): "))

    # Kiểm tra lựa chọn hợp lệ
    if choice not in files:
        print("❌ Lựa chọn không hợp lệ!")
        return

    # Đọc tín hiệu từ file tương ứng
    file_name = files[choice]
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)

    try:
        # Đọc tín hiệu từ tệp
        encoded_signal = np.loadtxt(file_path, dtype=int)
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        return

    print(f"Đã đọc tín hiệu từ file {file_name}.")

    # Các phương pháp giải mã
    decoding_methods = {
        1: unipolar_decode,
        2: nrz_l_decode,
        3: nrz_i_decode,
        4: rz_decode,
        5: manchester_decode,
        6: differential_manchester_decode,
        7: ami_decode,
        8: pseudoternary_decode,
        9: two_b_one_q_decode,
    }

    decode_function = decoding_methods[choice]
    decoded_signal = decode_function(encoded_signal)

    print(f"Tín hiệu đã giải mã: {decoded_signal}")

    # Chuyển tín hiệu đã giải mã thành văn bản
    decoded_text = bits_to_text(decoded_signal)
    print(f"Văn bản giải mã: {decoded_text}")


if __name__ == "__main__":
    main()