# setup.py
from setuptools import setup, find_packages

setup(
    name="frd_client",
    version="0.1.0",
    author="Your Name",
    author_email="you@example.com",
    description="FirstRate Data API client and updater",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/frd_client",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "requests>=2.25.1",
        "pandas",
    ],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)