"""Download Wikimedia Commons images listed in .github/fetch-images.tsv into images/ as ~1600px JPEGs."""
import io
import sys
import urllib.request

from PIL import Image

UA = {"User-Agent": "AltaimobiMorningPaper/1.0 (jackson@altaimobi.com)"}
ALLOWED = ("https://upload.wikimedia.org/", "https://thumb.wikimedia.org/")
MAX_W = 1600

for line in open(".github/fetch-images.tsv", encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip() or line.startswith("#"):
        continue
    parts = line.split("\t")
    path, url = parts[0], parts[1]
    crop = parts[2] if len(parts) > 2 else ""
    if not url.startswith(ALLOWED):
        sys.exit("refusing non-Wikimedia URL: " + url)
    if not (path.startswith("images/") and path.endswith(".jpg")) or ".." in path or "/" in path[len("images/"):]:
        sys.exit("refusing path: " + path)
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if crop:
        x0, y0, x1, y1 = (float(v) for v in crop.split(","))
        w, h = im.size
        im = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(path, "JPEG", quality=78, optimize=True, progressive=True)
    print(path, im.size)
