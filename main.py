from flask import Flask, request, render_template, send_file
from kaleidoscope import preprocess, kaleidoscope
import io

app = Flask("")


@app.route('/')
def index():
    return render_template('index.html', image_data = "yeet")


@app.route('/getimage', methods=["GET"])
def data():
    x = int(request.args.get("x"))
    y = int(request.args.get("y"))
    width = int(request.args.get("width"))
    height = int(request.args.get("height"))

    img = kaleidoscope(preprocess("test.jpg", x, y, width, height),
                       windowX=width, windowY=height)
    img_obj = io.BytesIO()
    img.save(img_obj, "GIF")
    img_obj.seek(0)

    return send_file(
        img_obj,
        mimetype="image/gif",
        as_attachment=True,
        attachment_filename="kaleidoscope.gif"
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
