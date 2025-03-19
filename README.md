# Auto Dependency Installer

[![PyPI version](https://badge.fury.io/py/auto-dep-installer.svg)](https://badge.fury.io/py/auto-dep-installer)
[![Python Versions](https://img.shields.io/pypi/pyversions/auto-dep-installer.svg)](https://pypi.org/project/auto-dep-installer/)
[![License](https://img.shields.io/pypi/l/auto-dep-installer.svg)](https://github.com/yourusername/auto_dep_installer/blob/main/LICENSE)

Auto Dependency Installer is a Python package that automatically scans your project's source code for imported modules, detects which ones are missing in your environment, and installs them for you. It can create and use virtual environments to keep your dependencies isolated.

## Installation

Install directly from PyPI:

```bash
pip install auto-dep-installer
```

## Features

- **Virtual Environment Support:** Automatically create and activate virtual environments
- **Automated Scanning:** Recursively scans Python files for import statements
- **Dependency Detection:** Identifies which imported modules are missing
- **Automatic Installation:** Installs missing packages via pip
- **Command-Line Interface:** Simple and intuitive CLI
- **Customizable Mappings:** Support for custom module-to-package mappings

## Quick Start

### Basic Usage

To scan the current directory and install all dependencies in a new virtual environment:

```bash
auto-dep
```

This will:

1. Create a virtual environment named `.venv` in the current directory (if it doesn't exist)
2. Activate the virtual environment
3. Scan for Python files and detect imports
4. Install missing dependencies

### Advanced Usage

Specify a custom virtual environment name:

```bash
auto-dep --venv my_project_env
```

Scan a specific directory:

```bash
auto-dep --directory ./path/to/project
```

Skip virtual environment creation:

```bash
auto-dep --no-venv
```

Use custom module-to-package mappings:

```bash
auto-dep --custom-mappings mappings.json
```

## Command-Line Options

```
usage: auto-dep [-h] [--directory DIRECTORY] [--venv VENV] [--no-venv] [--custom-mappings CUSTOM_MAPPINGS]

Auto Dependency Installer

optional arguments:
  -h, --help            show this help message and exit
  --directory DIRECTORY, -d DIRECTORY
                        Directory to scan for Python files (default: current directory)
  --venv VENV, -v VENV  Virtual environment name/path (default: .venv)
  --no-venv             Skip virtual environment creation/activation
  --custom-mappings CUSTOM_MAPPINGS, -m CUSTOM_MAPPINGS
                        Path to JSON file with custom module-to-package mappings
```

## Custom Mappings

You can provide a JSON file with custom module-to-package mappings:

```json
{
  "custom_module": "custom-package-name",
  "private_pkg": "company-private-package"
}
```

The tool already includes common mappings like:

- `bs4` → `beautifulsoup4`
- `PIL` → `pillow`
- `cv2` → `opencv-python`
- `sklearn` → `scikit-learn`

## Use Cases

- **Quick Prototyping:** Start coding without worrying about dependencies
- **Project Setup:** Quickly set up development environments
- **Onboarding:** Help new team members get your project running
- **Legacy Projects:** Easily identify and install dependencies for older projects

## Known Limitations

- Only top-level imports are detected; dynamic or conditional imports might be missed
- The tool assumes module names match package names (except for known mappings)
- Standard library modules are excluded but some edge cases might exist

## Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Auto Dependency Installer is dual-licensed under the MIT License and the Apache License 2.0. You may choose either license.
