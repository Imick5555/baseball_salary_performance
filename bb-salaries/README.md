# hello-uv-yourname
A tiny demo package for learning Python packaging.
## Description
This package demonstrates:
- Basic functions (`add_one`)
- Functions with dependencies (`calculate_mean` using numpy)
- Proper project structure with tests
- Modern packaging with `uv`

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Development

Use the repo-local virtual environment and install dev dependencies:

```powershell
# from the project folder (bb-salaries)
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install -U pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -e .[dev]
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
# This package is not yet finished
