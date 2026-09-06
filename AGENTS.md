# Project Guidelines & Rules

## Workspace Boundaries & Privacy
- **Strict Workspace Boundary**: Never search, list, read, or access files or directories outside the project repository (`/Users/baart_f/src/D-SLF`). Never run `find`, `ls`, or glob commands across `~`, `~/Downloads`, `~/Desktop`, or other repositories. If any file, dataset, or information from outside the workspace is needed, always stop and ask the user directly.

## Execution & Testing
- Always use `uv` to run tests and execute Python scripts (e.g. `uv run pytest`, `uv run python ...`).
- Use `click` for building CLI scripts.
- Use `pathlib` for all filesystem path operations instead of `os.path`.

## Coding Principles
- **Fail Fast**: Remove defensive fallbacks, speculative existence checks, and error-swallowing try-except blocks. Allow failures to surface immediately and clearly when expectations are not met.
- **Early Returns / Guard Clauses**: Check for negative conditions and return or continue early rather than nesting deep conditional blocks.
- **Maintain Assistant Boundary**: Never claim authorship, co-authorship, or sign commit messages, memos, or code. All authorship belongs solely to the user.
