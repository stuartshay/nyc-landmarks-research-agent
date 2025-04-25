"""
Setup script for the NYC Landmarks Research Agent package.
"""
from setuptools import setup, find_packages

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
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.1",
            "black>=23.10.1",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.6.1",
            "pre-commit>=3.5.0",
        ],
    },
)
