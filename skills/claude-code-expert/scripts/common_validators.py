"""
Common validation functions for Claude Code components
Shared utilities to avoid code duplication
Stdlib only - no external dependencies
"""

import re


def extract_frontmatter(content):
    """
    Extract YAML frontmatter from markdown content

    Args:
        content: Markdown file content as string

    Returns:
        str: YAML frontmatter content (between ---) or None if not found
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        return None
    return match.group(1)


def parse_simple_yaml(yaml_content):
    """
    Parse simple YAML frontmatter (key: value format only)
    Does NOT support nested objects, lists, or multiline values

    Args:
        yaml_content: YAML string to parse

    Returns:
        dict: Parsed fields as {key: value} strings
    """
    fields = {}
    for line in yaml_content.split("\n"):
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue
        # Parse key: value
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            fields[key] = value
    return fields


def validate_no_trailing_commas(value, field_name):
    """
    Check if a field value has trailing commas

    Args:
        value: Field value to check
        field_name: Name of field (for error message)

    Returns:
        str|None: Error message if trailing comma found, None otherwise
    """
    if value.strip().endswith(","):
        return f"ERROR: Campo '{field_name}' no debe terminar en coma"
    return None


def validate_tools_field(tools_value):
    """
    Validate 'tools' field in frontmatter

    Args:
        tools_value: Value of 'tools' field

    Returns:
        tuple: (errors, warnings) lists
    """
    errors = []
    warnings = []

    # Check for trailing comma
    trailing_comma_error = validate_no_trailing_commas(tools_value, "tools")
    if trailing_comma_error:
        errors.append(trailing_comma_error)

    # Check for quotes around values
    if '"' in tools_value or "'" in tools_value:
        warnings.append(
            "WARNING: Campo 'tools' no debe tener comillas alrededor de los valores"
        )

    return errors, warnings


def validate_allowed_tools_field(tools_value):
    """
    Validate 'allowed-tools' field in command frontmatter

    Args:
        tools_value: Value of 'allowed-tools' field

    Returns:
        tuple: (errors, warnings) lists
    """
    errors = []
    warnings = []

    # Check for trailing comma
    trailing_comma_error = validate_no_trailing_commas(tools_value, "allowed-tools")
    if trailing_comma_error:
        errors.append(trailing_comma_error)

    # Validate Bash patterns (e.g., Bash(git add:*))
    if "Bash(" in tools_value:
        bash_patterns = re.findall(r"Bash\([^)]+\)", tools_value)
        for pattern in bash_patterns:
            if not re.match(r"Bash\(.+\)", pattern):
                errors.append(f"ERROR: Patrón Bash mal formado: {pattern}")

    return errors, warnings


def validate_model_field(model_value, valid_models):
    """
    Validate 'model' field value

    Args:
        model_value: Value of 'model' field
        valid_models: List of valid model names

    Returns:
        str|None: Error message if invalid, None otherwise
    """
    if model_value not in valid_models:
        return f"ERROR: 'model' debe ser uno de {valid_models}: {model_value}"
    return None


def validate_file_exists(file_path):
    """
    Check if file exists

    Args:
        file_path: Path to file

    Returns:
        str|None: Error message if not found, None otherwise
    """
    import os

    if not os.path.exists(file_path):
        return f"ERROR: Archivo no encontrado: {file_path}"
    return None


def validate_utf8_encoding(file_path):
    """
    Check if file is valid UTF-8

    Args:
        file_path: Path to file

    Returns:
        str|None: Error message if not UTF-8, None otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.read()
        return None
    except UnicodeDecodeError as e:
        return f"ERROR: Archivo no es UTF-8 válido: {e}"


def validate_kebab_case(name, max_length=None):
    """
    Check if name follows kebab-case convention

    Args:
        name: Name to validate
        max_length: Optional maximum length

    Returns:
        list: Error messages (empty if valid)
    """
    errors = []

    if not re.match(r"^[a-z0-9-]+$", name):
        errors.append(f"ERROR: '{name}' debe usar kebab-case (lowercase, hyphens)")

    if max_length and len(name) > max_length:
        errors.append(
            f"ERROR: '{name}' no puede exceder {max_length} caracteres: {len(name)}"
        )

    return errors


def validate_snake_case_filename(filename):
    """
    Check if filename follows snake_case convention

    Args:
        filename: Filename to validate (without path)

    Returns:
        str|None: Error message if invalid, None otherwise
    """
    # Remove extension
    name_without_ext = filename.rsplit(".", 1)[0]

    if not re.match(r"^[a-z0-9_]+$", name_without_ext):
        return f"ERROR: '{filename}' debe usar snake_case (lowercase, underscores)"
    return None
