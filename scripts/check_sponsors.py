"""Verify new basecamp sponsors with public test data, never your journal.
Requires SENTRY_DSN and SERPAPI_API_KEY in .env. After running, confirm
species.research / gen_ai.chat spans in the Sentry project dashboard.
"""
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
missing=[k for k in ('SENTRY_DSN','SERPAPI_API_KEY') if not os.getenv(k)]
if missing:
    print('Add these basecamp settings first: '+', '.join(missing))
    raise SystemExit(2)
with tempfile.TemporaryDirectory(prefix='trail-sponsor-test-') as directory:
    os.environ.update(MODE='basecamp',MONGODB_URI='',DATA_DIR=directory)
    from backend.main import research_profile,telemetry,store
    if not telemetry.enabled():
        raise SystemExit('Sentry configuration invalid; check the project DSN.')
    profile={'id':'Black-capped Chickadee','name':'Black-capped Chickadee','scientific':'Poecile atricapillus','summary':'A small North American songbird.'}
    store.put('species',profile)
    try:
        result=research_profile(profile)
        assert result['research_sources'] and result['field_notes']
        print('SerpApi: '+str(len(result['research_sources']))+' public reference links returned.')
        print('Local Gemma: sourced field notes generated.')
        telemetry.flush()
        print('Sentry: species research/model traces flushed. Confirm receipt in the project dashboard.')
        print('No personal journal records were accessed or changed.')
    except Exception as error:
        # Never print raw HTTP exceptions containing a query-string provider key.
        print('Verification failed: '+type(error).__name__+'. Check provider key/quota and local Ollama.')
        raise SystemExit(1)
    finally:
        telemetry.configure('trail')
