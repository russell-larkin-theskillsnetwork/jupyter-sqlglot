"""Setup configuration for jupyter-sqlglot."""

from setuptools import setup, find_packages
import os

# Read the version from the package
version = {}
with open(os.path.join("src", "jupyter_sqlglot", "__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

# Read the long description from README
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="jupyter-sqlglot",
    version=version.get("__version__", "0.1.0"),
    author="Russell Larkin",
    author_email="",
    description="Jupyter extension for automatic Spark SQL formatting using SQLGlot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jupyter-sqlglot",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/jupyter-sqlglot/issues",
        "Source": "https://github.com/yourusername/jupyter-sqlglot",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Framework :: Jupyter",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "sqlglot>=20.0.0",
        "ipython>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        # No CLI entry points needed for a Jupyter extension
    },
    keywords="jupyter notebook sql sqlglot spark formatting",
    zip_safe=False,
)
