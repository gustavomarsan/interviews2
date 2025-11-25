from programs import aritmetic_operations

def test_sum_two_numbersition():
    result = aritmetic_operations.sum_two_numbers(2, 3)
    assert result == 5
    result = aritmetic_operations.sum_two_numbers(-1, 1)
    assert result == 0  
    result = aritmetic_operations.sum_two_numbers(0, 0)
    assert result == 0  
    result = aritmetic_operations.sum_two_numbers(-2, -3)
    assert result == -5

def test_subtraction():
    result = aritmetic_operations.subtract_numbers(5, 3)
    assert result == 2
    result = aritmetic_operations.subtract_numbers(0, 0)
    assert result == 0  
    result = aritmetic_operations.subtract_numbers(-1, -1)
    assert result == 0  
    result = aritmetic_operations.subtract_numbers(-3, -2)
    assert result == -1

def test_multiplication():
    result = aritmetic_operations.multiply_two_numbers(4, 5)
    assert result == 20
    result = aritmetic_operations.multiply_two_numbers(0, 10)
    assert result == 0  
    result = aritmetic_operations.multiply_two_numbers(-2, 3)
    assert result == -6  
    result = aritmetic_operations.multiply_two_numbers(-2, -4)
    assert result == 8

def test_division():
    result = aritmetic_operations.divide_numbers(10, 2)
    assert result == 5
    result = aritmetic_operations.divide_numbers(6, 3)
    assert result == 2  
    result = aritmetic_operations.divide_numbers(-8, 2)
    assert result == -4  
    result = aritmetic_operations.divide_numbers(-9, -3)
    assert result == 3
    result = aritmetic_operations.divide_numbers(8, 0)
    assert result is None