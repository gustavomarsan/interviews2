import pytest
from programs import aritmetic_operations

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (-2, -3, -5),
])
def test_sum_two_numbersition(a, b, expected):
    assert aritmetic_operations.sum_two_numbers(a, b) == expected



@pytest.mark.parametrize("a,b,expected", [
    (5, 3, 2),
    (0, 0, 0),
    (-1, -1, 0),
    (-3, -2, -1),
])
def test_subtraction(a, b, expected):
    assert aritmetic_operations.subtract_numbers(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [
    (4, 5, 20),
    (0, 10, 0),
    (-2, 3, -6),
    (-2, -4, 8),
])
def test_multiplication(a, b, expected):
    assert aritmetic_operations.multiply_two_numbers(a, b) == expected



@pytest.mark.parametrize("a,b,expected", [
    (10, 2, 5),
    (6, 3, 2),
    (-8, 2, -4),
    (-9, -3, 3),
    (8, 0, None),
])

def test_division(a, b, expected):
    assert aritmetic_operations.divide_numbers(a, b) == expected