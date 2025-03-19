# auto_dep_installer/auto_dep_installer/scanner.py

import ast
import os
import re
import logging
from pathlib import Path

logger = logging.getLogger('auto_dep_installer')

class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements."""
    
    def __init__(self):
        self.imports = set()
    
    def visit_Import(self, node):
        """Visit an Import node."""
        for name in node.names:
            self.imports.add(name.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit an ImportFrom node."""
        if node.level == 0:  # absolute import
            self.imports.add(node.module)
        self.generic_visit(node)

def extract_imports_from_file(file_path):
    """Extract import statements from a Python file."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        try:
            content = file.read()
            tree = ast.parse(content)
            visitor = ImportVisitor()
            visitor.visit(tree)
            imports = visitor.imports
            
            # Also look for imports in strings that might be used in exec() or similar
            # This is a simple regex approach and might miss some cases
            pattern = r'(?:import|from)\s+([a-zA-Z0-9_\.]+)'
            string_imports = re.findall(pattern, content)
            for imp in string_imports:
                if '.' in imp:
                    # For 'from x import y' pattern, we just want 'x'
                    imports.add(imp.split('.')[0])
                else:
                    imports.add(imp)
            
            return imports
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return set()
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
            return set()

def scan_directory_for_imports(directory_path):
    """Recursively scan a directory for Python files and extract imports."""
    imports = set()
    directory = Path(directory_path)
    
    # Skip common directories that shouldn't be scanned
    skip_dirs = {'.git', '.venv', 'venv', 'env', '__pycache__', 'node_modules', 'build', 'dist'}
    
    file_count = 0
    for item in directory.glob('**/*.py'):
        # Skip files in directories we want to ignore
        if any(skip_dir in item.parts for skip_dir in skip_dirs):
            continue
            
        if item.is_file():
            logger.debug(f"Scanning {item}")
            file_imports = extract_imports_from_file(item)
            imports.update(file_imports)
            file_count += 1
    
    logger.info(f"Scanned {file_count} Python files, found {len(imports)} unique imported modules")
    return imports