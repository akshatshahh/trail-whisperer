import io, importlib, base64
import httpx, pytest
from fastapi.testclient import TestClient
from PIL import Image
from backend.store import Store

@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv('DATA_DIR',str(tmp_path))
    monkeypatch.setenv('MODE','trail')
    monkeypatch.delenv('MONGODB_URI',raising=False)
    from backend import main
    importlib.reload(main)
    return main

@pytest.fixture
def client(app):
    return TestClient(app.app)

def test_persistence_trip_and_stats(app,client):
    a=client.post('/api/sightings',json={'species':'Oak','kind':'plant','trail_name':'Wildcat Canyon'}).json()
    b=client.post('/api/sightings',json={'species':'Oak','kind':'plant','trail_name':'Wildcat Canyon'}).json()
    assert a['trip_id']==b['trip_id']
    assert Store(app.DATA,'trail').get('sightings',a['id'])['species']=='Oak'
    assert client.get('/api/stats').json()['lifelist_count']==1
    assert client.get('/api/trips').json()[0]['species_count']==1
    assert len(client.get('/api/species/Oak').json()['sightings'])==2
    assert client.get('/api/health').json()['cloud_calls_this_session']==0

def test_trail_blocks_online_paths(app,client,monkeypatch):
    def forbidden(*a,**kw):raise AssertionError('Network attempted')
    monkeypatch.setattr(httpx.Client,'request',forbidden)
    # Invoke handlers directly; avoid intercepting TestClient's own requests.
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as e:app.similar('red bird')
    assert e.value.status_code==403
    with pytest.raises(HTTPException):app.transcribe(app.Transcription(sighting_id='none'))
    with pytest.raises(HTTPException):app.external('GET','https://example.org')
    assert app.cloud_calls==0

def test_missing_optional_keys_and_invalid_data(client):
    assert client.get('/api/sightings').status_code==200
    assert client.post('/api/sync').status_code==503
    assert client.post('/api/sightings',json={'species':'Oak','timestamp':'bad'}).status_code==422
    assert client.post('/api/sightings',json={'species':'Oak','lat':91}).status_code==422
    assert client.post('/api/identify/photo',files={'file':('bad.jpg',b'nope','image/jpeg')}).status_code==422

def test_photo_and_audio_contract(app,client,monkeypatch):
    monkeypatch.setattr(app.inference,'generate',lambda *a,**kw:{'label':'Oak','description':'Lobed leaves','caution':'Uncertain','kind':'plant'})
    monkeypatch.setattr(app.inference,'identify_audio',lambda *a:[{'common':'Robin','scientific':'Turdus migratorius','confidence':.87}])
    im=Image.new('RGB',(100,100),'green');b=io.BytesIO();im.save(b,'JPEG')
    photo=client.post('/api/identify/photo',files={'file':('oak.jpg',b.getvalue(),'image/jpeg')}).json()
    assert photo['label']=='Oak'
    assert client.get(photo['photo_path']).status_code==200
    audio=client.post('/api/identify/audio',files={'file':('song.webm',b'clip','audio/webm')}).json()
    assert audio['results'][0]['confidence']==.87
    assert client.get('/api/health').json()['cloud_calls_this_session']==0

def test_ingest_idempotent_media_enrichment(app,client,monkeypatch):
    app.MODE='basecamp';monkeypatch.setenv('SYNC_TOKEN','test-token')
    monkeypatch.setattr(app,'external',lambda *a,**kw:httpx.Response(200,json={'extract':'An oak tree.'}))
    monkeypatch.setattr(app.inference,'generate',lambda *a,**kw:'Three field facts and tips')
    monkeypatch.setattr(app.inference,'embed',lambda *a:[.1,.2,.3])
    batch={'sightings':[{'id':'one','species':'Oak','kind':'plant','photo_path':'/media/oak.jpg'}],'media':{'oak.jpg':base64.b64encode(b'image').decode()}}
    assert client.post('/api/sync/ingest',json=batch).status_code==401
    for _ in range(2):
        assert client.post('/api/sync/ingest',json=batch,headers={'X-Sync-Token':'test-token'}).status_code==200
    assert len(client.get('/api/sightings').json())==1
    profile=client.get('/api/species/Oak').json()
    assert profile['summary']=='An oak tree.' and profile['field_notes']
    assert client.get('/api/sightings').json()[0]['embedding']==[.1,.2,.3]
    assert client.get('/api/similar?query_text=tree').json()['results'][0]['id']=='one'

def test_failed_sync_preserves_unsynced_then_retries(app,client,monkeypatch):
    row=client.post('/api/sightings',json={'species':'Robin'}).json()
    monkeypatch.setenv('BASECAMP_URL','https://basecamp.example')
    monkeypatch.setenv('SYNC_TOKEN','test-token')
    real_client=httpx.Client
    def fake_client(*a,**kw):return real_client(transport=httpx.MockTransport(lambda r:httpx.Response(503)),**kw)
    monkeypatch.setattr(app.httpx,'Client',fake_client)
    assert client.post('/api/sync').status_code==502
    assert not app.store.get('sightings',row['id'])['synced']
    monkeypatch.setattr(app.httpx,'Client',lambda *a,**kw:real_client(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'accepted_ids':[row['id']]})),**kw))
    assert client.post('/api/sync').json()['synced']==1
    assert app.store.get('sightings',row['id'])['synced']
    assert app.cloud_calls==2

def test_voice_saved_offline(app,client):
    r=client.post('/api/voicenote',files={'file':('memo.webm',b'audio','audio/webm')})
    assert r.status_code==200
    assert r.json()['kind']=='journal'
    assert app.cloud_calls==0

def test_birdnet_result_parser_ignores_settings_and_filters(app,tmp_path,monkeypatch):
    import subprocess
    inf=app.inference
    monkeypatch.setattr(inf.importlib.util,'find_spec',lambda name:object())
    monkeypatch.setattr(inf,'ffmpeg',lambda:'ffmpeg')
    def fake_run(args,**kw):
        if '-m' in args:
            out=__import__('pathlib').Path(args[4])
            (out/'BirdNET_analysis_params.csv').write_text('Sample rate,Overlap\n48000,0\n')
            (out/'clip.BirdNET.results.csv').write_text('Scientific name,Common name,Confidence\na,A,.7\na,A,.9\nb,B,.49\nc,C,.8\nd,D,.6\ne,E,.55\n')
        return subprocess.CompletedProcess(args,0)
    monkeypatch.setattr(inf.subprocess,'run',fake_run)
    results=inf.identify_audio(tmp_path/'bird.wav')
    assert [(r['common'],r['confidence']) for r in results]==[('A',.9),('C',.8),('D',.6)]
