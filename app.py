from flask import Flask, render_template, request, session, redirect, url_for
from PIL import Image
import io, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Characters from lightest to darkest
ASCII_CHARS = " ⠁⠃⠇⠧⡇⣇⣧⣿"

def convert_image(image_bytes, w, h, invert=False):
    """
    Convert image bytes to ASCII art.
    If invert=True, reverse the mapping so dark pixels use light chars and vice versa.
    """
    image = Image.open(io.BytesIO(image_bytes)).resize((w, h)).convert("L")
    pixels = image.getdata()
    if invert:
        # Map pixel brightness to reversed charset
        chars = "".join(
            ASCII_CHARS[
                len(ASCII_CHARS) - 1 - min(p // 25, len(ASCII_CHARS) - 1)
            ]
            for p in pixels
        )
    else:
        chars = "".join(
            ASCII_CHARS[min(p // 25, len(ASCII_CHARS) - 1)]
            for p in pixels
        )
    return "\n".join([chars[i : i + w] for i in range(0, len(chars), w)])


@app.before_request
def clear_session_on_refresh():
    # Clear session when user reloads the page (except POSTs)
    if request.method == "GET" and request.endpoint == "index":
        if request.headers.get("Cache-Control") != "max-age=0":
            session.clear()


@app.route("/", methods=["GET", "POST"])
def index():
    ascii_result = ""
    width = 60       # default width
    invert = False   # default: no invert

    if request.method == "POST":
        # Reset action
        if "reset" in request.form:
            session.clear()
            return redirect(url_for("index"))

        # Invert checkbox
        invert = "invert" in request.form

        # Determine width
        size = request.form.get("size")
        if size == "custom":
            width = int(request.form.get("custom_width", 60))
        else:
            width = int(size or 60)

        # Handle image upload or reuse
        file = request.files.get("image")
        upload_folder = os.path.join(app.root_path, "static", "temp")
        filename = "upload.png"
        file_path = os.path.join(upload_folder, filename)

        if file and file.filename:
            os.makedirs(upload_folder, exist_ok=True)
            img_bytes = file.read()
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            session["img_path"] = file_path
        elif "img_path" in session:
            img_path = session.get("img_path")
            if img_path and os.path.isfile(img_path):
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
            else:
                img_bytes = None
        else:
            img_bytes = None

        # Generate ASCII
        if img_bytes:
            try:
                img_obj = Image.open(io.BytesIO(img_bytes))
                original_w, original_h = img_obj.size
                aspect_ratio = original_h / original_w
                height = int(width * aspect_ratio * 0.55)
                ascii_result = convert_image(img_bytes, width, height, invert=invert)
            except Exception:
                ascii_result = "Error processing image."

    # For preview display
    img_data = (
        url_for("static", filename="temp/upload.png")
        if session.get("img_path")
        else None
    )

    return render_template(
        "index.html",
        ascii_result=ascii_result,
        img_data=img_data,
        width=width,
        invert=invert,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
