# auto_dep_installer/setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="auto_dep_installer",
    version="0.2",
    author="Shubham Chambhare",
    author_email="shubhamchambhare654@gmail.com",
    description="Automatically install missing dependencies in your Python project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shubham654/auto_dep_installer",
    project_urls={
        "Bug Tracker": "https://github.com/Shubham654/auto_dep_installer/issues",
        "Documentation": "https://github.com/Shubham654/auto_dep_installer#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="dependency, management, automation, virtual environment, venv",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "auto-dep=auto_dep_installer.cli:main",
        ],
    },
    install_requires=[
        "setuptools",
    ],
)