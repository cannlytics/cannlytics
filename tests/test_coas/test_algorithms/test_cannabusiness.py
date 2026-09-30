"""
Validation & regression tests for cannabusiness.py
(CannaBusiness Laboratories COA parser).

Encodes the Kentucky-integration-guide doctrine fixtures for CannaBusiness:
    - two page-1 layouts (full-panel cover vs. biomass OBR header)
    - strain resolved from the non-Metrc-tag field (null for tag-only biomass)
    - dual %/mg-g rows collapsed into one record (both units captured)
    - APCI + ESI pesticide panels merged
    - biomass total THC via the 0.877 decarb fallback
    - null-vs-zero (ND/<LOQ/>ULOL/NT -> None, never 0.0)
    - a legitimate measured zero (E.coli 0 CFUs) is preserved as 0.0
    - Sample-Type-driven panel scope (biomass = potency + pesticides only)
    - failing results preserved; overall status reflects any Fail

Run:
    python test_cannabusiness.py          # pytest-free, self-contained
    pytest test_cannabusiness.py -v       # or under pytest
"""
import json
import os
import sys

import pytest

from cannlytics.data.coas.algorithms import cannabusiness as cb

HERE = os.path.dirname(os.path.abspath(__file__))
CB = os.path.join(HERE, 'cb')

# The fixtures are real Kentucky COA PDFs, kept out of the repository
# and every distribution (see MANIFEST.in). Without them, skip.
pytestmark = [
    pytest.mark.fixtures,
    pytest.mark.skipif(not os.path.isdir(CB), reason='local COA fixtures (cb/) not present'),
]

# Full-panel (Buds) COAs -- Emerald Fire, Goeing Blue.
BUDS_0029 = os.path.join(CB, 'KY-2025-11-26_21-45-57-1A4220100000001000000029_1.pdf')
BUDS_0030 = os.path.join(CB, 'KY-2025-11-26_21-46-19-1A4220100000001000000030_1.pdf')
BUDS_0031 = os.path.join(CB, 'KY-2025-11-26_21-46-45-1A4220100000001000000031_1.pdf')
BUDS_0042 = os.path.join(CB, 'KY-2025-11-26_21-49-18-1A4220100000001000000042_1.pdf')
# Biomass COAs -- Goeing Blue (limited panel, no cover, tag-only strain).
BIO_0018 = os.path.join(CB, 'KY-2025-11-25_11-15-38-1A4220100000001000000018_1.pdf')
BIO_0026 = os.path.join(CB, 'KY-2025-11-25_17-15-53-1A4220100000001000000026_1.pdf')

_cache = {}

def parse(fp):
    if fp not in _cache:
        _cache[fp] = cb.parse_cannabusiness_coa(None, fp)
    return _cache[fp]

def results(fp):
    return json.loads(parse(fp)['results'])

def by_key(fp, analysis, key):
    for r in results(fp):
        if r['analysis'] == analysis and r['key'] == key:
            return r
    return None

# ── Lab identity ───────────────────────────────────────────────────

def test_lab_identity():
    d = parse(BUDS_0029)
    assert d['lab'] == 'CannaBusiness Laboratories'
    assert d['lab_license_number'] == 'P_0059'
    assert d['lab_state'] == 'KY'
    assert d['lab_legal_entity'] == 'Aquatic Laboratories LLC'
    assert cb.is_cannabusiness(BUDS_0029)
    assert cb.is_cannabusiness(BIO_0018)

# ── Layout detection ───────────────────────────────────────────────

def test_full_panel_layout_detected():
    assert parse(BUDS_0029)['coa_layout'] == 'full'

def test_biomass_layout_detected():
    assert parse(BIO_0018)['coa_layout'] == 'biomass'

# ── Strain resolution (non-Metrc-tag field) ────────────────────────

def test_strain_from_external_sample_id():
    # Buds: Sample Name is the Metrc tag; strain is the External Sample ID.
    assert parse(BUDS_0029)['strain_name'] == 'Emerald Fire 11.02.25 MB Auto'
    assert parse(BUDS_0030)['strain_name'] == 'Emerald Fire 11.3.25 HB Auto'

