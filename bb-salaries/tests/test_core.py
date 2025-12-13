from bb_salaries import add_one, calculate_mean
import pytest

def test_add_one(): 
    assert add_one(2) == 3

mean_data = [([5], 5.0),
                ([1, 2, 3, 4], 2.5),
                ([10, 20, 30], 20.0)]
@pytest.mark.parametrize("x, expected", mean_data)
def test_calculate_mean(x, expected):
    assert calculate_mean(x) == expected
