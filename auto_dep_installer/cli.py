# auto_dep_installer/auto_dep_installer/cli.py

import argparse
import os
import sys
import venv
import subprocess
import logging
from pathlib import Path

from .installer import install_missing_packages, resolve_dependencies
from .scanner import scan_directory_for_imports

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('auto_dep_installer')

def create_venv(venv_path):
    """Create a virtual environment at the specified path."""
    logger.info(f"Creating virtual environment at {venv_path}...")
    try:
        venv.create(venv_path, with_pip=True)
        logger.info(f"Virtual environment created successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to create virtual environment: {e}")
        return False

def get_venv_python(venv_path):
    """Get the path to the Python executable in the virtual environment."""
    if sys.platform == "win32":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")

def activate_venv(venv_path):
    """Modify environment to use the virtual environment."""
    # Get the Python executable path in the virtual environment
    python_path = get_venv_python(venv_path)
    
    if not os.path.exists(python_path):
        logger.error(f"Python executable not found in virtual environment: {python_path}")
        return False
    
    if sys.platform == "win32":
        # On Windows, modify PATH to include the venv's Scripts directory
        scripts_dir = os.path.join(venv_path, "Scripts")
        os.environ["PATH"] = f"{scripts_dir};{os.environ['PATH']}"
    else:
        # On Unix, modify PATH to include the venv's bin directory
        bin_dir = os.path.join(venv_path, "bin")
        os.environ["PATH"] = f"{bin_dir}:{os.environ['PATH']}"
    
    # Set VIRTUAL_ENV environment variable
    os.environ["VIRTUAL_ENV"] = str(venv_path)
    
    # Remove PYTHONHOME if set
    if "PYTHONHOME" in os.environ:
        del os.environ["PYTHONHOME"]
    
    logger.info(f"Virtual environment activated: {venv_path}")
    return True

def verify_venv_activation(venv_path):
    """Verify that the virtual environment is activated by checking sys.executable."""
    python_path = get_venv_python(venv_path)
    if os.path.normcase(sys.executable) != os.path.normcase(python_path):
        # If not properly activated, try to run a subprocess using the venv Python
        logger.warning(f"Virtual environment not fully activated. Using subprocess approach.")
        return False
    return True

def install_in_venv(venv_path, packages, resolve=True):
    """Install packages in the virtual environment using a subprocess."""
    python_path = get_venv_python(venv_path)
    
    if not packages:
        logger.info("No packages to install.")
        return True
    
    logger.info(f"Installing {len(packages)} packages in virtual environment...")
    
    # Install packages one by one for better error handling
    success_count = 0
    failed_packages = []
    
    for package in packages:
        try:
            logger.info(f"Installing {package}...")
            subprocess.check_call([python_path, "-m", "pip", "install", package])
            success_count += 1
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
            failed_packages.append(package)
    
    # If we have failed packages and resolve is True, try to resolve dependencies
    if failed_packages and resolve:
        logger.info(f"Attempting to resolve dependencies for {len(failed_packages)} failed packages...")
        resolved_packages = resolve_dependencies(failed_packages)
        if resolved_packages:
            # Try installing the resolved packages
            return install_in_venv(venv_path, resolved_packages, resolve=False)
    
    if failed_packages:
        logger.warning(f"Failed to install {len(failed_packages)} packages: {', '.join(failed_packages)}")
    
    logger.info(f"Successfully installed {success_count} out of {len(packages)} packages.")
    return success_count == len(packages)

def main():
    parser = argparse.ArgumentParser(description="Auto Dependency Installer")
    parser.add_argument(
        "--directory", "-d", 
        default=".", 
        help="Directory to scan for Python files (default: current directory)"
    )
    parser.add_argument(
        "--venv", "-v", 
        default=".venv", 
        help="Virtual environment name/path (default: .venv)"
    )
    parser.add_argument(
        "--no-venv", 
        action="store_true", 
        help="Skip virtual environment creation/activation"
    )
    parser.add_argument(
        "--custom-mappings", "-m",
        help="Path to JSON file with custom module-to-package mappings"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "--resolve", 
        action="store_true", 
        help="Attempt to resolve dependency issues"
    )
    parser.add_argument(
        "--force-reinstall", 
        action="store_true", 
        help="Force reinstall of packages even if they are already installed"
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    # Convert relative paths to absolute
    project_dir = os.path.abspath(args.directory)
    venv_path = os.path.abspath(args.venv)
    
    logger.info(f"Starting Auto Dependency Installer")
    logger.info(f"Project directory: {project_dir}")
    
    # Create and activate virtual environment if requested
    if not args.no_venv:
        if not os.path.exists(venv_path):
            if not create_venv(venv_path):
                logger.error("Failed to create virtual environment. Exiting.")
                sys.exit(1)
        
        if not activate_venv(venv_path):
            logger.error("Failed to activate virtual environment. Exiting.")
            sys.exit(1)
        
        # Verify activation
        if not verify_venv_activation(venv_path):
            logger.warning("Virtual environment not fully activated. Will use subprocess approach.")
    
    # Load custom mappings if provided
    custom_mappings = {}
    if args.custom_mappings and os.path.exists(args.custom_mappings):
        import json
        try:
            with open(args.custom_mappings, 'r') as f:
                custom_mappings = json.load(f)
            logger.info(f"Loaded {len(custom_mappings)} custom mappings from {args.custom_mappings}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse custom mappings file: {e}")
    
    # Scan for imports
    logger.info(f"Scanning directory: {project_dir}")
    imported_modules = scan_directory_for_imports(project_dir)
    
    if not imported_modules:
        logger.warning("No imports found in the specified directory.")
        sys.exit(0)
    
    logger.info(f"Found {len(imported_modules)} imported modules")
    
    # Determine packages to install
    packages_to_install = install_missing_packages(
        imported_modules, 
        custom_mappings, 
        dry_run=True, 
        force_reinstall=args.force_reinstall
    )
    
    if not packages_to_install:
        logger.info("All dependencies are already installed.")
        sys.exit(0)
    
    logger.info(f"Identified {len(packages_to_install)} packages to install")
    
    # Install packages
    if args.no_venv:
        # Install directly in the current environment
        success = install_missing_packages(
            imported_modules, 
            custom_mappings, 
            dry_run=False, 
            force_reinstall=args.force_reinstall
        )
    else:
        # Install in the virtual environment
        success = install_in_venv(
            venv_path, 
            packages_to_install, 
            resolve=args.resolve
        )
    
    if success:
        logger.info("Auto Dependency Installer completed successfully.")
    else:
        logger.warning("Auto Dependency Installer completed with some issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()