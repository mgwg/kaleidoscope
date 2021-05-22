from flask import Flask, render_template
from preprocess import gen_images
from PIL import Image
import base64
import io

app = Flask("")

print("Images buffering...")
images = gen_images("test.jpg")

b64images = []

img: Image.Image
for img in images:

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    b64images.append(base64.b64encode(buffered.getvalue()).decode("utf-8"))


@app.route('/')
def index():
    return render_template('index.html', imagedata=b64images)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
