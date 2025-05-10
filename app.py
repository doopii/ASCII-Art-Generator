from flask import Flask, render_template, request, session, redirect, url_for
from PIL import Image
import io, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

ASCII_CHARS = " ⠁⠃⠇⠧⡇⣇⣧⣿"

def convert_image(image_bytes, w, h):
    image = Image.open(io.BytesIO(image_bytes)).resize((w, h)).convert("L")
    pixels = image.getdata()
    chars = "".join([ASCII_CHARS[min(p // 25, len(ASCII_CHARS) - 1)] for p in pixels])
    return "\n".join([chars[i:i + w] for i in range(0, len(chars), w)])

@app.before_request
def clear_session_on_refresh():
    if request.method == "GET" and request.endpoint == "index":
        if request.headers.get("Cache-Control") != "max-age=0":
            session.clear()

@app.route("/", methods=["GET", "POST"])
def index():
    print("[DEBUG] index() route triggered")
    ascii_result = ""
    width = 60  # default width if not set by user

    if request.method == "POST":
        print("[DEBUG] POST received")

        if "reset" in request.form:
            print("[DEBUG] Reset requested")
            session.clear()
            return redirect(url_for("index"))

        size = request.form.get("size")
        if size == "custom":
            width = int(request.form.get("custom_width", 60))
        else:
            width = int(size or 60)

        print(f"[DEBUG] Width = {width}")

        file = request.files.get("image")
        upload_folder = os.path.join(app.root_path, "static", "temp")
        filename = "upload.png"
        file_path = os.path.join(upload_folder, filename)

        if file and file.filename:
            print("[DEBUG] New image uploaded")
            os.makedirs(upload_folder, exist_ok=True)
            img_bytes = file.read()
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            session["img_path"] = file_path
        elif "img_path" in session:
            print("[DEBUG] Reusing image from session")
            img_path = session.get("img_path")
            if img_path and os.path.isfile(img_path):
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
            else:
                img_bytes = None
        else:
            print("[DEBUG] No image available")
            img_bytes = None

        if img_bytes:
            try:
                image_obj = Image.open(io.BytesIO(img_bytes))
                original_w, original_h = image_obj.size
                aspect_ratio = original_h / original_w
                height = int(width * aspect_ratio * 0.55)
                print(f"[DEBUG] Aspect ratio = {aspect_ratio:.2f}, Calculated height = {height}")
                ascii_result = convert_image(img_bytes, width, height)
                print("[DEBUG] ASCII generated")
            except Exception as e:
                print(f"[ERROR] Failed to process image: {e}")
        else:
            print("[DEBUG] No ASCII generated")

    # For preview
    img_data = url_for('static', filename='temp/upload.png') if session.get("img_path") else None

    return render_template("index.html", ascii_result=ascii_result, img_data=img_data, width=width)

if __name__ == "__main__":
    app.run(debug=True)