def test_strain_null_for_tag_only_biomass():
    # Biomass: both name fields are Metrc tags -> strain must be None,
    # never a guessed value.
    assert parse(BIO_0018)['strain_name'] is None
    assert parse(BIO_0026)['strain_name'] is None

def test_sample_name_is_metrc_tag():
    d = parse(BUDS_0029)
    assert d['sample_name'].startswith('1A4')
    assert d['metrc_id'] == d['sample_name']

# ── Metadata (producer / dates / ids) ──────────────────────────────

def test_producer_extracted_not_lab():
    for fp in (BUDS_0029, BIO_0018):
        d = parse(fp)
        assert d['producer'] == 'Goeing Blue LLC'
        assert d['producer_license_number'] == 'CULT0001034'
        assert d['producer_city'] == 'Lexington'

def test_ids_and_dates():
    d = parse(BUDS_0029)
    assert d['sample_id'] == '251119021'
    assert d['batch_number'] == '1A4220100000001000000011'
    assert d['date_collected'] == '11/13/2025'
    assert d['date_received'] == '11/19/2025'
    assert d['date_tested'] == '11/26/2025'

def test_sample_type_and_product_type():
    assert parse(BIO_0018)['sample_type'] == 'Biomass'
    assert parse(BIO_0018)['product_type'] == 'biomass'
    assert parse(BUDS_0029)['sample_type'] == 'Buds'

# ── Panel scope driven by sample type ──────────────────────────────

def test_biomass_limited_panel():
    # Biomass ran potency (+ moisture) + pesticides ONLY. The microbial,
    # metals, mycotoxin, terpene, and water-activity panels were not run
    # and must be absent (null), never zero-filled.
    got = set(json.loads(parse(BIO_0018)['analyses']))
    assert got == {'cannabinoids', 'pesticides', 'moisture'}, got
    # Water activity was NOT run on biomass -> no such analysis / row.
    assert 'water_activity' not in got
    assert by_key(BIO_0018, 'water_activity', 'water_activity') is None

def test_full_panel_all_analyses():
    got = set(json.loads(parse(BUDS_0029)['analyses']))
    expected = {'cannabinoids', 'terpenes', 'heavy_metals', 'pesticides',
                'mycotoxins', 'microbials', 'moisture', 'water_activity'}
    assert expected <= got, expected - got

def test_moisture_emitted_as_result_row():
    # Moisture must be a RESULT ROW (key 'moisture_content'), not only a
    # scalar -- the parse cache drops non-canonical scalars, and
    # agg_results promotes moisture_content from the results array.
    for fp in (BIO_0018, BUDS_0029):
        row = by_key(fp, 'moisture', 'moisture_content')
        assert row is not None, f'no moisture_content row in {fp}'
        assert isinstance(row['value'], (int, float))
        assert row['units'] == 'percent'

def test_water_activity_emitted_on_full_panel():
    # Water Activity row must be captured on full-panel COAs (the header
    # and the data row share the text 'Water Activity' -- the data row
    # must not be swallowed as a header).
    wa = by_key(BUDS_0029, 'water_activity', 'water_activity')
    assert wa is not None, 'water_activity row missing on full-panel COA'
    assert 0.0 < wa['value'] < 1.0
    assert wa['status'] == 'Pass'

def test_moisture_water_promote_downstream():
    # Simulate agg_results.extract_moisture_water_activity: it scans result
    # rows by key. Confirm the promotion would recover both scalars.
    def promote(fp):
        m = w = None
        for r in results(fp):
            k = str(r.get('key', '')).lower().replace(' ', '_').replace('-', '_')
            v = r.get('value')
            if v in (None, 0.0):
                continue
            if k in ('moisture_content', 'moisture', 'loss_on_drying'):
                m = v
            elif k in ('water_activity', 'aw', 'a_w'):
                w = v
        return m, w
    m, w = promote(BUDS_0029)
    assert m is not None and w is not None, (m, w)
    mb, wb = promote(BIO_0018)
    assert mb is not None and wb is None  # biomass: moisture only

