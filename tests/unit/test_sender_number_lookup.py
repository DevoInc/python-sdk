import pytest

from devo.sender import Lookup


def test_check_is_number():
    assert Lookup.is_number("5")
    assert Lookup.is_number("5.0")


def test_check_is_not_a_number():
    assert not Lookup.is_number(
        "5551,HNBId=001D4C-1213120051,Fsn=1213120051,bSRName=,manualPscUsed=false"
    )
    assert not Lookup.is_number("5.")
    assert not Lookup.is_number("5,0")


def test_process_fields_does_not_modify_arguments():
    fields = ["a", "b", "c"]
    processed_fields = Lookup.process_fields(fields, key_index=1)

    assert fields == ["a", "b", "c"]
    assert processed_fields == '"b","a","c"'


# Clean field
@pytest.mark.parametrize(
    "field, escape_quotes, expected_result",
    [
        ("No double quotes", False, '"No double quotes"'),
        ("No double quotes", True, '"No double quotes"'),
        ('Double quotes"', False, '"Double quotes""'),
        ('Double quotes"', True, '"Double quotes"""'),
    ],
)
def test_clean_field_parametrized(field, escape_quotes, expected_result):
    result = Lookup.clean_field(field, escape_quotes)
    assert result == expected_result


if __name__ == "__main__":
    pytest.main()
