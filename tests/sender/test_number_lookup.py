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


if __name__ == "__main__":
    pytest.main()
