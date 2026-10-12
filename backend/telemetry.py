"""Opt-in basecamp tracing. Never initializes the SDK in trail mode."""
import os
from contextlib import contextmanager

_sdk = None
_client = None
_enabled = False

def scrub(event, hint):
    # Manual spans only: no prompts, recordings, locations, headers or credentials.
    for key in ('request', 'user', 'breadcrumbs', 'extra', 'exception', 'logentry'):
        event.pop(key, None)
    if event.get('type') != 'transaction':
        event['message'] = 'Basecamp operation failed; see trace status.'
    return event

def configure(mode, on_cloud_call=None, transport=None):
    global _sdk, _client, _enabled
    _enabled = False
    if _client is not None:
        _client.close()
        _sdk.get_global_scope().set_client(None)
        _client = None
    if mode != 'basecamp' or not os.getenv('SENTRY_DSN'):
        return False
    import sentry_sdk
    from sentry_sdk.transport import HttpTransport
    class CountedTransport(HttpTransport):
        def _send_request(self, *args, **kwargs):
            if on_cloud_call:
                on_cloud_call()
            return super()._send_request(*args, **kwargs)
    try:
        sentry_sdk.init(
            dsn=os.environ['SENTRY_DSN'],
            environment='basecamp',
            server_name='trail-whisperer-basecamp',
            traces_sample_rate=1.0,
            transport=transport if transport is not None else CountedTransport,
            default_integrations=False,
            auto_enabling_integrations=False,
            auto_session_tracking=False,
            include_local_variables=False,
            send_default_pii=False,
            enable_logs=False,
            enable_metrics=False,
            before_send=scrub,
            before_send_transaction=scrub,
        )
        _sdk = sentry_sdk
        _client = sentry_sdk.get_client()
        _enabled = True
    except (ValueError, TypeError):
        # Bad optional telemetry configuration must not break the journal.
        return False
    return True

def enabled():
    return _enabled and os.getenv('MODE', 'trail') == 'basecamp'

@contextmanager
def trace(name, op='gen_ai.invoke_agent', model=None):
    if not enabled():
        yield None
        return
    root = _sdk.get_current_span()
    context = _sdk.start_span(op=op, name=name) if root else _sdk.start_transaction(op=op, name=name)
    with context as span:
        if model:
            span.set_data('gen_ai.request.model', model)
            span.set_data('gen_ai.provider.name', 'ollama')
        span.set_data('gen_ai.operation.name', op.split('.')[-1])
        if op == 'gen_ai.invoke_agent':
            span.set_data('gen_ai.agent.name','Trail Whisperer basecamp')
        try:
            yield span
        except Exception:
            span.set_status('internal_error')
            raise

def record_usage(span, response):
    if span is None:
        return
    for source,target in [('prompt_eval_count','gen_ai.usage.input_tokens'),('eval_count','gen_ai.usage.output_tokens'),('total_duration','ollama.duration_ns')]:
        value=response.get(source)
        if isinstance(value,(int,float)):
            span.set_data(target,value)
    span.set_data('inference.local',True)

def flush():
    if enabled():
        _sdk.flush(timeout=5)
