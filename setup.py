"""
Setup script for the NYC Landmarks Research Agent package.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="nyc-landmarks-research-agent",
    version="0.1.0",
    author="NYC Landmarks Research Agent Team",
    author_email="example@example.com",
    description="An AI-powered agent to generate research reports about NYC landmarks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/nyc-landmarks-research-agent",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            # Testing
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.1",
            "httpx>=0.24.1",
            # Linting and formatting
            "pre-commit>=3.5.0",
            "black>=25.1.0",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "flake8-docstrings>=1.7.0",
            "flake8-quotes>=3.4.0",
            "flake8-comprehensions>=3.14.0",
            # Type checking
            "mypy>=1.9.0",
            "types-requests>=2.31.0",
            "types-PyYAML>=6.0.0",
            # Security
            "bandit>=1.7.8",
            # Jupyter notebook tools
            "nbstripout>=0.6.1",
            "nbqa>=1.7.1",
        ],
    },
)
