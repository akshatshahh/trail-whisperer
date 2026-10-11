import base64, csv, json, os, shutil, subprocess, tempfile, threading, sys, importlib.util
from pathlib import Path
from urllib.parse import urlparse
import httpx
from fastapi import HTTPException

MODEL = os.getenv('OLLAMA_MODEL', 'gemma3n')
VISION_MODEL = os.getenv('OLLAMA_VISION_MODEL', 'gemma3:4b')
if any('cloud' in name.lower() for name in (MODEL, VISION_MODEL)):
    raise RuntimeError('Cloud model variants are forbidden. Choose downloaded local Gemma weights.')
URL = os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434').rstrip('/')
if urlparse(URL).hostname not in {'localhost', '127.0.0.1', '::1'}:
    raise RuntimeError('OLLAMA_URL must be loopback: AI inference always runs on this machine.')
lock = threading.Lock()

def generate(prompt, image=None, structured=False):
    payload = {'model': VISION_MODEL if image else MODEL, 'prompt': prompt, 'stream': False, 'options': {'temperature': 0.2}}
    if image:
        payload['images'] = [base64.b64encode(image).decode()]
    if structured:
        payload['format'] = 'json'
    try:
        with httpx.Client(timeout=180, trust_env=False) as client:
            r = client.post(URL + '/api/generate', json=payload)
            r.raise_for_status()
            answer = r.json()['response']
        return json.loads(answer) if structured else answer
    except (httpx.HTTPError, ValueError, KeyError) as e:
        raise HTTPException(503, f'Local model unavailable ({MODEL}). Start Ollama and pull the model. {str(e)[:120]}')

def embed(text):
    try:
        with httpx.Client(timeout=120, trust_env=False) as client:
            r = client.post(URL + '/api/embed', json={'model': 'nomic-embed-text', 'input': text})
            r.raise_for_status()
            return r.json()['embeddings'][0]
    except (httpx.HTTPError, KeyError, IndexError):
        return None

def ffmpeg():
    executable = shutil.which('ffmpeg')
    if not executable:
        import imageio_ffmpeg
        executable = imageio_ffmpeg.get_ffmpeg_exe()
    return executable

def identify_audio(path):
    """Official Analyzer CLI, with the documented birdnetlib fallback."""
    with lock, tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / 'clip.wav'
        try:
            subprocess.run([ffmpeg(), '-y', '-i', str(path), '-t', '5', '-ar', '48000', '-ac', '1', str(wav)], check=True, capture_output=True, timeout=30)
        except (subprocess.SubprocessError, RuntimeError) as e:
            raise HTTPException(422, 'Audio conversion failed. Upload a valid 3–5 second clip.') from e
        official = importlib.util.find_spec('birdnet_analyzer') is not None
        detections = []
        if official:
            try:
                subprocess.run([sys.executable, '-m', 'backend.birdnet_worker', str(wav), tmp, str(Path(os.getenv('BIRDNET_DIR', 'birdnet_models')).resolve())], check=True, capture_output=True, timeout=120)
                for file in Path(tmp).rglob('*.BirdNET.results.csv'):
                    with file.open() as stream:
                        for row in csv.DictReader(stream):
                            detections.append({'common': row.get('Common name', row.get('Common Name', 'Unknown')), 'scientific': row.get('Scientific name', row.get('Scientific Name', '')), 'confidence': float(row['Confidence'])})
            except subprocess.SubprocessError as e:
                raise HTTPException(503, 'BirdNET failed. Run scripts/setup_birdnet.py online before heading out.') from e
        else:
            try:
                from birdnetlib import Recording
                from birdnetlib.analyzer import Analyzer
                directory = Path(os.getenv('BIRDNET_DIR', 'birdnet_models'))
                model = directory / 'BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite'
                labels = directory / 'BirdNET_GLOBAL_6K_V2.4_Labels.txt'
                if not model.exists() or not labels.exists():
                    raise HTTPException(503, 'BirdNET models missing. Run scripts/setup_birdnet.py online first.')
                analyzer = Analyzer(classifier_model_path=str(model), classifier_labels_path=str(labels))
                recording = Recording(analyzer, str(wav), min_conf=0.5)
                recording.analyze()
                detections = [{'common': d['common_name'], 'scientific': d['scientific_name'], 'confidence': float(d['confidence'])} for d in recording.detections]
            except ImportError as e:
                raise HTTPException(503, 'BirdNET is not installed. Install requirements-birdnet.txt.') from e
        best = {}
        for item in detections:
            if item['confidence'] >= .5 and item['confidence'] > best.get(item['scientific'], {}).get('confidence', 0):
                best[item['scientific']] = item
        return sorted(best.values(), key=lambda d: d['confidence'], reverse=True)[:3]
