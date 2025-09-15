import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk

TERMINATOR = "$$END$$"

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    text = ""
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            text += chr(int(byte, 2))
    return text

def get_bit(byte, position):
    return (byte >> position) & 1

def set_bit(byte, position, bit):
    mask = 1 << position
    return (byte & ~mask) | (bit << position)

def encode_data_in_image(cover_image, secret_data, is_image=False):
    cover_data_list = list(cover_image.getdata())
    
    if is_image:
        secret_width, secret_height = secret_data.size
        secret_data_list = list(secret_data.getdata())
        
        required_pixels = (1 + 32 + (len(secret_data_list) * 3 * 8))
        data_type_bit = 1
    else: 
        binary_message = text_to_binary(secret_data + TERMINATOR)
        required_pixels = 1 + len(binary_message)
        data_type_bit = 0
        
    available_pixels = len(cover_data_list) * 3
    if required_pixels > available_pixels:
        raise ValueError("Cover image is too small to hold the secret data.")

    pixel = cover_data_list[0]
    r, g, b, *a = pixel
    new_r = (r & 254) | data_type_bit
    cover_data_list[0] = (new_r, g, b) + tuple(a)
    
    data_index = 1

    if is_image:
        metadata = [secret_width, secret_height]
        for i in range(2):
            for j in range(16):
                bit = get_bit(metadata[i], j)
                pixel_index = data_index // 3
                channel_index = data_index % 3
                pixel = cover_data_list[pixel_index]
                val = list(pixel[:3])
                val[channel_index] = (val[channel_index] & 254) | bit
                cover_data_list[pixel_index] = tuple(val) + tuple(pixel[3:])
                data_index += 1
        
        for s_pixel in secret_data_list:
            for s_val in s_pixel[:3]:
                for j in range(8):
                    bit = get_bit(s_val, j)
                    pixel_index = data_index // 3
                    channel_index = data_index % 3
                    pixel = cover_data_list[pixel_index]
                    val = list(pixel[:3])
                    val[channel_index] = (val[channel_index] & 254) | bit
                    cover_data_list[pixel_index] = tuple(val) + tuple(pixel[3:])
                    data_index += 1
    else:
        for bit in binary_message:
            pixel_index = data_index // 3
            channel_index = data_index % 3
            pixel = cover_data_list[pixel_index]
            val = list(pixel[:3])
            val[channel_index] = (val[channel_index] & 254) | int(bit)
            cover_data_list[pixel_index] = tuple(val) + tuple(pixel[3:])
            data_index += 1

    encoded_image = Image.new(cover_image.mode, cover_image.size)
    encoded_image.putdata(cover_data_list)
    return encoded_image

