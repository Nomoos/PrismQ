"""Setup configuration for PrismQ.IdeaInspiration.Model package."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prismq-idea-model",
    version="0.1.0",
    author="PrismQ",
    author_email="dev@prismq.com",
    description="Core IdeaInspiration model for PrismQ content processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nomoos/PrismQ.IdeaInspiration.Model",
    py_modules=['idea_inspiration', 'config_manager'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - pure Python
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
    package_data={},
    zip_safe=False,
)
