import os
import io
import zipfile
from flask import Flask, request, send_file, render_template
from PIL import Image

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>GIF to PNG Converter</title>
    </head>
    <body>
        <h1>GIF to PNG Converter</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="gif_file" accept="image/gif">
            <button type="submit">Convert and Download</button>
        </form>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'gif_file' not in request.files:
        return "No file uploaded", 400

    gif_file = request.files['gif_file']
    if gif_file.filename == '':
        return "No selected file", 400

    try:
        # GIFを読み込み
        gif = Image.open(gif_file)
        frame_number = 0
        png_files = []

        # ZIPファイル作成用
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            while True:
                # フレームをPNGに変換して保存
                frame_io = io.BytesIO()
                gif.save(frame_io, format="PNG")
                frame_io.seek(0)
                file_name = f"frame_{frame_number}.png"
                zip_file.writestr(file_name, frame_io.read())
                png_files.append(file_name)
                frame_number += 1

                try:
                    gif.seek(gif.tell() + 1)
                except EOFError:
                    break

        zip_buffer.seek(0)

        # ZIPファイルを返す
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name="frames.zip",
            mimetype="application/zip"
        )

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)