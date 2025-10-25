from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import cv2
import os

# Base directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

# Flask app setup
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    img = cv2.imread(filepath)

    if img is None:
        print("⚠️ OpenCV failed to read:", filepath)
        return None

    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = os.path.join(STATIC_FOLDER, filename)
            cv2.imwrite(newFilename, imgProcessed)
            return f"static/{filename}"
        case "cwebp": 
            newFilename = os.path.join(STATIC_FOLDER, f"{filename.split('.')[0]}.webp")
            cv2.imwrite(newFilename, img)
            return f"static/{filename.split('.')[0]}.webp"
        case "cjpg": 
            newFilename = os.path.join(STATIC_FOLDER, f"{filename.split('.')[0]}.jpg")
            cv2.imwrite(newFilename, img)
            return f"static/{filename.split('.')[0]}.jpg"
        case "cpng": 
            newFilename = os.path.join(STATIC_FOLDER, f"{filename.split('.')[0]}.png")
            cv2.imwrite(newFilename, img)
            return f"static/{filename.split('.')[0]}.png"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST": 
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return render_template("index.html")

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return render_template("index.html")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
            if new:
                flash(f"✅ Your image is ready: <a href='/{new}' target='_blank'>View</a>")
            else:
                flash("⚠️ Failed to process image. Unsupported format or corrupt file.")
            return render_template("index.html")

    return render_template("index.html")

if __name__ == "__main__":
    app.run()
