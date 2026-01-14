# Coding conventions

## Overall Guidance and Style
- Do not use `print` in production code. For terminal output, use `logger`.

## Python Version Requirements
- **Target Python Version**: Python 3.13 and above
- **Modern Python Features**: User Python 3.13+ features where appropriate

## Type Annotations:
- Type hints required for all Python code
- **ALWAYS use builtin types for annotations**: `dict`, `list`, `set`, `tuple` instead of `typing.Dict`, `typing.List`, `typing.Set`, `typing.Tuple`
- **NEVER import or use** `typing` module for annotations

## Import Organization
- **ALWAYS use top-level (module-scoped) imported** - avoid function-scoped imports except in specific cases
- Acceptable exceptions for function-scoped imports: 
i. **TYPING_CHECKING blocks**: Imports only needed for type annotations
ii. **Circular import resolution**: When imports would create circular dependencies

```python
# ✅ GOOD: Top-level imports
from aiolimiter import AsyncLimiter

from mezon.api.utils import build_body, build_headers, build_params, parse_response

async def my_function():
    async with AsyncLimiter(max_rate=1, time_period=1.25) as rate_limiter:
        ...
```

```python
# ❌ BAD: Function-scoped imports
from mezon.api.utils import build_body, build_headers, build_params, parse_response

async def my_function():
    from aiolimiter import AsyncLimiter
    async with AsyncLimiter(max_rate=1, time_period=1.25) as rate_limiter:
        ...
```

```python
# ✅ ACCEPTABLE: TYPE_CHECKING imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mezon.api import MezonApi
```

## Use Literal Types for String Enums
**ALWAYS use `Literal` types for string constants that represent enums**
**ALWAYS create type aliases for reusable literal types**

```python
# ✅ GOOD
from typing import Literal

DiagnosticsLevel = Literal["off", "error", "info", "debug"]

def create_service(level: DiagnosticsLevel = "off") -> MyService:
    return MyService(level=level)
```

```python
# ❌ Bad
def create_service(level: str = "off") -> MyService:  # No type safety
    return MyService(level=level)
```

## Docstring Convention

Every function or class must include a PEP 257 compliant docstring:

```python
"""
<Short summary of the function or class.>

Args:
    param1 (type): description
    param2 (type): description

Returns:
    type: description
"""
```

## Package Organization
- **NEVER use __all__ in subpackage __init__.py files**
- **Only use __all__ in top-level package __init__.py files to define public APIs**
- **Rely on absolute imports for internal classes and functions**