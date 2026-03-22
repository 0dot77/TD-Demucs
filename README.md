[English](#english) | [한국어](#한국어)

# TD-Demucs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TouchDesigner](https://img.shields.io/badge/TouchDesigner-2023+-blue.svg)](https://derivative.ca)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)

## English

**Audio Source Separation Plugin for TouchDesigner** - Separates music into individual instrument tracks using Meta's [Demucs](https://github.com/facebookresearch/demucs) model.

## What is Audio Source Separation?

Audio Source Separation is a technique for extracting individual instrument sounds from a single music file. TD-Demucs uses Meta's Hybrid Transformer Demucs (htdemucs) model to separate music into **4 stems**:

| Stem | Description |
|------|-------------|
| **vocals** | Vocals / Voice |
| **drums** | Drums / Percussion |
| **bass** | Bass |
| **other** | Guitar, Piano, and other instruments |

## Requirements

- **TouchDesigner** 2023 or later
- **Python 3.9+** (separate Python environment with demucs installed)
- **demucs** package: `pip install demucs`
- **PyTorch**: automatically installed with demucs
- **Storage**: ~80MB for model weights, ~2GB for PyTorch
- **RAM**: minimum 8GB (16GB recommended)

## Installation

### 1. Prepare Python Environment

Use a **separate Python environment**, not TouchDesigner's built-in Python. Demucs depends on PyTorch, so an independent environment is required.

```bash
# Create a virtual environment (recommended)
python -m venv demucs_env
source demucs_env/bin/activate  # macOS/Linux
# or
demucs_env\Scripts\activate     # Windows

# Install demucs
pip install demucs
```

### 2. Download Model

```bash
# Run the automatic model download script
python scripts/download_model.py
```

Alternatively, the model will be automatically downloaded the first time you run demucs.

### 3. TouchDesigner Setup

#### Register Extension

1. Create a **Base COMP** in TouchDesigner and name it `TDDemucs`.
2. Create a **Text DAT** inside the Base COMP.
3. Paste the contents of `td/TDDemucs_Extension.py` into the Text DAT.
4. In the Base COMP's **Extensions** parameter:
   - Extension Object: `TDDemucsExt`
   - Extension Module: specify the Text DAT

#### Callback Setup

1. Create a **Timer CHOP** (for status polling):
   - Length: `0.5` seconds
   - Repeat: `On`
   - Active: `Off` (activated when separation starts)
2. Create a **DAT Execute** or **Script CHOP**.
3. Paste the contents of `td/TDDemucs_Callbacks.py` into the callback DAT.

#### Status Display DAT (Optional)

1. Create a **Table DAT** and name it `status_dat`.
2. Separation progress will be automatically recorded.

## Usage

### Basic Usage

From the Python Shell or Script:

```python
# Access the Extension
ext = op('TDDemucs').ext.TDDemucsExt

# Start audio separation
ext.Separate(
    audio_path='/path/to/your/song.mp3',
    python_exe='/path/to/demucs_env/bin/python'  # Python with demucs installed
)

# Check status
print(ext.GetStatus())   # 'idle', 'processing', 'complete', 'error'
print(ext.Message)        # Detailed message

# Get stem paths after separation is complete
stems = ext.GetStems()
# {'vocals': '/path/separated/vocals.wav', 'drums': '...', ...}

# Auto-load into Audio File In CHOPs
ext.LoadStemsToChops()
```

### Change Model

```python
ext = op('TDDemucs').ext.TDDemucsExt
ext.Model = 'htdemucs_ft'  # Fine-tuned model (higher quality, 4x slower)
ext.Separate('/path/to/song.mp3', python_exe='python')
```

### Available Models

| Model | Description | Processing Time |
|-------|-------------|-----------------|
| `htdemucs` | Default model, fastest | ~10-30s |
| `htdemucs_ft` | Fine-tuned, higher quality | ~40-120s |
| `htdemucs_6s` | 6 stems (adds guitar, piano) | ~15-40s |

## Use Cases

### Per-Instrument Audio-Reactive Visuals

Load each stem into a separate Audio File In CHOP for independent audio analysis per instrument:

- **vocals** -> Audio Spectrum -> Vocal-reactive particles
- **drums** -> Audio Spectrum -> Beat-reactive camera shake
- **bass** -> Audio Spectrum -> Low-frequency background distortion
- **other** -> Audio Spectrum -> Melody-reactive color changes

### Live Performance / VJ

Pre-separate your setlist tracks to:
- Build visual layers that respond only to specific instruments
- Remove vocals and use instrumentals only
- Extract drum tracks for beat sync

### Interactive Installations

- Adjust individual instrument track volumes based on audience participation
- Sound installations where different instruments are heard depending on spatial position

## Performance Notes

- **This is NOT real-time processing.** Demucs processes entire audio files offline.
- Processing time for a 3-minute track:
  - CPU: ~30-90 seconds
  - GPU (CUDA): ~10-30 seconds
- For GPU acceleration, install the CUDA version of PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cu121`
- Processing runs in a background thread, so the TouchDesigner UI will not freeze.
- Already-separated tracks can be reused without reprocessing.

## Troubleshooting

### "Missing dependency" Error

Make sure you specify the Python environment with demucs installed via the `python_exe` parameter.

```python
ext.Separate('/path/to/song.mp3', python_exe='/path/to/demucs_env/bin/python')
```

### Out of Memory (OOM)

This can occur with long audio files. Demucs processes in segments internally, but for very long files (over 10 minutes), it is recommended to split them beforehand.

### GPU Not Being Used

Verify that the CUDA version of PyTorch is installed:

```python
import torch
print(torch.cuda.is_available())  # Must be True for GPU usage
```

### Low Separation Quality

- Try using the `htdemucs_ft` model (slower but higher quality).
- Higher quality input audio (WAV, FLAC > MP3) produces better results.

## Project Structure

```
TD-Demucs/
├── td/
│   ├── TDDemucs_Extension.py    # Extension (registered to COMP)
│   └── TDDemucs_Callbacks.py    # Timer/Execute callbacks
├── scripts/
│   ├── demucs_worker.py         # Separation worker subprocess
│   └── download_model.py        # Model download script
├── models/                      # Model files (gitignored)
├── separated/                   # Separation results (gitignored)
├── README.md
├── LICENSE
└── .gitignore
```

## License

MIT License - See [LICENSE](LICENSE)

## Credits

- [Demucs](https://github.com/facebookresearch/demucs) by Meta Research
- [TouchDesigner](https://derivative.ca) by Derivative

---

## 한국어

**TouchDesigner용 오디오 소스 분리 플러그인** - Meta의 [Demucs](https://github.com/facebookresearch/demucs) 모델을 사용하여 음악을 개별 악기 트랙으로 분리합니다.

## 오디오 소스 분리란?

오디오 소스 분리(Audio Source Separation)는 하나의 음악 파일에서 개별 악기 소리를 추출하는 기술입니다. TD-Demucs는 Meta의 Hybrid Transformer Demucs(htdemucs) 모델을 사용하여 음악을 **4개의 스템(stem)**으로 분리합니다:

| 스템 | 설명 |
|------|------|
| **vocals** | 보컬/목소리 |
| **drums** | 드럼/퍼커션 |
| **bass** | 베이스 |
| **other** | 기타, 피아노 등 나머지 악기 |

## 요구 사항

- **TouchDesigner** 2023 이상
- **Python 3.9+** (demucs가 설치된 별도 Python 환경)
- **demucs** 패키지: `pip install demucs`
- **PyTorch**: demucs 설치 시 자동으로 함께 설치됨
- **저장 공간**: 모델 가중치 약 80MB, PyTorch 약 2GB
- **RAM**: 최소 8GB (16GB 권장)

## 설치

### 1. Python 환경 준비

TouchDesigner의 내장 Python이 아닌 **별도의 Python 환경**을 사용합니다. demucs는 PyTorch에 의존하므로 독립적인 환경이 필요합니다.

```bash
# 가상환경 생성 (권장)
python -m venv demucs_env
source demucs_env/bin/activate  # macOS/Linux
# 또는
demucs_env\Scripts\activate     # Windows

# demucs 설치
pip install demucs
```

### 2. 모델 다운로드

```bash
# 모델 자동 다운로드 스크립트 실행
python scripts/download_model.py
```

또는 demucs를 한 번 실행하면 모델이 자동으로 다운로드됩니다.

### 3. TouchDesigner 설정

#### Extension 등록

1. TouchDesigner에서 **Base COMP**를 생성하고 이름을 `TDDemucs`로 지정합니다.
2. Base COMP 안에 **Text DAT**을 생성합니다.
3. `td/TDDemucs_Extension.py`의 내용을 Text DAT에 붙여넣습니다.
4. Base COMP의 **Extensions** 파라미터에서:
   - Extension Object: `TDDemucsExt`
   - Extension Module: 해당 Text DAT을 지정

#### 콜백 설정

1. **Timer CHOP**을 생성합니다 (상태 폴링용):
   - Length: `0.5` seconds
   - Repeat: `On`
   - Active: `Off` (분리 시작 시 활성화)
2. **DAT Execute** 또는 **Script CHOP**을 생성합니다.
3. `td/TDDemucs_Callbacks.py`의 내용을 콜백 DAT에 붙여넣습니다.

#### 상태 표시용 DAT (선택)

1. **Table DAT**을 생성하고 이름을 `status_dat`으로 지정합니다.
2. 분리 진행 상태가 자동으로 기록됩니다.

## 사용 방법

### 기본 사용

Python Shell 또는 Script에서:

```python
# Extension 접근
ext = op('TDDemucs').ext.TDDemucsExt

# 오디오 분리 시작
ext.Separate(
    audio_path='/path/to/your/song.mp3',
    python_exe='/path/to/demucs_env/bin/python'  # demucs가 설치된 Python
)

# 상태 확인
print(ext.GetStatus())   # 'idle', 'processing', 'complete', 'error'
print(ext.Message)        # 상세 메시지

# 분리 완료 후 스템 경로 확인
stems = ext.GetStems()
# {'vocals': '/path/separated/vocals.wav', 'drums': '...', ...}

# Audio File In CHOP으로 자동 로드
ext.LoadStemsToChops()
```

### 모델 변경

```python
ext = op('TDDemucs').ext.TDDemucsExt
ext.Model = 'htdemucs_ft'  # Fine-tuned 모델 (더 높은 품질, 4배 느림)
ext.Separate('/path/to/song.mp3', python_exe='python')
```

### 사용 가능한 모델

| 모델 | 설명 | 처리 시간 |
|------|------|-----------|
| `htdemucs` | 기본 모델, 가장 빠름 | ~10-30초 |
| `htdemucs_ft` | Fine-tuned, 더 높은 품질 | ~40-120초 |
| `htdemucs_6s` | 6개 스템 (guitar, piano 추가) | ~15-40초 |

## 사용 사례

### 악기별 오디오 리액티브 비주얼

각 스템을 별도의 Audio File In CHOP으로 로드하면, 악기별로 독립적인 오디오 분석이 가능합니다:

- **vocals** -> Audio Spectrum -> 보컬 반응 파티클
- **drums** -> Audio Spectrum -> 비트 반응 카메라 쉐이크
- **bass** -> Audio Spectrum -> 저주파 기반 배경 변형
- **other** -> Audio Spectrum -> 멜로디 반응 색상 변화

### 라이브 퍼포먼스 / VJ

사전에 세트리스트의 곡들을 분리해두면:
- 특정 악기에만 반응하는 비주얼 레이어 구성
- 보컬 제거 후 인스트루멘탈만 사용
- 드럼 트랙만 추출하여 비트 싱크

### 인터랙티브 설치

- 관객 참여에 따라 특정 악기 트랙의 볼륨 조절
- 공간의 위치에 따라 다른 악기가 들리는 사운드 설치

## 성능 참고 사항

- **실시간 처리가 아닙니다.** Demucs는 전체 오디오 파일을 처리하는 오프라인 방식입니다.
- 3분 길이 곡 기준 처리 시간:
  - CPU: 약 30-90초
  - GPU (CUDA): 약 10-30초
- GPU 사용 시 PyTorch CUDA 버전을 설치하세요: `pip install torch --index-url https://download.pytorch.org/whl/cu121`
- 처리는 백그라운드 스레드에서 실행되므로 TouchDesigner UI가 멈추지 않습니다.
- 이미 분리된 곡은 다시 처리할 필요 없이 결과 파일을 재사용하세요.

## 문제 해결

### "Missing dependency" 오류

demucs가 설치된 Python 환경을 `python_exe` 파라미터로 정확히 지정했는지 확인하세요.

```python
ext.Separate('/path/to/song.mp3', python_exe='/path/to/demucs_env/bin/python')
```

### 메모리 부족 (OOM)

긴 오디오 파일에서 발생할 수 있습니다. demucs는 내부적으로 세그먼트 단위로 처리하지만, 매우 긴 파일(10분 이상)은 미리 잘라서 처리하는 것을 권장합니다.

### GPU가 사용되지 않음

PyTorch CUDA 버전이 설치되어 있는지 확인하세요:

```python
import torch
print(torch.cuda.is_available())  # True여야 GPU 사용
```

### 분리 품질이 낮음

- `htdemucs_ft` 모델을 사용해보세요 (처리 시간이 늘어나지만 품질 향상).
- 입력 오디오의 품질이 높을수록 (WAV, FLAC > MP3) 결과가 좋습니다.

## 프로젝트 구조

```
TD-Demucs/
├── td/
│   ├── TDDemucs_Extension.py    # Extension (COMP에 등록)
│   └── TDDemucs_Callbacks.py    # Timer/Execute 콜백
├── scripts/
│   ├── demucs_worker.py         # 분리 작업 subprocess
│   └── download_model.py        # 모델 다운로드 스크립트
├── models/                      # 모델 파일 (gitignored)
├── separated/                   # 분리 결과 (gitignored)
├── README.md
├── LICENSE
└── .gitignore
```

## 라이선스

MIT License - [LICENSE](LICENSE) 참조

## 크레딧

- [Demucs](https://github.com/facebookresearch/demucs) by Meta Research
- [TouchDesigner](https://derivative.ca) by Derivative
