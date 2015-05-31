from flask import Flask, request, render_template, make_response
from PIL import Image
from StringIO import StringIO
import cStringIO
import urllib
import urlparse

application = Flask(__name__)


def serve_pil_image(pil_img):
    output = StringIO()
    pil_img.save(output, format="JPEG")
    contents = output.getvalue().encode('base64')

    response = make_response(contents)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


def build(rr, f, o):
    new_im = Image.new('RGB', (116 * 5 - 104, 116 * 6 - 72))
    ver = 1
    last_img = None

    for x in xrange(0, 5):
        y = 0
        while y < 6:
            URL = ("http://images{5}.flashphotography.com/Magnifier/" +
                   "MagnifyRender.ashx?X={0}&Y={1}&O={2}&R={3}&F={4}&A=0")
            url = URL.format(60 + 116 * x, 60 + 116 * y, o, rr, f, ver)
            file = cStringIO.StringIO(urllib.urlopen(url).read())
            img = Image.open(file)
            if img == last_img and x == 0 and ver == 1:
                ver = 2
                y = 0
                continue
            w, h = img.size
            nw = nh = 116
            l = (w - nw) / 2
            r = (w + nw) / 2
            t = (h - nh) / 2
            b = (h + nh) / 2
            nimg = img.crop((l, t, r, b))
            new_im.paste(nimg, (116 * x, 116 * y))
            last_img = img
            y += 1

    return new_im


@application.route("/", methods=['GET', 'POST'])
def flash():
    if request.method == 'POST':
        url = request.form['url']
        parsed = urlparse.urlparse(url)
        params = urlparse.parse_qs(parsed.query)
        if not set(['R', 'F', 'O']).issubset(params):
            return "Malformed URL (check the sample placeholder)", 400
        return serve_pil_image(build(params['R'][0], params['F'][0],
                                     params['O'][0]))
    else:
        return render_template('index.html')

if __name__ == "__main__":
    application.run(host='0.0.0.0')