def decode_data_from_image(stego_image):
    stego_data = list(stego_image.getdata())
    data_type = stego_data[0][0] & 1

    if data_type == 0:
        binary_message = ""
        text_message = ""
        data_index = 1
        while not text_message.endswith(TERMINATOR):
            pixel_index = data_index // 3
            channel_index = data_index % 3
            pixel = stego_data[pixel_index]
            bit = pixel[channel_index] & 1
            binary_message += str(bit)
            if len(binary_message) % 8 == 0:
                text_message = binary_to_text(binary_message)
            data_index += 1
            if data_index >= len(stego_data) * 3:
                 raise ValueError("Could not find hidden text.")
        return text_message[:-len(TERMINATOR)]
    else:
        width, height = 0, 0
        data_index = 1
        for i in range(16):
            pixel_index, channel_index = divmod(data_index, 3)
            bit = stego_data[pixel_index][channel_index] & 1
            width = set_bit(width, i, bit)
            data_index += 1
        for i in range(16):
            pixel_index, channel_index = divmod(data_index, 3)
            bit = stego_data[pixel_index][channel_index] & 1
            height = set_bit(height, i, bit)
            data_index += 1

        if width <= 0 or height <= 0 or width > stego_image.width or height > stego_image.height:
            raise ValueError("Invalid hidden image dimensions.")

        decoded_pixels = []
        for _ in range(width * height):
            new_pixel = []
            for _ in range(3):
                byte = 0
                for i in range(8):
                    pixel_index, channel_index = divmod(data_index, 3)
                    bit = stego_data[pixel_index][channel_index] & 1
                    byte = set_bit(byte, i, bit)
                    data_index += 1
                new_pixel.append(byte)
            decoded_pixels.append(tuple(new_pixel))

        decoded_image = Image.new('RGB', (width, height))
        decoded_image.putdata(decoded_pixels)
        return decoded_image

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Tool")
        self.root.geometry("600x500")
        self.root.minsize(550, 450)

        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        
        self.tabControl = ttk.Notebook(root)
        self.encode_tab = ttk.Frame(self.tabControl, padding="10")
        self.decode_tab = ttk.Frame(self.tabControl, padding="10")
        
        self.tabControl.add(self.encode_tab, text='Encode')
        self.tabControl.add(self.decode_tab, text='Decode')
        self.tabControl.pack(expand=1, fill="both")
        
        self.cover_path = tk.StringVar()
        self.secret_path = tk.StringVar()
        self.stego_path = tk.StringVar()
        
        self.create_encode_widgets()
        self.create_decode_widgets()

    def create_encode_widgets(self):
        frame = self.encode_tab
        
        cover_btn = ttk.Button(frame, text="Select Cover Image", command=self.select_cover_image)
        cover_btn.pack(fill='x', pady=5)
        self.cover_label = ttk.Label(frame, text="No cover image selected.", wraplength=500)
        self.cover_label.pack(fill='x', pady=2)
        
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)
        
        self.secret_type = tk.StringVar(value="text")
        text_radio = ttk.Radiobutton(frame, text="Hide Text", variable=self.secret_type, value="text", command=self.toggle_secret_input)
        text_radio.pack(anchor='w')
        image_radio = ttk.Radiobutton(frame, text="Hide Image", variable=self.secret_type, value="image", command=self.toggle_secret_input)
        image_radio.pack(anchor='w', pady=2)
        
        self.text_frame = ttk.Frame(frame)
        self.image_frame = ttk.Frame(frame)
        
        self.secret_text = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, height=5, width=50)
        self.secret_text.pack(expand=True, fill="both", pady=5)
        
        secret_img_btn = ttk.Button(self.image_frame, text="Select Secret Image", command=self.select_secret_image)
        secret_img_btn.pack(fill='x', pady=5)
        self.secret_label = ttk.Label(self.image_frame, text="No secret image selected.", wraplength=500)
        self.secret_label.pack(fill='x', pady=2)

        self.text_frame.pack(fill='x')
        
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)
        
        encode_btn = ttk.Button(frame, text="Encode and Save", command=self.encode_and_save)
        encode_btn.pack(fill='x', pady=10)

    def create_decode_widgets(self):
        frame = self.decode_tab
        
        stego_btn = ttk.Button(frame, text="Select Image to Decode", command=self.select_stego_image)
        stego_btn.pack(fill='x', pady=5)
        self.stego_label = ttk.Label(frame, text="No image selected.", wraplength=500)
        self.stego_label.pack(fill='x', pady=2)
        
        decode_btn = ttk.Button(frame, text="Decode", command=self.decode)
        decode_btn.pack(fill='x', pady=10)
        
        self.result_frame = ttk.Frame(frame)
        self.result_frame.pack(expand=True, fill='both', pady=5)
        
        self.result_label = ttk.Label(self.result_frame, text="Decoded Message/Image will appear here.")
        self.result_label.pack()
        
    def select_cover_image(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if path:
            self.cover_path.set(path)
            self.cover_label.config(text=f"Cover: {path.split('/')[-1]}")

    def select_secret_image(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if path:
            self.secret_path.set(path)
            self.secret_label.config(text=f"Secret: {path.split('/')[-1]}")
            
    def select_stego_image(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if path:
            self.stego_path.set(path)
            self.stego_label.config(text=f"Selected: {path.split('/')[-1]}")

    def toggle_secret_input(self):
        if self.secret_type.get() == "text":
            self.image_frame.pack_forget()
            self.text_frame.pack(fill='x')
        else:
            self.text_frame.pack_forget()
            self.image_frame.pack(fill='x')

    def encode_and_save(self):
        cover_path = self.cover_path.get()
        if not cover_path:
            messagebox.showerror("Error", "Please select a cover image.")
            return

        try:
            cover_image = Image.open(cover_path).convert('RGB')
            secret_data = None
            is_image = self.secret_type.get() == 'image'
            
            if is_image:
                secret_path = self.secret_path.get()
                if not secret_path:
                    messagebox.showerror("Error", "Please select a secret image.")
                    return
                secret_data = Image.open(secret_path).convert('RGB')
            else:
                secret_data = self.secret_text.get("1.0", tk.END).strip()
                if not secret_data:
                    messagebox.showerror("Error", "Please enter some secret text.")
                    return

            output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if not output_path:
                return

            encoded_image = encode_data_in_image(cover_image, secret_data, is_image)
            encoded_image.save(output_path)
            messagebox.showinfo("Success", f"Image successfully saved to {output_path}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def decode(self):
        stego_path = self.stego_path.get()
        if not stego_path:
            messagebox.showerror("Error", "Please select an image to decode.")
            return

        for widget in self.result_frame.winfo_children():
            widget.destroy()

        try:
            stego_image = Image.open(stego_path).convert('RGB')
            decoded_data = decode_data_from_image(stego_image)
            
            if isinstance(decoded_data, str):
                text_widget = scrolledtext.ScrolledText(self.result_frame, wrap=tk.WORD, height=10)
                text_widget.insert(tk.END, decoded_data)
                text_widget.config(state='disabled')
                text_widget.pack(expand=True, fill='both')
            elif isinstance(decoded_data, Image.Image):
                decoded_data.thumbnail((300, 300))
                img_tk = ImageTk.PhotoImage(decoded_data)
                img_label = ttk.Label(self.result_frame, image=img_tk)
                img_label.image = img_tk
                img_label.pack()
                
                save_btn = ttk.Button(self.result_frame, text="Save Decoded Image", command=lambda: self.save_decoded_image(decoded_data))
                save_btn.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during decoding: {e}")
            
    def save_decoded_image(self, image):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            image.save(path)
            messagebox.showinfo("Success", f"Decoded image saved to {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
