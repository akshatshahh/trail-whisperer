"""Species-only SerpApi research: no GPS, personal notes or media sent."""
import os
from urllib.parse import urlparse
from fastapi import HTTPException
from .telemetry import trace

def search_species(name, scientific, request):
    if os.getenv('MODE', 'trail') != 'basecamp':
        raise HTTPException(403, 'Species research is online and available only at basecamp.')
    key=os.getenv('SERPAPI_API_KEY')
    if not key:
        raise HTTPException(503, 'Set SERPAPI_API_KEY at basecamp to enable species research.')
    query=f'{scientific or name} identification habitat natural history'
    with trace('species.web_search',op='http.client') as span:
        try:
            response=request('GET','https://serpapi.com/search.json',params={'engine':'google','q':query,'api_key':key,'num':5})
            data=response.json()
        except Exception:
            # HTTP exceptions can contain the query-string API key. Never expose them.
            raise HTTPException(502, 'Species research provider unavailable. Check its key, quota and connectivity.') from None
        if data.get('error'):
            raise HTTPException(502, 'Species research provider rejected the search. Check its key and quota.')
        sources=[]
        for row in data.get('organic_results',[]):
            link=row.get('link','')
            parsed=urlparse(link)
            if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username:
                continue
            if any(s['url']==link for s in sources):
                continue
            sources.append({'title':str(row.get('title',name))[:200],'url':link[:2000],'snippet':str(row.get('snippet',''))[:1200]})
            if len(sources)==3:break
        if span:
            span.set_data('research.result_count',len(sources))
        return sources
