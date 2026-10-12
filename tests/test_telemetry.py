import json
import pytest
from backend import telemetry

def test_trail_never_initializes_sentry_even_with_dsn(monkeypatch):
    monkeypatch.setenv('SENTRY_DSN','https://test@example.com/1')
    monkeypatch.setattr(telemetry,'_client',None)
    calls=[]
    assert telemetry.configure('trail',on_cloud_call=lambda:calls.append(1)) is False
    with telemetry.trace('text.generate') as span:
        assert span is None
    assert not calls

def test_sentry_records_safe_model_usage_and_failure(monkeypatch):
    import sentry_sdk
    from sentry_sdk.transport import Transport
    monkeypatch.setenv('MODE','basecamp');monkeypatch.setenv('SENTRY_DSN','https://test@example.com/1')
    class MemoryTransport(Transport):
        def __init__(self):
            super().__init__();self.envelopes=[]
        def capture_envelope(self,envelope):self.envelopes.append(envelope)
    transport=MemoryTransport()
    try:
        assert telemetry.configure('basecamp',transport=transport)
        with telemetry.trace('species.research'):
            with telemetry.trace('text.generate',op='gen_ai.chat',model='gemma3n') as span:
                telemetry.record_usage(span,{'prompt_eval_count':42,'eval_count':12,'total_duration':1000,'response':'private journal text'})
        with pytest.raises(ValueError):
            with telemetry.trace('text.generate',op='gen_ai.chat',model='gemma3n'):
                raise ValueError('private-test-key')
        telemetry.flush()
        payloads=[json.loads(item.get_bytes()) for env in transport.envelopes for item in env.items if item.headers.get('type')=='transaction']
        assert len(payloads)==2
        serialized=json.dumps(payloads)
        assert 'private journal text' not in serialized and 'private-test-key' not in serialized
        span_payloads=[json.loads(item.get_bytes()) for env in transport.envelopes for item in env.items if item.headers.get('type')=='span']
        spans=[s for payload in span_payloads for s in payload['items']]
        assert any(s['attributes'].get('gen_ai.usage.input_tokens',{}).get('value')==42 and s['attributes'].get('gen_ai.usage.output_tokens',{}).get('value')==12 for s in spans)
        assert 'private journal text' not in json.dumps(span_payloads) and 'private-test-key' not in json.dumps(span_payloads)
        assert payloads[1]['contexts']['trace']['status']=='internal_error'
    finally:
        telemetry.configure('trail')

def test_invalid_optional_sentry_dsn_degrades(monkeypatch):
    monkeypatch.setenv('MODE','basecamp');monkeypatch.setenv('SENTRY_DSN','not-a-dsn')
    assert telemetry.configure('basecamp') is False

def test_sentry_scrubs_request_headers_and_exception_values():
    event={'request':{'headers':{'X-Sync-Token':'secret'}},'user':{'id':'private'},'breadcrumbs':[], 'extra':{'note':'private'},'exception':{'values':[{'value':'secret'}]},'logentry':{'message':'secret'}}
    cleaned=telemetry.scrub(event,{})
    assert all(k not in cleaned for k in ('request','user','breadcrumbs','extra','exception','logentry'))
    assert 'secret' not in json.dumps(cleaned)
