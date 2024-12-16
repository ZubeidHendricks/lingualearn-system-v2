from setuptools import setup, find_packages

setup(
    name="lingualearn",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "websockets>=10.0",
        "librosa>=0.8.0",
        "sounddevice>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0",
            "pytest-cov>=2.12.0",
            "flake8>=3.9.0",
            "black>=21.0",
            "isort>=5.9.0",
        ],
    },
)