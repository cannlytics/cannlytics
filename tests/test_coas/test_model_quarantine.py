"""No quarantined model may be a provider default (null-versus-zero doctrine)."""
import pytest

from cannlytics.data.coas.config import AI_PROVIDERS

@pytest.mark.parametrize('provider', sorted(AI_PROVIDERS))
def test_default_model_is_not_quarantined(provider):
    config = AI_PROVIDERS[provider]
    assert not config['models'][config['default_model']].get('quarantined', False)

def test_gpt_5_nano_is_quarantined_but_still_selectable():
    models = AI_PROVIDERS['openai']['models']
    assert models['gpt-5-nano']['quarantined'] is True
    assert AI_PROVIDERS['openai']['default_model'] != 'gpt-5-nano'
