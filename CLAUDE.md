# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: League of Legends Sitemap Scraper

### Commands
- Build: N/A (Python script)
- Run: `python scraper.py`
- Lint: `flake8`
- Type check: `mypy .`
- Test: `pytest`
- Single test: `pytest tests/test_filename.py::test_function_name -v`

### Code Style Guidelines
- **Formatting**: Use Black with default settings
- **Imports**: Group standard library, third-party, and local imports
- **Types**: Use type hints for function parameters and return values
- **Naming**: Use snake_case for variables/functions, PascalCase for classes
- **Error Handling**: Use try/except blocks with specific exceptions
- **Documentation**: Use docstrings for functions and classes
- **Line Length**: Maximum 88 characters
- **Data Parsing**: Use proper XML parsing libraries (ElementTree or BeautifulSoup)
- **HTTP Requests**: Use aiohttp for asynchronous requests or requests library