"""Real inference via HTTP, saving proof to data/validation-http.json."""
import json, os
from pathlib import Path
import httpx
url=os.getenv('TRAIL_URL','http://localhost:8000')
results={}
with httpx.Client(timeout=240,trust_env=False) as c:
    results['health_before']=c.get(url+'/api/health').json()
    with open('data/fixtures/soundscape.wav','rb') as f:
        r=c.post(url+'/api/identify/audio',files={'file':('bird.wav',f,'audio/wav')})
    r.raise_for_status();results['audio']=r.json()
    if Path('data/fixtures/plant.jpg').exists():
        with open('data/fixtures/plant.jpg','rb') as f:
            r=c.post(url+'/api/identify/photo',files={'file':('plant.jpg',f,'image/jpeg')})
        r.raise_for_status();results['photo']=r.json()
    r=c.post(url+'/api/ask',json={'question':'How can I observe birds without disturbing them?'})
    r.raise_for_status();results['ask']=r.json()
    results['health_after']=c.get(url+'/api/health').json()
assert results['health_after']['cloud_calls_this_session']==0
Path('data/validation-http.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
