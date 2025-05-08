import subprocess
import sys

def install_dependencies():
    """Install required dependencies on Streamlit Cloud during deployment"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

if __name__ == "__main__":
    install_dependencies()