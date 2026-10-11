"""Run before the trip. No network except loopback Ollama."""
import base64, io, json, os
import httpx
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
url = os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434')
with httpx.Client(timeout=180, trust_env=False) as client:
    models = client.get(url + '/api/tags').json()['models']
    for name in ('gemma3n', 'gemma3:4b', 'nomic-embed-text'):
        m = next((m for m in models if m['name'].split(':')[0] == name.split(':')[0]), None)
        print(name, 'installed' if m else 'MISSING', m.get('capabilities') if m else '')
    r = client.post(url + '/api/generate', json={'model': os.getenv('OLLAMA_MODEL','gemma3n'), 'prompt':'What is a field journal? One sentence.', 'stream':False})
    r.raise_for_status(); print('Text:',r.json()['response'])
    im = Image.new('RGB', (200,200), 'green'); buf = io.BytesIO(); im.save(buf,'JPEG')
    r = client.post(url + '/api/generate', json={'model':os.getenv('OLLAMA_VISION_MODEL','gemma3:4b'), 'prompt':'Describe the image in one sentence.', 'images':[base64.b64encode(buf.getvalue()).decode()], 'stream':False})
    r.raise_for_status(); print('Vision:',r.json()['response'])
    r = client.post(url + '/api/embed', json={'model':'nomic-embed-text','input':'oak woodland bird'})
    r.raise_for_status(); print('Embedding dimensions:',len(r.json()['embeddings'][0]))
