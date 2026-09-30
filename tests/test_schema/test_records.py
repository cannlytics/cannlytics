"""
Tests for cannlytics.schema
===========================
The records moved from the COA parser's schema; these tests pin that
the move changed nothing a stored record depends on.
"""
import ast
import hashlib
import json
import pathlib
import sys
from datetime import datetime

from cannlytics import schema
from cannlytics.schema import VALIDATION_RULES, LabResult, ResultDetail, validate_result

def test_one_class_two_paths():
    from cannlytics.data.coas import schema as parser_schema
    assert parser_schema.LabResult is LabResult and parser_schema.ResultDetail is ResultDetail
    assert parser_schema.validate_result is validate_result and parser_schema.VALIDATION_RULES is VALIDATION_RULES

def test_imports_only_the_standard_library_and_hashing():
    tree = ast.parse(pathlib.Path(schema.__file__).read_text(encoding='utf-8'))
    roots = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.level == 0}
    roots |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    assert {r for r in roots if r.split('.')[0] not in sys.stdlib_module_names} == {'cannlytics.utils.hashing'}

def test_111_fields():
    from dataclasses import fields
    assert len(fields(LabResult)) == 111

def test_id_and_hash_are_the_original_derivations():
    record = LabResult(state='ky', product_name='Blue Dream', producer='Acme Farms',
                       batch_number='B-1', total_thc=21.4, date_tested=datetime(2026, 9, 1))
    key = f"{record.product_name}{record.producer}{record.batch_number}{record.date_tested}"
    assert record.id == hashlib.sha256(key.encode()).hexdigest()[:16]
    data = {'product_name': 'Blue Dream', 'producer': 'Acme Farms', 'batch_number': 'B-1',
            'total_thc': 21.4, 'date_tested': str(record.date_tested)}
    assert record.sample_hash == hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def test_round_trip_and_validation():
    record = LabResult(state='ky', product_name='Blue Dream', total_thc=21.4)
    assert LabResult.from_dict(record.to_dict()).to_dict() == record.to_dict()
    assert validate_result(record) == (True, [])
