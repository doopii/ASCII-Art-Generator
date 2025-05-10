from flask import Flask, render_template, request, session, url_for, jsonify, redirect
from PIL import Image
import io, os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY")

SYMBOL_SETS = {
    'braille': " ⠁⠃⠇⠧⡇⣇⣧⣿",
    'ascii':   " .:-=+*#%@",
    'chinese': "　。丶一十口日田囗国黑"
}

def convert_image(img_bytes, w, h, charset='braille', invert=False):
    img = Image.open(io.BytesIO(img_bytes)).resize((w, h)).convert("L")
    seq = SYMBOL_SETS.get(charset, SYMBOL_SETS['braille'])
    mx  = len(seq) - 1
    def m(p):
        i = min(p // 25, mx)
        return seq[mx - i] if invert else seq[i]
    s = "".join(m(p) for p in img.getdata())
    return "\n".join(s[i:i+w] for i in range(0, len(s), w))

@app.before_request
def clear_on_reload():
    # Flush session on normal GET-refresh
    if request.method == "GET" and request.endpoint=="index" and \
       request.headers.get("Cache-Control")!="max-age=0":
        session.clear()

@app.route("/", methods=["GET"])
def index():
    # Just render initial UI; all conversions done in /preview
    return render_template(
        "index.html",
        ascii_result="",
        img_data=None,
        width=None,
        invert=False,
        charset='braille'
    )

@app.route("/preview", methods=["POST"])
def preview():
    invert  = 'invert' in request.form
    charset = request.form.get("charset","braille")
    size    = request.form.get("size")
    width   = int(request.form.get("custom_width",size)) if size=='custom' else int(size or 60)

    # load image bytes
    file = request.files.get("image")
    if file and file.filename:
        img_bytes = file.read()
        # cache on disk for persistence
        folder = os.path.join(app.root_path,"static","temp")
        os.makedirs(folder,exist_ok=True)
        path = os.path.join(folder,"upload.png")
        with open(path,"wb") as f: f.write(img_bytes)
        session["img_path"] = path
    elif session.get("img_path"):
        with open(session["img_path"],"rb") as f:
            img_bytes = f.read()
    else:
        img_bytes = None

    result = ""
    if img_bytes:
        try:
            im = Image.open(io.BytesIO(img_bytes))
            h = int(width * (im.height/im.width) * 0.55)
            result = convert_image(img_bytes, width, h, charset, invert)
        except:
            result = "Error processing image."

    return jsonify(result=result)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",5000)))
