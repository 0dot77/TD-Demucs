"""
TDDemucs Extension - TouchDesigner에서 Demucs 오디오 소스 분리를 관리합니다.

COMP의 Extension으로 등록하여 사용합니다.
subprocess를 통해 demucs_worker.py를 실행하고, 분리된 스템을 관리합니다.
"""

import subprocess
import json
import os
import threading


class TDDemucsExt:
    """Demucs 오디오 소스 분리 Extension."""

    STEMS = ["vocals", "drums", "bass", "other"]

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self._process = None
        self._status = "idle"
        self._message = ""
        self._stem_paths = {}
        self._thread = None
        self._model = "htdemucs"

        # scripts 폴더 경로 (프로젝트 구조 기준)
        self._project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._worker_script = os.path.join(self._project_root, "scripts", "demucs_worker.py")
        self._output_dir = os.path.join(self._project_root, "separated")

    @property
    def Status(self) -> str:
        """현재 분리 작업 상태를 반환합니다."""
        return self._status

    @property
    def Message(self) -> str:
        """현재 상태 메시지를 반환합니다."""
        return self._message

    @property
    def StemPaths(self) -> dict:
        """분리된 스템 파일 경로 딕셔너리를 반환합니다."""
        return dict(self._stem_paths)

    @property
    def Model(self) -> str:
        return self._model

    @Model.setter
    def Model(self, value: str):
        self._model = value

    def Separate(self, audio_path: str, output_dir: str = None, python_exe: str = None):
        """
        오디오 파일의 소스 분리를 시작합니다.

        Args:
            audio_path: 입력 오디오 파일 경로
            output_dir: 출력 디렉토리 (기본: separated/)
            python_exe: Python 실행 파일 경로 (demucs가 설치된 환경)
        """
        if self._status == "processing":
            self._message = "Separation already in progress"
            return

        if not os.path.isfile(audio_path):
            self._status = "error"
            self._message = f"File not found: {audio_path}"
            return

        out_dir = output_dir or self._output_dir
        py_exe = python_exe or "python"

        self._status = "processing"
        self._message = "Starting separation..."
        self._stem_paths = {}

        self._thread = threading.Thread(
            target=self._run_worker,
            args=(py_exe, audio_path, out_dir),
            daemon=True,
        )
        self._thread.start()

    def _run_worker(self, python_exe: str, audio_path: str, output_dir: str):
        """워커 subprocess를 실행하고 stdout에서 상태를 읽습니다."""
        cmd = [
            python_exe, self._worker_script,
            "--input", audio_path,
            "--output", output_dir,
            "--model", self._model,
        ]

        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            for line in self._process.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    self._handle_worker_message(msg)
                except json.JSONDecodeError:
                    pass

            self._process.wait()

            if self._process.returncode != 0 and self._status != "complete":
                stderr = self._process.stderr.read()
                self._status = "error"
                self._message = stderr[:500] if stderr else "Worker process failed"

        except Exception as e:
            self._status = "error"
            self._message = str(e)
        finally:
            self._process = None

    def _handle_worker_message(self, msg: dict):
        """워커로부터 받은 JSON 메시지를 처리합니다."""
        status = msg.get("status", "")

        if status == "loading":
            self._message = msg.get("message", "Loading model...")
        elif status == "processing":
            self._message = msg.get("message", "Processing...")
        elif status == "stem_complete":
            stem = msg.get("stem", "")
            path = msg.get("path", "")
            if stem and path:
                self._stem_paths[stem] = path
            self._message = f"Stem complete: {stem}"
        elif status == "complete":
            self._status = "complete"
            self._stem_paths = msg.get("stems", self._stem_paths)
            self._message = "Separation complete"
        elif status == "error":
            self._status = "error"
            self._message = msg.get("message", "Unknown error")

    def GetStems(self) -> dict:
        """
        분리된 스템 파일 경로를 반환합니다.

        Returns:
            {"vocals": "/path/to/vocals.wav", "drums": "...", ...}
        """
        return dict(self._stem_paths)

    def GetStatus(self) -> str:
        """현재 상태 문자열을 반환합니다: idle, processing, complete, error."""
        return self._status

    def Cancel(self):
        """진행 중인 분리 작업을 취소합니다."""
        if self._process is not None:
            self._process.terminate()
            self._status = "cancelled"
            self._message = "Separation cancelled"

    def Reset(self):
        """상태를 초기화합니다."""
        if self._status == "processing":
            self.Cancel()
        self._status = "idle"
        self._message = ""
        self._stem_paths = {}

    def LoadStemsToChops(self, parent_path: str = None):
        """
        분리된 스템을 Audio File In CHOP으로 로드합니다.

        Args:
            parent_path: CHOP을 생성할 부모 COMP 경로 (기본: ownerComp)
        """
        if self._status != "complete" or not self._stem_paths:
            self._message = "No stems available. Run Separate() first."
            return

        parent = op(parent_path) if parent_path else self.ownerComp

        for stem_name, stem_path in self._stem_paths.items():
            chop_name = f"audiofilein_{stem_name}"
            existing = parent.op(chop_name)
            if existing is not None:
                existing.destroy()

            chop = parent.create(audiofileinCHOP, chop_name)
            chop.par.file = stem_path
            chop.par.play = True
            chop.nodeX = self.STEMS.index(stem_name) * 200
            chop.nodeY = -200
