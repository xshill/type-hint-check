# type-hint-check.py
This is a small tool to check which parts of your Python 3 code do not have type hinting.
It parses your code using the `ast` module from the standard library and outputs JSON describing the issues.

## Example
Suppose you have the following Python file:

```python
def example_function(a: str, b):
    return a * b

class ExampleClass:
    def example_method(self, a, b):
        if not a or not b:
            return
        
        print(a + b)
```

The tool will produce the following output:

```json
[
    {
        "file": "/home/user/type-hint-check/example.py",
        "report": [
            {
                "type": "function",
                "name": "example_function",
                "line": 1,
                "column": 0,
                "issues": [
                    "Missing type hint for return value",
                    "Missing type hint for 'b'"
                ]
            },
            {
                "type": "function",
                "name": "example_method",
                "line": 5,
                "column": 4,
                "issues": [
                    "Missing type hint for 'a'",
                    "Missing type hint for 'b'"
                ]
            }
        ]
    }
]
```

Notice it didn't flag the lack of return type for `example_method`, since it doesn't actually return anything.

## Usage
The simplest use case is to just check one file:

```
type-hint-check.py code.py
```

You can check multiple files:

```
type-hint-check.py module_a.py module_b.py
```

You can recursively check directories with the `-r` flag:

```
type-hint-check.py -r module/
```

You can also mix files and directories:

```
type-hint-check.py -r lib/ main.py test.py
```