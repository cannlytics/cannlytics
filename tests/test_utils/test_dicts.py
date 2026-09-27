"""
Tests for dictionary and list utilities in cannlytics.utils.utils
==================================================================
Covers: clean_dictionary, clean_nested_dictionary, remove_dict_fields,
remove_dict_nulls, update_dict, sorted_nicely, split_list, dump_column.
"""
import json
import pytest

from cannlytics.utils.utils import (
    clean_dictionary,
    clean_nested_dictionary,
    remove_dict_fields,
    remove_dict_nulls,
    update_dict,
    sorted_nicely,
    split_list,
    dump_column,
)

class TestCleanDictionary:

    def test_snake_cases_keys(self):
        result = clean_dictionary({'First Name': 'Keegan', 'Last Name': 'Skeate'})
        assert 'first_name' in result
        assert 'last_name' in result

    def test_custom_function(self):
        result = clean_dictionary({'a': 1, 'b': 2}, function=str.upper)
        assert 'A' in result and 'B' in result

class TestCleanNestedDictionary:

    def test_nested_dicts(self):
        data = {'User Info': {'First Name': 'Keegan'}}
        result = clean_nested_dictionary(data)
        assert 'user_info' in result
        assert 'first_name' in result['user_info']

    def test_list_of_dicts(self):
        data = {'Items': [{'Item Name': 'A'}, {'Item Name': 'B'}]}
        result = clean_nested_dictionary(data)
        assert 'items' in result
        assert result['items'][0]['item_name'] == 'A'

    def test_non_dict_values_preserved(self):
        data = {'Tags': ['a', 'b', 'c']}
        result = clean_nested_dictionary(data)
        assert result['tags'] == ['a', 'b', 'c']

class TestRemoveDictFields:

    def test_removes_specified_keys(self):
        data = {'a': 1, 'b': 2, 'c': 3}
        result = remove_dict_fields(data, ['a', 'c'])
        assert result == {'b': 2}

    def test_missing_keys_ignored(self):
        data = {'a': 1}
        result = remove_dict_fields(data, ['nonexistent'])
        assert result == {'a': 1}

class TestRemoveDictNulls:

    def test_removes_none_values(self):
        data = {'a': 1, 'b': None, 'c': 'val', 'd': None}
        result = remove_dict_nulls(data)
        assert result == {'a': 1, 'c': 'val'}

    def test_empty_dict(self):
        assert remove_dict_nulls({}) == {}

    def test_preserves_falsy_non_none(self):
        data = {'a': 0, 'b': '', 'c': False, 'd': None}
        result = remove_dict_nulls(data)
        assert 'a' in result and 'b' in result and 'c' in result
        assert 'd' not in result

class TestUpdateDict:

    def test_merges_kwargs(self):
        result = update_dict({'existing': 'val'}, name='Keegan')
        assert 'name' in result
        assert 'existing' in result

class TestSortedNicely:

    def test_natural_sort(self):
        items = ['item10', 'item2', 'item1', 'item20']
        result = sorted_nicely(items)
        assert result == ['item1', 'item2', 'item10', 'item20']

    def test_alphabetical(self):
        result = sorted_nicely(['banana', 'apple', 'cherry'])
        assert result == ['apple', 'banana', 'cherry']

class TestSplitList:

    def test_split_in_half(self):
        first, second = split_list([1, 2, 3, 4])
        assert first == [1, 2]
        assert second == [3, 4]

    def test_split_at_index(self):
        first, second = split_list([1, 2, 3, 4, 5], at_index=1)
        assert first == [1]
        assert second == [2, 3, 4, 5]

    def test_empty_list(self):
        first, second = split_list([])
        assert first == [] and second == []

class TestDumpColumn:

    def test_valid_json(self):
        assert dump_column('{"key": 1}') == {'key': 1}

    def test_invalid_returns_none(self):
        assert dump_column('not json') is None

    def test_none_input(self):
        assert dump_column(None) is None
