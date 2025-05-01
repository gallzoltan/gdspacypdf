from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()]

setup(
    name="gdspacypdf",
    version="0.1.0",
    author="Gáll Zoltán",
    author_email="your.email@example.com",  # Add your email here
    description="A Magyar Közlöny önkormányzatokra vonatkozó tartalom elemzése",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gdspacypdf",  # Replace with your repository URL
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Hungarian",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gdspacypdf=src.main:main",
        ],
    },
)