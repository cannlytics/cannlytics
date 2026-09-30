"""
Check AI Providers | Cannlytics
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/28/2026
Updated: 9/28/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Make one small request through the real COA client for every AI
    provider whose key is set, and report whether it worked, its tokens,
    and its cost. Run it after every model update and before any large
    parse: offline tests cannot see a model the provider has retired or
    a request its SDK refuses to send, and on 2026-09-28 both were true
    (the xAI default was retired; every Anthropic call was refused
    before it was sent).

        python tools/check_ai_providers.py                 # every default model
        python tools/check_ai_providers.py --all-models    # every registered model

    Each request costs a fraction of a cent. Keys are read from the
    environment (load your `.env` first, or pass --env-file).
"""
# Standard imports:
import argparse
import sys

# Internal imports:
from cannlytics.data.coas.ai_client import AIClient
from cannlytics.data.coas.config import AI_PROVIDERS, PRICES_VERIFIED

PROMPT = 'Return this JSON object exactly: {"lab": "Cannlytics", "total_thc": 21.4, "status": "pass"}'

def check(provider: str, model: str) -> bool:
    """Send one request; print the outcome; return whether it worked."""
    client = AIClient(provider=provider, model=model)
    if not client.is_available:
        print(f'  skip  {provider:9s} {model:30s} no {AI_PROVIDERS[provider]["env_key"]}')
        return True
    parsed, cost, in_tok, out_tok = client._call_ai(
        'You extract data and answer with JSON only.', PROMPT, page_text='(no document)', mode='metadata',
    )
    ok = isinstance(parsed, dict) and parsed.get('lab') == 'Cannlytics'
    detail = f'{in_tok} in / {out_tok} out, ${cost:.6f}' if ok else 'FAILED (see the log line above)'
    print(f"  {'ok  ' if ok else 'FAIL'}  {provider:9s} {model:30s} {detail}")
    return ok

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Make one live request per configured AI provider.')
    parser.add_argument('--all-models', action='store_true', help='check every registered model, not only defaults')
    parser.add_argument('--env-file', help='load API keys from this .env file first')
    args = parser.parse_args(argv)
    if args.env_file:
        from dotenv import load_dotenv
        load_dotenv(args.env_file)
    print(f'Registry prices verified {PRICES_VERIFIED}.')
    results = []
    for provider, config in AI_PROVIDERS.items():
        models = list(config['models']) if args.all_models else [config['default_model']]
        for model in models:
            if config['models'][model].get('quarantined'):
                continue
            results.append(check(provider, model))
    failed = results.count(False)
    print('PASSED' if not failed else f'FAILED: {failed} request(s)')
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main())
