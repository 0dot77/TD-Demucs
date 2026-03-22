"""
Demucs 모델 다운로드 스크립트.

demucs 패키지를 설치하고 htdemucs 모델 가중치를 미리 다운로드합니다.
"""

import subprocess
import sys


def install_demucs():
    """demucs 패키지를 pip으로 설치합니다."""
    print("[1/2] Installing demucs...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "demucs"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error installing demucs:\n{result.stderr}")
        return False
    print("demucs installed successfully.")
    return True


def download_model(model_name: str = "htdemucs"):
    """모델 가중치를 미리 다운로드합니다."""
    print(f"[2/2] Downloading model: {model_name}...")
    try:
        from demucs import pretrained
        pretrained.get_model(model_name)
        print(f"Model '{model_name}' downloaded successfully.")
        return True
    except Exception as e:
        print(f"Error downloading model: {e}")
        return False


def main():
    if not install_demucs():
        sys.exit(1)
    if not download_model():
        sys.exit(1)
    print("\nSetup complete. You can now use TD-Demucs.")


if __name__ == "__main__":
    main()
