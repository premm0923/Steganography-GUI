# 💻 Python Steganography GUI Tool 🖼️

A user-friendly desktop application built with Python and Tkinter that allows you to hide secret messages 📝 or even other images 🖼️ within a cover image.  
It also provides the functionality to extract the hidden data from a stego-image.

This tool uses the Least Significant Bit (LSB) steganography technique to embed data invisibly into the pixels of the cover image.

---

## ✨ Features

- ✍️ **Encode Text:** Hide any text message within a PNG image.
- 🖼️ **Encode Image:** Hide a smaller PNG image within a larger cover PNG image.
- 🔍 **Decode:** Automatically detect and extract either a hidden text message or a hidden image from a stego-image.
- 💾 **Save Decoded Data:** Save decoded text or image to a file.
- 🖥️ **Graphical User Interface:** Intuitive, tabbed Tkinter interface — no programming required.
- 🌐 **Cross-Platform:** Runs on Windows, macOS, and Linux (Python + Tkinter).
- 🖼️ **PNG/JPG Support:** PNG recommended for best results. JPG/JPEG can be converted automatically if added.

---

## ⚙️ How It Works

The application employs the LSB (Least Significant Bit) steganography method.  
**Here's an overview:**

- 🏷️ **Data Header:** The first pixel stores a "header" bit (0 = text, 1 = image).
- 📏 **Metadata (for images):** If hiding an image, its width and height are stored in the next pixels.
- 🧬 **Data Embedding:** Secret data (text/image pixels) is converted to binary and embedded into the least significant bit of each RGB channel.
- 🛑 **Terminator (for text):** For text, the special terminator string (`$$END$$`) signals the end of the message.
- 👁️ **Stealth:** Minuscule pixel changes make the hidden data invisible to the human eye.

---

## 📂 Project Structure

```
steganography-tool/
│-- steganography_gui.py   
│-- README.md              
│-- requirements.txt       
│-- LICENSE                
│-- sample/                
```

---

## ✅ Requirements

- Python 3.x (3.8+ recommended)
- [Pillow](https://pypi.org/project/Pillow/) (PIL fork)
- Tkinter (usually included with Python)

Install dependencies:

```bash
pip install Pillow
```

---

## 🚀 Installation & Usage

1. **Clone or Download** this repository.
2. **Install Dependencies:**  
   ```bash
   pip install Pillow
   ```
3. **Run the Application:**  
   ```bash
   steganography_gui.py
   ```
   (Or: `steg.py` if you named the file differently.)

---

## 🖱️ How to Use

### Encoding (Hiding Data)

1. Go to the **Encode** tab.
2. Click **Select Cover Image** and choose a `.png` file.
3. Choose whether to hide **Text** or **Image**.
    - If hiding text, type your message.
    - If hiding an image, click **Select Secret Image** and choose your secret `.png`.
4. Click **Encode and Save**. Choose where to save the stego-image.

### Decoding (Revealing Data)

1. Go to the **Decode** tab.
2. Click **Select Image to Decode** and choose your stego-image (`.png`).
3. Click **Decode**.
    - If text was hidden, it appears in the text box.
    - If an image was hidden, it displays and you can save it.

---

## ⚠️ Notes & Limitations

- **PNG format recommended** for cover and secret images.
- **Cover image must be large enough** to hide the secret data, or encoding will fail.
- **Hidden image dimensions** are stored in the stego image for accurate recovery.
- Only PNG images are supported for decoding. JPG/JPEG are converted to PNG automatically when encoding.
- The app will notify you if the cover image is too small.
  

---

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## 🙏 Credits

Developed by [premm0923](https://github.com/premm0923).

---
