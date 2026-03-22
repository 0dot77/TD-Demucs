"""
TDDemucs Callbacks - Timer CHOP 또는 Execute DAT에서 호출되는 콜백.

Timer CHOP의 onDone 콜백에서 상태를 폴링하거나,
Execute DAT에서 분리 완료 시 후처리를 수행합니다.
"""


def onSeparateStart(info: dict):
    """
    분리 작업 시작 시 호출됩니다.
    Execute DAT의 onValueChange 등에서 트리거합니다.

    사용 예 (Execute DAT onValueChange):
        audio_path = op('filechooser').par.file.eval()
        ext = op('TDDemucs').ext.TDDemucsExt
        ext.Separate(audio_path)
    """
    ext = op("TDDemucs").ext.TDDemucsExt
    audio_path = info.get("audio_path", "")
    python_exe = info.get("python_exe", "python")

    if audio_path:
        ext.Separate(audio_path, python_exe=python_exe)
        debug(f"[TD-Demucs] Separation started: {audio_path}")


def onTimerPulse(timerOp):
    """
    Timer CHOP에서 주기적으로 호출되어 분리 상태를 확인합니다.
    Timer CHOP의 callback_pulse에 연결합니다.
    """
    ext = op("TDDemucs").ext.TDDemucsExt
    status = ext.GetStatus()

    # 상태를 Text DAT 또는 Table DAT에 기록
    status_dat = op("status_dat")
    if status_dat is not None:
        status_dat.clear()
        status_dat.appendRow(["status", status])
        status_dat.appendRow(["message", ext.Message])

        stems = ext.GetStems()
        for stem_name, stem_path in stems.items():
            status_dat.appendRow([stem_name, stem_path])


def onSeparateComplete():
    """
    분리 완료 시 호출됩니다.
    Timer 콜백에서 status == 'complete'를 감지하면 호출합니다.

    분리된 스템을 Audio File In CHOP으로 자동 로드합니다.
    """
    ext = op("TDDemucs").ext.TDDemucsExt

    if ext.GetStatus() == "complete":
        ext.LoadStemsToChops()
        debug("[TD-Demucs] Stems loaded to CHOPs")

        stems = ext.GetStems()
        for name, path in stems.items():
            debug(f"  {name}: {path}")


def onPollStatus(timerOp):
    """
    Timer CHOP onDone 콜백.
    분리 상태를 확인하고 완료 시 스템을 로드합니다.

    Timer CHOP 설정:
        - Length: 0.5 seconds
        - Repeat: on
        - Callbacks DAT: 이 DAT를 지정
    """
    ext = op("TDDemucs").ext.TDDemucsExt
    status = ext.GetStatus()

    if status == "complete":
        onSeparateComplete()
        # 폴링 타이머 정지
        timerOp.par.start.pulse()
    elif status == "error":
        debug(f"[TD-Demucs] Error: {ext.Message}")
        timerOp.par.start.pulse()
