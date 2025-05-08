import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies on Streamlit Cloud during deployment"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
   
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

if __name__ == "__main__":
    install_dependencies()