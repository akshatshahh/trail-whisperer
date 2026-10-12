"""Real model regression check against scripts/offline_server.py (port 8004).
Requires already-downloaded data/fixtures/plant.jpg and soundscape.wav.
No fixtures or models are downloaded during this check.
"""
import json
from pathlib import Path
import httpx
url='http://localhost:8004'
proof={}
with httpx.Client(timeout=180,trust_env=False) as c:
 policy=c.get(url+'/api/offline-test');policy.raise_for_status()
 assert policy.json()['outbound_policy']=='loopback only'
 assert policy.json()['blocked_attempts']>=1
 for kind,file in [('photo','plant.jpg'),('audio','soundscape.wav')]:
  with open(Path('data/fixtures')/file,'rb') as stream:
   r=c.post(url+'/api/identify/'+kind,files={'file':(file,stream)})
  r.raise_for_status();j=r.json();proof[kind]=j
  if kind=='photo':
   row={'species':j['label'],'scientific':j.get('scientific',''),'kind':j.get('kind','plant'),'photo_path':j['photo_path']}
  else:
   assert j['results'];b=j['results'][0]
   row={'species':b['common'],'scientific':b['scientific'],'kind':'bird','confidence':b['confidence'],'audio_path':j['audio_path']}
  row.update(trail_name='Offline regression fixture',note='Public sample for testing; not a real trail encounter.')
  r=c.post(url+'/api/sightings',json=row);r.raise_for_status()
  saved=r.json();assert any(s['id']==saved['id'] for s in c.get(url+'/api/sightings').json())
  assert c.get(url+saved['photo_path' if kind=='photo' else 'audio_path']).status_code==200
  print(kind,'identified, saved, re-read and media served.',flush=True)
 r=c.post(url+'/api/ask',json={'question':'Which species did I save today? Answer briefly.'});r.raise_for_status();proof['ask']=r.json()
 for path,body in [('/api/sync',{}),('/api/voicenote/transcribe',{'sighting_id':'test'})]:
  assert c.post(url+path,json=body).status_code in (403,503)
 proof['health']=c.get(url+'/api/health').json();proof['network']=c.get(url+'/api/offline-test').json()
 assert proof['health']['cloud_calls_this_session']==0
 # No unexpected egress was attempted; only the startup test probe was blocked.
 assert proof['network']['blocked_attempts']==1
Path('data/offline-regression-proof.json').write_text(json.dumps(proof,indent=2))
print('PASS: real photo, audio, Q&A, storage, media and offline gates; zero cloud calls.')
