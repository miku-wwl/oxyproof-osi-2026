"""Verify local no-voice capture metadata and extract scenes for human visual review."""

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    video = ROOT / ".local/demo/oxyproof-phase2.webm"
    binary = next((ROOT / ".local/ms-playwright").glob("ffmpeg-*/ffmpeg-win64.exe"))
    probe = subprocess.run(
        [str(binary), "-hide_banner", "-i", str(video)], capture_output=True, text=True, timeout=30
    )
    text = probe.stderr
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", text)
    if not match:
        raise RuntimeError("VIDEO_METADATA_UNAVAILABLE")
    hours, minutes, seconds = map(float, match.groups())
    duration = hours * 3600 + minutes * 60 + seconds
    assert 180 <= duration <= 240 and "1440x1000" in text and "Video: vp9" in text
    assert "Audio:" not in text
    log = json.loads((ROOT / ".local/demo/scene-log.json").read_text(encoding="utf-8"))
    frame_dir = ROOT / ".local/demo/frames"
    frame_dir.mkdir(exist_ok=True)
    frames = []
    for scene in log["scenes"]:
        position = scene["time_s"] + 4
        target = frame_dir / f"scene-{len(frames) + 1:02d}.png"
        subprocess.run(
            [
                str(binary),
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                str(position),
                "-i",
                str(video),
                "-frames:v",
                "1",
                str(target),
            ],
            check=True,
            timeout=30,
        )
        frames.append(
            {
                "position_s": position,
                "path": target.relative_to(ROOT).as_posix(),
                "caption": scene["caption"],
            }
        )
    exported = json.loads((ROOT / ".local/demo/exported-decision.json").read_text(encoding="utf-8"))
    result = {
        "status": "METADATA_AND_SCENE_EXTRACTION_PASS",
        "video_path": video.relative_to(ROOT).as_posix(),
        "video_sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
        "bytes": video.stat().st_size,
        "duration_seconds": duration,
        "resolution": "1440x1000",
        "codec": "VP9/WebM",
        "audio_streams": 0,
        "runtime_mode": log["runtime_mode"],
        "source_scope": log["source_scope"],
        "capture_code_version": exported["code_version"],
        "frames": frames,
        "visual_review": "See PHASE2_HANDOVER.md for actually inspected frames; extraction alone is not visual acceptance.",
    }
    (ROOT / "artifacts/demo_video_validation.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"DEMO_VIDEO_METADATA=PASS duration_s={duration} resolution=1440x1000 audio_streams=0 frames_extracted={len(frames)}"
    )
