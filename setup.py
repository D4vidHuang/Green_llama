from setuptools import setup, find_packages

setup(
    name="green-llama",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "pynvml",
        "rich",
        "pyfiglet",
        "matplotlib",
        "ollama",
        "datasets",
        "requests",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "green-llama=green_llama.__main__:main",
        ],
    },
    description="Green Llama: A CLI tool for monitoring energy metrics of Ollama models",
    author="",
    author_email="",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
