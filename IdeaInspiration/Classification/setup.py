"""Setup configuration for PrismQ.Idea.Classification package."""

from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prismq-idea-classification",
    version="2.0.0",
    author="PrismQ Team",
    author_email="dev@prismq.io",
    description="Platform-agnostic content classification for short-form vertical video",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification",
    packages=find_namespace_packages(include=['prismq.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
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
        # No external dependencies - 100% stdlib
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    keywords="prismq classification content-analysis story-detection category-classification short-form-video nlp",
    project_urls={
        "Bug Reports": "https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification/issues",
        "Source": "https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification",
        "Documentation": "https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification/docs",
    },
)
