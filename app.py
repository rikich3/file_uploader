import imghdr                      # valida contenido real del archivo
import os
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # limite aumentado a 2MB para dropzone
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'

# valida que el archivo sea realmente una imagen
def validate_image(stream):
    header = stream.read(512)       # lee los primeros 512 bytes
    stream.seek(0)                  # reinicia el puntero
    format = imghdr.what(None, header)   # detecta el formato real
    if not format:
        return None                 # no es imagen
    return '.' + (format if format != 'jpeg' else 'jpg')   # devuelve extension

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH']) if os.path.exists(app.config['UPLOAD_PATH']) else []
    return render_template('index.html', files=files)

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        filename = secure_filename(uploaded_file.filename)
        file_ext = os.path.splitext(filename)[1]   # saca la extension del nombre
        
        # valida extension y que el contenido real coincida
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
           file_ext != validate_image(uploaded_file.stream):
            return "Invalid image", 400  # dropzone muestra este mensaje en el error

        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return '', 204  # 204 No Content: exito sin redireccion (requerido por dropzone)


@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

# ejecutar servidor
if __name__ == '__main__':
    app.run(debug=True)