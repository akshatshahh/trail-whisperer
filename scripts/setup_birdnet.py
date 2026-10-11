"""Download the official Analyzer V2.4 model bundle while online."""
import os, io, zipfile
from pathlib import Path
import httpx
from dotenv import load_dotenv
load_dotenv()
directory = Path(os.getenv('BIRDNET_DIR', 'birdnet_models'))
directory.mkdir(parents=True, exist_ok=True)
url = 'https://tuc.cloud/index.php/s/886x39f5N3sdsAM/download/V2.4.zip'
print('Downloading official BirdNET V2.4 bundle…')
r = httpx.get(url, timeout=180, follow_redirects=True)
r.raise_for_status()
with zipfile.ZipFile(io.BytesIO(r.content)) as bundle:
    for name in bundle.namelist():
        filename = Path(name).name
        if filename.endswith(('.tflite', '.txt')):
            (directory / filename).write_bytes(bundle.read(name))
for name in ('BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite', 'BirdNET_GLOBAL_6K_V2.4_Labels.txt'):
    if not (directory / name).exists():
        raise RuntimeError('Missing model asset: ' + name)
print('BirdNET models ready in', directory)
