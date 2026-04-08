import imghdr                      # valida contenido real del archivo
import os
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
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
            abort(400)              # rechaza el archivo
        
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

# ejecutar servidor
if __name__ == '__main__':
    app.run(debug=True)