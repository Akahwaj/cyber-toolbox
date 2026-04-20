```markdown
# cyber-toolbox Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `cyber-toolbox` Python repository. You'll learn how to structure files, write imports and exports, and follow the project's unique coding and commit styles. This guide also covers how to recognize and write tests, even though no formal workflow automation is detected.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.

  **Example:**
  ```
  cyber_utils.py
  password_generator.py
  ```

### Import Style
- Use **relative imports** within the package.

  **Example:**
  ```python
  from .crypto_utils import encrypt_data
  from . import network_scanner
  ```

### Export Style
- Use **named exports** (explicitly specify what to export).

  **Example:**
  ```python
  __all__ = ['scan_network', 'encrypt_data']
  ```

### Commit Patterns
- Commit messages are **freeform** (no strict prefixes).
- Average commit message length: ~43 characters.

  **Example:**
  ```
  Add port scanning feature to network scanner
  Fix bug in password generator
  ```

## Workflows

### Adding a New Tool Module
**Trigger:** When you want to add a new utility or tool to the cyber-toolbox.
**Command:** `/add-tool-module`

1. Create a new Python file using snake_case (e.g., `hash_cracker.py`).
2. Implement your module logic.
3. Use relative imports for any internal dependencies.
4. Add your module's main functions or classes to `__all__`.
5. Write a corresponding test file (see Testing Patterns).

### Running Tests
**Trigger:** When you want to verify your code works as expected.
**Command:** `/run-tests`

1. Locate test files matching the `*.test.*` pattern (e.g., `network_scanner.test.py`).
2. Run the tests using your preferred Python test runner (e.g., `pytest`, `unittest`).
3. Review output for failures or errors.

### Refactoring Imports
**Trigger:** When reorganizing code or resolving import issues.
**Command:** `/refactor-imports`

1. Ensure all internal imports are relative (e.g., `from .module import func`).
2. Avoid absolute imports for modules within the package.
3. Update `__all__` as needed to reflect exported functions/classes.

## Testing Patterns

- Test files follow the pattern: `*.test.*` (e.g., `crypto_utils.test.py`).
- The testing framework is **unknown**; use standard Python testing practices.
- Place tests in the same directory as the code or in a dedicated `tests/` directory.
- Each test file should import the module using relative imports.

  **Example:**
  ```python
  from .crypto_utils import encrypt_data

  def test_encrypt_data():
      assert encrypt_data('secret') != 'secret'
  ```

## Commands
| Command           | Purpose                                      |
|-------------------|----------------------------------------------|
| /add-tool-module  | Scaffold and add a new tool module           |
| /run-tests        | Run all test files in the repository         |
| /refactor-imports | Refactor and check for proper import styles  |
```
