import os
import re
import sys
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent

MODELS = [
    {
        "name": "VGG encoder",
        "env": "VGG_MODEL_URL",
        "path": ROOT_DIR / "NST_Code" / "vgg_normalised.pth",
    },
    {
        "name": "AdaIN decoder",
        "env": "DECODER_MODEL_URL",
        "path": ROOT_DIR / "NST_Code" / "experiment" / "final_exp" / "decoder_final.pth",
    },
]


def google_drive_file_id(url):
    patterns = [
        r"/file/d/([^/]+)",
        r"[?&]id=([^&]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def download_with_gdown(url, destination):
    try:
        import gdown
    except ImportError:
        return False

    file_id = google_drive_file_id(url)
    download_url = f"https://drive.google.com/uc?id={file_id}" if file_id else url
    gdown.download(download_url, str(destination), quiet=False, fuzzy=True)
    return destination.exists() and destination.stat().st_size > 0


def download_with_urllib(url, destination):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request) as response:
        with destination.open("wb") as output:
            output.write(response.read())


def ensure_model(model):
    destination = model["path"]
    if destination.exists() and destination.stat().st_size > 0:
        print(f"{model['name']} already exists: {destination}")
        return

    url = os.environ.get(model["env"])
    if not url:
        raise RuntimeError(
            f"Missing {model['env']}. Add this environment variable in Render "
            f"with a public download URL for {model['name']}."
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {model['name']} to {destination}")

    if "drive.google.com" in url and download_with_gdown(url, destination):
        return

    download_with_urllib(url, destination)

    if not destination.exists() or destination.stat().st_size == 0:
        raise RuntimeError(f"Downloaded file is empty: {destination}")


def main():
    try:
        for model in MODELS:
            ensure_model(model)
    except Exception as exc:
        print(f"Model download failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
