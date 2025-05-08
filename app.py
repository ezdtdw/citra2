# Import library yang diperlukan
from flask import Flask, render_template, request, redirect, url_for  # Flask untuk membuat aplikasi web
from PIL import Image, ImageEnhance, ImageFilter  # Pillow untuk manipulasi gambar
import cv2  # OpenCV untuk pengolahan gambar tingkat lanjut
import os  # Untuk operasi file dan direktori
import numpy as np  # Untuk manipulasi array, digunakan bersama OpenCV
from edge_detection import save_edges  # Import fungsi deteksi tepi

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Konfigurasi folder untuk menyimpan file yang diunggah
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Route untuk halaman utama
@app.route('/')
def index():
    # Merender template HTML untuk halaman utama
    return render_template('index.html')

# Route untuk menangani unggahan file
@app.route('/upload', methods=['POST'])
def upload():
    # Memeriksa apakah file ada dalam request
    if 'files[]' not in request.files:
        # Jika tidak ada file, redirect ke halaman utama
        return redirect(url_for('index'))

    # Mengambil semua file dari request
    files = request.files.getlist('files[]')
    results = []

    # Memproses setiap file
    for file in files:
        if file and file.filename != '':
            # Menyimpan file ke folder yang telah dikonfigurasi
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Memproses gambar untuk meningkatkan kualitasnya
            img = Image.open(filepath)
            img = improve_image_quality(img)

            # Menentukan nama file hasil yang telah diproses
            processed_filename = 'processed_' + file.filename
            processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)

            # Menyimpan gambar yang telah diproses
            img.save(processed_filepath)

            # Melakukan deteksi tepi
            save_edges(file.filename, app.config['UPLOAD_FOLDER'])

            # Mengumpulkan hasil pemrosesan untuk file ini
            result = {
                'original': file.filename,
                'processed': processed_filename,
                'canny': f"{os.path.splitext(file.filename)[0]}_canny.jpg",
                'sobel': f"{os.path.splitext(file.filename)[0]}_sobel.jpg",
                'laplacian': f"{os.path.splitext(file.filename)[0]}_laplacian.jpg"
            }
            results.append(result)

    # Merender template HTML dengan semua hasil
    return render_template('index.html', results=results)

# Fungsi untuk meningkatkan kualitas gambar
def improve_image_quality(img):
    # Mengonversi gambar menjadi grayscale
    img = img.convert('L')

    # Meningkatkan kontras gambar
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    # Mengonversi gambar ke format OpenCV untuk pengolahan lebih lanjut
    img = cv2.cvtColor(np.array(img), cv2.COLOR_GRAY2BGR)
    # Menghaluskan gambar menggunakan Gaussian Blur
    img = cv2.GaussianBlur(img, (5, 5), 0)
    # Mengonversi kembali gambar ke format Pillow
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

    # Menajamkan gambar menggunakan filter Pillow
    img = img.filter(ImageFilter.SHARPEN)

    # Mengembalikan gambar yang telah diproses
    return img

# Menjalankan aplikasi Flask
if __name__ == '__main__':
    # Menjalankan server Flask dalam mode debug
    app.run(debug=True)