# ── Dual %/mg-g collapse ───────────────────────────────────────────

def test_dual_unit_collapse_cannabinoids():
    thca = by_key(BUDS_0029, 'cannabinoids', 'thca')
    assert thca['value'] == 29.61          # % Dry Weight
    assert thca['value_mg_g'] == 296.1     # mg/g
    assert thca['units'] == 'percent'
    # One record per analyte (not two).
    cann = [r for r in results(BUDS_0029) if r['analysis'] == 'cannabinoids']
    keys = [r['key'] for r in cann]
    assert len(keys) == len(set(keys)), 'duplicate cannabinoid records'

def test_dual_unit_collapse_terpenes():
    lin = by_key(BUDS_0029, 'terpenes', 'linalool')
    assert lin['value'] == 0.114
    assert lin['value_mg_g'] == 1.137

# ── NULL vs ZERO doctrine ──────────────────────────────────────────

def test_nd_serializes_null_both_units():
    cbc = by_key(BUDS_0029, 'cannabinoids', 'cbc')
    assert cbc['value'] is None
    assert cbc['value_mg_g'] is None
    assert cbc['result_raw'] == 'ND'

def test_below_loq_serializes_null_flagged():
    bis = by_key(BUDS_0029, 'terpenes', 'alpha_bisabolol')
    assert bis['value'] is None
    assert bis['result_raw'] == '<LOQ'

def test_nt_pesticide_serializes_null():
    # Captan / Chlordane are NT on the APCI panel.
    captan = by_key(BUDS_0029, 'pesticides', 'captan')
    assert captan is not None
    assert captan['value'] is None
    assert captan['result_raw'] == 'NT'

def test_no_zero_leak_from_nondetects():
    # No cannabinoid / terpene / pesticide non-detect may leak as 0.0.
    for r in results(BUDS_0029):
        if r['analysis'] in ('cannabinoids', 'terpenes', 'pesticides'):
            if r['result_raw'] in ('ND', '<LOQ', '>ULOL', 'NT'):
                assert r['value'] is None, r

def test_measured_zero_preserved():
    # E.coli by Plating is a genuine measured 0 (0 CFUs, Pass) -- this is
    # a legitimate zero and MUST be preserved, not nulled.
    ecoli = by_key(BUDS_0029, 'microbials', 'total_ecoli')
    assert ecoli['value'] == 0.0
    assert ecoli['status'] == 'Pass'

# ── Pesticides: APCI + ESI merged ──────────────────────────────────

def test_pesticides_both_panels_merged():
    pest = [r for r in results(BUDS_0029) if r['analysis'] == 'pesticides']
    names = {r['key'] for r in pest}
    # APCI-only analyte:
    assert 'acequinocyl' in names
    # MGK-264 isomers must be two distinct records (no key collision).
    assert 'mgk_264_20_1' in names and 'mgk_264_79_9' in names
    # ESI analytes:
    assert 'trifloxystrobin' in names
    assert 'abamectinb1a' in names or any('abamectin' in k for k in names)
    # No duplicate keys within pesticides.
    keys = [r['key'] for r in pest]
    assert len(keys) == len(set(keys)), 'duplicate pesticide records'

# ── Totals & decarboxylation ───────────────────────────────────────

def test_full_panel_prints_total_thc():
    # Full-panel cover prints Total Potential THC directly.
    assert parse(BUDS_0029)['total_thc'] == 26.20
    assert parse(BUDS_0029)['total_cbd'] == 0.064
    assert parse(BUDS_0029)['total_cbg'] == 1.399
    assert parse(BUDS_0029)['total_cannabinoids'] == 31.49

def test_biomass_total_thc_decarb_fallback():
    # Biomass prints NO Total Potential THC -> compute 0.877*THCa + d9.
    # File ...018: THCa=24.26, d9=0.119 -> 0.877*24.26 + 0.119 = 21.395
    d = parse(BIO_0018)
    thca = by_key(BIO_0018, 'cannabinoids', 'thca')['value']
    d9 = by_key(BIO_0018, 'cannabinoids', 'delta_9_thc')['value']
    assert thca == 24.26 and d9 == 0.119
    assert abs(d['total_thc'] - (0.877 * thca + d9)) <= 0.001
    assert abs(d['total_thc'] - 21.395) <= 0.01

