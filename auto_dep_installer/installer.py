# auto_dep_installer/auto_dep_installer/installer.py

import importlib
import subprocess
import sys
import pkg_resources
import logging

logger = logging.getLogger('auto_dep_installer')

def is_module_installed(module_name):
    """Check if a module is installed and importable."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def get_installed_packages():
    """Get a dictionary of installed packages."""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def install_package(package_name):
    """Install a package using pip."""
    logger.info(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package_name}: {e}")
        return False

def get_package_for_module(module_name, custom_mappings=None):
    """Get the package name for a module, using mappings if available."""
    if custom_mappings is None:
        custom_mappings = {}
    
    # Common module-to-package mappings
    default_mappings = {
        "bs4": "beautifulsoup4",
        "PIL": "pillow",
        "cv2": "opencv-python",
        "sklearn": "scikit-learn",
        "yaml": "pyyaml",
        "wx": "wxpython",
        "matplotlib.pyplot": "matplotlib",
        "tensorflow.keras": "tensorflow",
        "urllib3": "urllib3",
        "lxml": "lxml",
        "requests": "requests",
        "numpy": "numpy",
        "pandas": "pandas",
        "flask": "flask",
        "django": "django",
        "sqlalchemy": "sqlalchemy",
        "pytest": "pytest",
        "selenium": "selenium",
        "dash": "dash",
        "kivy": "kivy",
        "scrapy": "scrapy",
        "folium": "folium",
        "nltk": "nltk",
        "gensim": "gensim",
        "torch": "torch",
        "transformers": "transformers",
        "pyspark": "pyspark",
        "streamlit": "streamlit",
        "fastapi": "fastapi",
        "plotly": "plotly",
        "seaborn": "seaborn",
        "bokeh": "bokeh",
        "scipy": "scipy",
        "sympy": "sympy",
        "statsmodels": "statsmodels",
    }
    
    # Combine default and custom mappings
    mappings = {**default_mappings, **custom_mappings}
    
    # Get root module name (e.g., 'numpy' from 'numpy.array')
    root_module = module_name.split('.')[0]
    
    # Return the mapped package name or the root module name if no mapping exists
    return mappings.get(root_module, root_module)

def filter_standard_library_modules(modules):
    """Filter out standard library modules."""
    non_stdlib_modules = []
    for module in modules:
        root_module = module.split('.')[0]
        try:
            # If the module is in the standard library, it will be found in one of these locations
            spec = importlib.util.find_spec(root_module)
            if spec is None:
                non_stdlib_modules.append(module)
                continue
            
            # Check if the module is part of the standard library
            if any(p.startswith(sys.prefix) for p in spec.submodule_search_locations or []):
                # This is likely a third-party package installed in site-packages
                non_stdlib_modules.append(module)
            else:
                # This is likely a standard library module
                pass
        except (ImportError, AttributeError):
            # If there's an error, assume it's not a standard library module
            non_stdlib_modules.append(module)
    
    return non_stdlib_modules

def resolve_dependencies(failed_packages):
    """Attempt to resolve dependencies for failed packages."""
    resolved_packages = []
    
    for package in failed_packages:
        # Try different approaches to resolve dependencies
        
        # 1. Check if the package has a different name on PyPI
        alternative_names = {
            # Add mappings for common packages with different names
            "yaml": "pyyaml",
            "cv": "opencv-python",
            "skimage": "scikit-image",
            "bs4": "beautifulsoup4",
            "pil": "pillow",
            "tk": "tk",
            "tkinter": "tk",
            "wx": "wxpython",
        }
        
        if package.lower() in alternative_names:
            logger.info(f"Trying alternative package name: {alternative_names[package.lower()]} for {package}")
            resolved_packages.append(alternative_names[package.lower()])
            continue
        
        # 2. Try with different casing
        if package.lower() != package:
            logger.info(f"Trying lowercase version: {package.lower()} for {package}")
            resolved_packages.append(package.lower())
            continue
        
        # 3. Try with hyphens instead of underscores
        if "_" in package:
            hyphen_version = package.replace("_", "-")
            logger.info(f"Trying with hyphens: {hyphen_version} for {package}")
            resolved_packages.append(hyphen_version)
            continue
        
        # 4. Try common prefixes/suffixes
        prefixes = ["python-"]
        for prefix in prefixes:
            logger.info(f"Trying with prefix: {prefix}{package} for {package}")
            resolved_packages.append(f"{prefix}{package}")
        
        suffixes = ["-python"]
        for suffix in suffixes:
            logger.info(f"Trying with suffix: {package}{suffix} for {package}")
            resolved_packages.append(f"{package}{suffix}")
    
    return resolved_packages

def install_missing_packages(imported_modules, custom_mappings=None, dry_run=False, force_reinstall=False):
    """Install missing packages based on imported modules."""
    if custom_mappings is None:
        custom_mappings = {}
    
    # Filter out standard library modules
    non_stdlib_modules = filter_standard_library_modules(imported_modules)
    logger.info(f"Found {len(non_stdlib_modules)} non-standard library modules out of {len(imported_modules)} imports")
    
    installed_packages = get_installed_packages()
    to_install = []
    
    for module_name in non_stdlib_modules:
        # Get root module name (e.g., 'numpy' from 'numpy.array')
        root_module = module_name.split('.')[0]
        
        # Skip if the module is already installed and we're not forcing reinstall
        if not force_reinstall and is_module_installed(root_module):
            logger.debug(f"Module {root_module} is already installed")
            continue
        
        # Get the package name for this module
        package_name = get_package_for_module(module_name, custom_mappings)
        
        # Skip if the package is already installed under a different name
        if not force_reinstall and package_name.lower() in installed_packages:
            logger.debug(f"Package {package_name} is already installed")
            continue
            
        to_install.append(package_name)
    
    # Remove duplicates while preserving order
    to_install = list(dict.fromkeys(to_install))
    
    if not to_install:
        logger.info("All dependencies are already installed.")
        return []
    
    if dry_run:
        logger.info(f"Would install {len(to_install)} packages: {', '.join(to_install)}")
        return to_install
    
    logger.info(f"Found {len(to_install)} packages to install: {', '.join(to_install)}")
    
    # Install each package
    success_count = 0
    failed_packages = []
    
    for package in to_install:
        if install_package(package):
            success_count += 1
        else:
            failed_packages.append(package)
    
    if failed_packages:
        logger.warning(f"Failed to install {len(failed_packages)} packages: {', '.join(failed_packages)}")
    
    return success_count == len(to_install)