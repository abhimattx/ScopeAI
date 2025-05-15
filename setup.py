import subprocess
import sys
from setuptools import setup, find_packages

def install_dependencies():
    """Install required dependencies on Streamlit Cloud during deployment"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Install spaCy model with pip instead of spacy CLI
    subprocess.check_call([sys.executable, "-m", "pip", "install", "en-core-web-sm==3.5.0", "--no-deps"])

if __name__ == "__main__":
    install_dependencies()
    
    setup(
        name="scopeai",
        version="0.1.0",
        packages=find_packages(),
        install_requires=[
            line.strip() for line in open("requirements.txt")
            if line.strip() and not line.startswith("#")
        ],
    )