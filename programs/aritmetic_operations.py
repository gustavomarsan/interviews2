def sum_two_numbers(a, b):
    return a + b

def multiply_two_numbers(a, b):
    return a * b

def subtract_numbers(a, b):
    return a - b

def divide_numbers(a, b):
    if b == 0:
        print("Cannot divide by zero.")
        return  None
    return int(a / b)


print(sum_two_numbers(5, 3))          # Output: 8
print(multiply_two_numbers(5, 3))     # Output: 15
print(subtract_numbers(5, 3))     # Output: 2
print(divide_numbers(6, 2))       # Raises ValueError   # Output: Cannot divide by zero.    