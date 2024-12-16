from setuptools import setup

setup(
    name="lingualearn",
    version="0.1.0",
    package_dir={"":"src"},
    packages=["lingualearn"],
    python_requires=">=3.8",
    install_requires=[
        "pytest>=6.0.0",
        "pytest-asyncio>=0.15.0",
    ],
)