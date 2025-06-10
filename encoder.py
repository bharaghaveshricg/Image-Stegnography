from PIL import Image
import os

def encode_image(input_image_path, message, output_image_path):
    try:
        # Open and convert image to RGB
        img = Image.open(input_image_path).convert("RGB")

        # Always save as PNG to avoid lossy compression
        if not output_image_path.lower().endswith(".png"):
            output_image_path += ".png"

        encoded = img.copy()
        width, height = img.size

        # Convert message to binary + end delimiter
        binary_message = ''.join(format(ord(char), '08b') for char in message) + '1111111111111110'
        data_index = 0

        for y in range(height):
            for x in range(width):
                if data_index >= len(binary_message):
                    break
                r, g, b = encoded.getpixel((x, y))

                if data_index < len(binary_message):
                    r = (r & ~1) | int(binary_message[data_index])
                    data_index += 1
                if data_index < len(binary_message):
                    g = (g & ~1) | int(binary_message[data_index])
                    data_index += 1
                if data_index < len(binary_message):
                    b = (b & ~1) | int(binary_message[data_index])
                    data_index += 1

                encoded.putpixel((x, y), (r, g, b))

        encoded.save(output_image_path, format="PNG")
        return True, f"Message encoded and saved as {os.path.basename(output_image_path)}"
    except Exception as e:
        return False, f"Encoding failed: {str(e)}"
