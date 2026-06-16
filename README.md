# Calculator

A simple Python calculator utlity with basic arithmetic operations.

## Fuctions

- `add(a, b)` — returns the sum of a and b
- `subtract(a, b)` — returns the diference of a and b
- `multiply(a, b)` — returns the product of a and b
- `divide(a, b)` — returns the quotient of a and b

## Usage

```python
from calculator import add, subtract, multiply, divide

print(add(10, 5))       # 15
print(subtract(10, 5))  # 5
print(multiply(10, 5))  # 50
print(divide(10, 5))    # 2.0
```

## Notes

- Divison by zero raises a `ValueError`
