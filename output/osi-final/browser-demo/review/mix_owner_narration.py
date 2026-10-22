"""Mix the owner's real recording with accepted video, without video re-encode.

ASR is a local, approximate alignment aid only. It is not used to replace the
voice, create subtitles, change science, or certify human listening.
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output/osi-final/browser-demo"
WORK = ROOT / ".local/narration-mix"
REVIEW = OUT / "review/narration"
BIN = ROOT / ".local/media-tools/ffmpeg-essentials/ffmpeg-9.0.2-essentials_build/bin"
# Keep the owner's private messaging-app path outside shareable project files.
SOURCE = Path(json.loads((WORK / "source-config.json").read_text(encoding="utf-8"))["source_audio_path"])
RATE = 48000
SAMPLES = 195 * RATE
PAUSE_AT = 185.55
PAUSE_ADDED = 4.65


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while data := f.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()


def run(args):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode:
        raise RuntimeError(f"Exit {p.returncode}: {p.stderr[-3000:]}")
    return p


def write(path, data):
    with path.open("x", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def probe(path):
    return json.loads(run([BIN / "ffprobe.exe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path]).stdout)


def protected():
    before = json.loads((WORK / "protected-before.json").read_text(encoding="utf-8"))
    bad = [p for p, digest in before.items() if sha(Path(p)) != digest]
    assert not bad, f"Protected inputs changed: {bad}"
    return len(before)


def base_filter():
    # Split only inside the measured 185.285521--185.808521 s deep quiet gap.
    # Every source sample is retained, at original speed, on one side of the cut.
    cut = round(PAUSE_AT * RATE)
    gap = round(PAUSE_ADDED * RATE)
    return (f"[0:a]aformat=sample_rates={RATE}:channel_layouts=stereo,asplit=2[h][t];"
            f"[h]atrim=end_sample={cut},asetpts=PTS-STARTPTS[head];"
            f"[t]atrim=start_sample={cut},asetpts=PTS-STARTPTS[tail];"
            f"anullsrc=r={RATE}:cl=stereo,atrim=end_sample={gap}[gap];"
            "[head][gap][tail]concat=n=3:v=0:a=1,highpass=f=70")


def loudness(text):
    data = re.findall(r"\{\s*\"input_i\".*?\}", text, re.S)
    assert data, text[-1500:]
    return json.loads(data[-1])


def mix():
    REVIEW.mkdir(exist_ok=False)
    count = protected()
    stats = run([BIN / "ffmpeg.exe", "-hide_banner", "-nostats", "-v", "info", "-threads", "1",
                 "-i", SOURCE, "-filter_complex", base_filter() +
                 ",loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json[out]", "-map", "[out]", "-f", "null", "-"])
    (WORK / "normalization-first-pass.log").write_text(stats.stderr, encoding="utf-8")
    measured = loudness(stats.stderr)
    params = ("loudnorm=I=-16:TP=-1.5:LRA=9:"
              f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
              f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
              f"offset={measured['target_offset']}:linear=false:print_format=json")
    wav = WORK / "aligned-normalized-195s.wav"
    p = run([BIN / "ffmpeg.exe", "-hide_banner", "-nostats", "-v", "info", "-n", "-threads", "1",
             "-i", SOURCE, "-filter_complex", base_filter() + "," + params +
             f",aresample={RATE},apad=whole_len={SAMPLES},atrim=end_sample={SAMPLES},"
             "afade=t=in:st=0:d=0.02,afade=t=out:st=194.7:d=0.3[out]",
             "-map", "[out]", "-c:a", "pcm_s24le", "-ar", RATE, wav])
    (WORK / "normalization-second-pass.log").write_text(p.stderr, encoding="utf-8")
    aligned = OUT / "oxyproof-owner-narration-aligned.m4a"
    run([BIN / "ffmpeg.exe", "-v", "error", "-n", "-i", wav, "-map", "0:a:0", "-map_metadata", "-1",
         "-c:a", "aac", "-b:a", "192k", "-ar", RATE, "-movflags", "+faststart", aligned])
    for variant in ("clean", "subtitled"):
        source = OUT / f"oxyproof-browser-demo-final-{variant}.mp4"
        dest = OUT / f"oxyproof-browser-demo-final-{variant}-narrated.mp4"
        run([BIN / "ffmpeg.exe", "-v", "error", "-n", "-i", source, "-i", aligned,
             "-map", "0:v:0", "-map", "1:a:0", "-map_metadata", "-1", "-c", "copy", "-t", "195",
             "-metadata:s:a:0", "language=eng", "-disposition:a:0", "default", "-movflags", "+faststart", dest])
        print("MUXED", dest.name, flush=True)
    source_info = probe(SOURCE)
    write(REVIEW / "mix-configuration.json", {
        "source_audio_file": SOURCE.name, "source_audio_sha256": sha(SOURCE),
        "source_audio_duration_s": float(source_info["format"]["duration"]),
        "source_sample_rate": RATE, "source_channels": 2,
        "video_duration_s": 195, "video_speed_changed": False, "video_reencoded": False,
        "voice_speed_or_pitch_changed": False, "voice_synthesized": False,
        "pause_insertion_source_time_s": PAUSE_AT, "pause_added_s": PAUSE_ADDED,
        "quiet_interval_source_s": [185.285521, 185.808521], "quiet_detection_threshold_db": -48,
        "ending_source_speech_end_approx_s": 188.653292, "ending_output_speech_end_approx_s": 193.303292,
        "alignment_method": "Preserve main narration timing; add a pause at the measured quiet gap before the early closing line, then pad to 195 s. No word edits or retiming of body narration.",
        "alignment_qualification": "Local ASR has recognition/timestamp errors and was used only as an approximate chapter aid; not a certified transcript or manual listening.",
        "processing": ["70 Hz high-pass", "two-pass dynamic loudness normalization: -16 LUFS / -1.5 dBTP", "20 ms opening fade and 300 ms ending fade in tail silence", "AAC 192 kb/s stereo at 48 kHz"],
        "first_pass_measurement": measured, "second_pass_measurement": loudness(p.stderr),
        "subtitle_policy": "Original concise action-summary subtitles retained, not a verbatim transcript of simplified narration.",
        "protected_inputs": count, "new_browser_actions": 0, "new_science_model_calls": 0,
        "local_asr": "whisper.cpp v1.8.4 / base.en-q5_1, CPU; no audio upload",
        "raw_recording_in_public_output": False})
    print("MIX_COMPLETE; PROTECTED_INPUTS_UNCHANGED", protected(), flush=True)


def stream_hash(path, kind):
    return run([BIN / "ffmpeg.exe", "-v", "error", "-i", path, "-map", f"0:{kind}:0", "-c", "copy",
                "-f", "hash", "-hash", "sha256", "-"]).stdout.strip()


def verify():
    results = []
    for variant in ("clean", "subtitled"):
        source = OUT / f"oxyproof-browser-demo-final-{variant}.mp4"
        dest = OUT / f"oxyproof-browser-demo-final-{variant}-narrated.mp4"
        info = probe(dest)
        assert len(info["streams"]) == 2
        video, audio = [next(s for s in info["streams"] if s["codec_type"] == k) for k in ("video", "audio")]
        assert [video[k] for k in ("codec_name", "width", "height", "r_frame_rate", "nb_frames")] == ["h264", 1920, 1080, "30/1", "5850"]
        assert video["pix_fmt"] == "yuv420p" and video["color_range"] == "tv"
        assert audio["codec_name"] == "aac" and audio["sample_rate"] == "48000" and audio["channels"] == 2
        assert abs(float(info["format"]["duration"]) - 195) < .025
        assert abs(float(video["start_time"])) < .00001 and abs(float(audio["start_time"])) < .00001
        assert abs(float(audio["duration"]) - 195) < .025
        before = stream_hash(source, "v")
        after = stream_hash(dest, "v")
        assert before == after, "Video elementary stream changed"
        audio_hash = stream_hash(dest, "a")
        assert audio_hash == stream_hash(OUT / "oxyproof-owner-narration-aligned.m4a", "a")
        decoded = run([BIN / "ffmpeg.exe", "-v", "error", "-threads", "1", "-xerror", "-i", dest,
                       "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"])
        (REVIEW / f"{variant}-full-decode.log").write_text(decoded.stderr, encoding="utf-8")
        results.append({"file": dest.name, "bytes": dest.stat().st_size, "sha256": sha(dest),
                        "duration_s": float(info["format"]["duration"]), "width": 1920, "height": 1080,
                        "fps": 30, "video_frames": 5850, "audio_codec": "aac", "audio_sample_rate": 48000,
                        "audio_channels": 2, "video_stream_copy_hash": after, "video_payload_unchanged": True,
                        "audio_start_s": float(audio["start_time"]), "audio_duration_s": float(audio["duration"]),
                        "audio_payload_matches_aligned_master": True, "full_audio_video_decode": "PASS"})
        print("FULL_AUDIO_VIDEO_DECODE_PASS", dest.name, flush=True)
    aligned = OUT / "oxyproof-owner-narration-aligned.m4a"
    p = run([BIN / "ffmpeg.exe", "-hide_banner", "-nostats", "-i", aligned,
             "-af", "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"])
    level = loudness(p.stderr)
    (REVIEW / "final-audio-loudness.log").write_text(p.stderr, encoding="utf-8")
    assert -17.5 <= float(level["input_i"]) <= -14.5
    assert float(level["input_tp"]) < -.5, "True-peak headroom too small"
    write(REVIEW / "verification.json", {"technical_status": "PASS", "outputs": results,
          "final_audio_loudness": level, "protected_inputs_unchanged": protected(),
          "video_visual_review": "Inherited validated final-polish frames; entire video payload hash identical",
          "manual_audio_listening": "NOT_RUN: tool runtime does not support audio input; no human-listening claim",
          "alignment_status": "Approximate chapter match, preserved speech speed, closing pause aligned to final dashboard",
          "subtitle_status": "Unchanged original action-summary captions", "application_tests": "NOT_RUN: media-only mix",
          "new_browser_actions": 0, "new_science_model_calls": 0})
    print("VERIFICATION_PASS", "integrated_LUFS", level["input_i"], "true_peak_dBTP", level["input_tp"],
          "protected", protected(), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("mix", "verify"))
    args = parser.parse_args()
    {"mix": mix, "verify": verify}[args.action]()