def test_decarb_helper_matches_printed_full_panel():
    # For a full-panel COA the decarb helper must reproduce the printed
    # cover total (0029: 0.877*29.61 + 0.231 = 26.20).
    computed = cb._compute_total_thc(results(BUDS_0029))
    assert abs(computed - 26.20) <= 0.02, computed

def test_biomass_total_cbg_decarb():
    # Total Potential CBG = 0.877*CBGa + CBG on biomass (no printed value).
    # File ...018: CBGa=0.616, CBG=0.155 -> 0.877*0.616 + 0.155 = 0.6952
    d = parse(BIO_0018)
    cbga = by_key(BIO_0018, 'cannabinoids', 'cbga')['value']
    cbg = by_key(BIO_0018, 'cannabinoids', 'cbg')['value']
    assert cbga == 0.616 and cbg == 0.155
    assert abs(d['total_cbg'] - (0.877 * cbga + cbg)) <= 0.001
    assert abs(d['total_cbg'] - 0.6952) <= 0.001

# ── Microbials (qualitative + quantitative) ────────────────────────

def test_microbials_qualitative_and_quantitative():
    # Aspergillus via qPCR (Negative -> Not Detected, Pass).
    asp = by_key(BUDS_0029, 'microbials', 'pathogenic_aspergillus')
    assert asp['qualitative'] == 'Not Detected'
    assert asp['status'] == 'Pass'
    # Yeast & Mold quantitative (2759 CFUs, Pass).
    ym = by_key(BUDS_0029, 'microbials', 'yeast_and_mold')
    assert ym['value'] == 2759.0
    assert ym['status'] == 'Pass'
    # STEC qualitative negative.
    stec = by_key(BUDS_0029, 'microbials', 'stec')
    assert stec['qualitative'] == 'Not Detected'

# ── Overall status ─────────────────────────────────────────────────

def test_microbials_qualitative_status_derived():
    # Every microbial row must carry a Pass/Fail status so the downstream
    # per-analyte rollup is complete. Bare qualitative rows (e.g. Listeria)
    # derive Pass from 'Not Detected'.
    micro = [r for r in results(BUDS_0029) if r['analysis'] == 'microbials']
    assert micro, 'no microbial rows'
    assert all(r.get('status') in ('Pass', 'Fail') for r in micro), \
        [r['key'] for r in micro if r.get('status') not in ('Pass', 'Fail')]
    listeria = by_key(BUDS_0029, 'microbials', 'listeria_monocytogenes')
    assert listeria['qualitative'] == 'Not Detected'
    assert listeria['status'] == 'Pass'

def test_overall_status_pass():
    # All sample COAs in this batch pass.
    assert parse(BUDS_0029)['status'] == 'pass'
    assert parse(BIO_0018)['status'] == 'pass'

# ── Serialization contract ─────────────────────────────────────────

def test_serialization_contract():
    d = parse(BUDS_0029)
    # analyses & results are JSON strings; core metadata at top level.
    assert isinstance(d['analyses'], str)
    assert isinstance(d['results'], str)
    assert isinstance(json.loads(d['analyses']), list)
    assert isinstance(json.loads(d['results']), list)
    assert d['coa_algorithm_entry_point'] == 'parse_cannabusiness_coa'
    assert d['lab_id'] == d['sample_id']

# ── Runner ─────────────────────────────────────────────────────────

def _run():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith('test_') and callable(v)]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f'  PASS  {t.__name__}')
            passed += 1
        except AssertionError as e:
            print(f'  FAIL  {t.__name__}: {e}')
            failed += 1
        except Exception as e:
            print(f'  ERROR {t.__name__}: {type(e).__name__}: {e}')
            failed += 1
    print(f'\n{passed}/{passed + failed} tests passed'
          + (f', {failed} FAILED' if failed else ''))
    return failed == 0

if __name__ == '__main__':
    sys.exit(0 if _run() else 1)
