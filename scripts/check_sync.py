"""Real local two-service sync/enrichment test, no Atlas/ElevenLabs keys needed."""
import json, os, subprocess, sys, time
from pathlib import Path
import httpx
root = Path(__file__).resolve().parents[1]
directory = root / 'data' / ('integration-' + str(int(time.time())))
directory.mkdir(parents=True)
procs=[]
proof={}
def start(mode,port):
    env={**os.environ,'MODE':mode,'DATA_DIR':str(directory/mode),'MONGODB_URI':'','SYNC_TOKEN':'integration-test-only','BASECAMP_URL':'http://localhost:8003'}
    log=(directory/(mode+'.log')).open('w')
    p=subprocess.Popen([sys.executable,'-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',str(port)],cwd=root,env=env,stdout=log,stderr=log)
    procs.append(p)
    for _ in range(40):
        try:
            if httpx.get(f'http://localhost:{port}/api/health',trust_env=False).status_code==200:return p
        except httpx.HTTPError:pass
        time.sleep(.25)
    raise RuntimeError('Service did not start')
try:
    trail=start('trail',8002);base=start('basecamp',8003)
    with httpx.Client(timeout=240,trust_env=False) as c:
        t='http://localhost:8002';b='http://localhost:8003'
        with open(root/'data/fixtures/soundscape.wav','rb') as f:
            r=c.post(t+'/api/identify/audio',files={'file':('bird.wav',f,'audio/wav')});r.raise_for_status();bird=r.json()
        candidate=bird['results'][0]
        r=c.post(t+'/api/sightings',json={'species':candidate['common'],'scientific':candidate['scientific'],'confidence':candidate['confidence'],'kind':'bird','audio_path':bird['audio_path'],'trail_name':'Validation bench','note':'Official BirdNET sample; not a real trail encounter.'});r.raise_for_status();bird_id=r.json()['id']
        with open(root/'data/fixtures/plant.jpg','rb') as f:
            r=c.post(t+'/api/identify/photo',files={'file':('flower.jpg',f,'image/jpeg')});r.raise_for_status();plant=r.json()
        r=c.post(t+'/api/sightings',json={'species':plant['label'],'scientific':plant.get('scientific',''),'kind':'plant','photo_path':plant['photo_path'],'trail_name':'Validation bench','note':'Public TensorFlow flower sample; not a real trail encounter.'});r.raise_for_status()
        proof['trail_health']=c.get(t+'/api/health').json();assert proof['trail_health']['cloud_calls_this_session']==0
        r=c.post(t+'/api/sync');r.raise_for_status();proof['sync']=r.json();assert proof['sync']['synced']==2
        print('Two real identifications synced with media; waiting for local enrichment.',flush=True)
        for _ in range(90):
            rows=c.get(b+'/api/sightings').json()
            if all(s.get('enrichment_status')=='complete' for s in rows):break
            time.sleep(2)
        assert all(s.get('enrichment_status')=='complete' for s in rows), 'Enrichment remained pending'
        proof['enrichment']=[{'species':s['species'],'status':s.get('enrichment_status'),'embedding_dimensions':len(s.get('embedding') or [])} for s in rows]
        proof['profile']=c.get(b+'/api/species/'+candidate['common']).json()
        r=c.get(b+'/api/similar',params={'query_text':'a small songbird with a black head'});r.raise_for_status();proof['search']=r.json()
        assert any(s['id']==bird_id for s in proof['search']['results'])
        assert proof['profile'].get('summary') and proof['profile'].get('field_notes')
        assert c.get(b+'/api/stats').json()['lifelist_count']==2
        trail.terminate();trail.wait(timeout=15);trail=start('trail',8002)
        assert len(c.get(t+'/api/sightings').json())==2
        proof['persistence_after_restart']=True
        proof['basecamp_stats']=c.get(b+'/api/stats').json()
    (directory/'proof.json').write_text(json.dumps(proof,indent=2))
    print('PASS: local sync, real Wikipedia/Gemma enrichment, semantic search, lifelist and restart persistence.',flush=True)
    print('Proof:',directory/'proof.json')
finally:
    for p in procs:
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill()
