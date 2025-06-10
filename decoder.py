from PIL import Image

def decode_image(image_path):
    try:
        img = Image.open(image_path)
        binary_data = ""
        for pixel in img.getdata():
            for channel in pixel[:3]:
                binary_data += str(channel & 1)

        all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
        decoded = ""
        for byte in all_bytes:
            if byte == '11111110':  # Delimiter
                break
            decoded += chr(int(byte, 2))
        return True, decoded
    except Exception as e:
        return False, f"Decoding failed: {str(e)}"
