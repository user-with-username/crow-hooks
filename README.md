# Crow Hooks

Python hook system for the Crow build system.

## Installation

```bash
pip install crow-hooks
```

## Usage
```python
from crow_hooks import ctx

def pre_build():
    print(f"Building project: {ctx.project_root}")
    print(f"Sources: {ctx.sources}")
    
    # Run custom commands
    ctx.run(["echo", "Pre-build hook executed"])
    
    # Compile targets
    ctx.compile_target("my_tool", ["tools/my_tool.cpp"])
```

## License

MIT