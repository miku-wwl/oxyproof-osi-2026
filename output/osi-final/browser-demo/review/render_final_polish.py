"""Media-only polish: reuse verified annotations, omit engineering text layers.

No browser/app/model calls. Pointer glyphs remain reconstructed from logged
targets/endpoints, never a claim of native mouse capture. Existing assets are
read-only. Outputs, evidence and private caches use new names.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
# Do not regenerate caches beside the preserved original renderer.
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("accepted_cursor", HERE / "render_cursor_demo.py")
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
ROOT, OUT, BIN = old.ROOT, old.OUT, old.BIN
SIZE, FPS, FRAMES = old.SIZE, old.FPS, old.FRAMES
REVIEW = HERE / "polish"
WORK = ROOT / ".local/final-video-polish"
PLAN = HERE / "cursor/annotation-plan.json"
MOMENTS = [1, 4.2, 6.3, 15.25, 17.2, 17.7, 19.3, 28.33, 28.83,
           47.2, 48.3, 49, 52.15, 53.25, 54, 57.2, 58.25, 59.5,
           63, 79.5, 85.5, 91, 108.33, 108.8, 113.5, 130.5,
           136.3, 136.8, 147, 160, 177.45, 177.95, 184, 193]


def write(path, data):
    with path.open("x", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def draw_overlay(t, live):
    # Identical geometry/colors/timing to the accepted renderer. Its text tags
    # and introductory disclosure are omitted; disclosure remains in the report.
    im = Image.new("RGBA", (3840, 2160), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def cursor(p):
        x, y = p
        pts = [(x + dx, y + dy) for dx, dy in
               [(0, 0), (0, 22), (6, 17), (10, 27), (14, 25), (10, 15), (18, 15)]]
        d.polygon([(round(x * 2), round(y * 2)) for x, y in pts],
                  fill="white", outline=(18, 27, 31, 255), width=4)

    for a in live:
        l, y, r, b = a.get("control_tracking", {}).get("rect_by_output_frame", {}).get(
            str(round(t * FPS)), a["target_rect_output_px"])
        start, end = a["video_interval_s"]
        if a["kind"] == "drag_endpoints":
            p, q = a["output_endpoints"]
            for x0, y0 in (p, q):
                d.ellipse(((x0 - 5) * 2, (y0 - 5) * 2, (x0 + 5) * 2, (y0 + 5) * 2),
                          outline=(35, 136, 148, 180), width=3)
            if t < start + .27:
                cursor(p)
            elif t >= a["call_interval_s"][1] - .33:
                cursor(q)
        else:
            box = [round(v * 2) for v in (l - 3, y - 3, r + 3, b + 3)]
            d.rounded_rectangle(box, radius=8, outline=(17, 42, 51, 160), width=7)
            d.rounded_rectangle(box, radius=8, outline=(52, 170, 170, 160), width=3)
            if a["kind"] == "logged_target":
                p = a["output_point"]
                cursor(p)
                dt = t - start
                if 0 <= dt < .4:
                    rad = 11 + 9 * dt / .4
                    alpha = round(210 * (1 - dt / .4))
                    x0, y0 = p
                    d.ellipse(((x0 - rad) * 2, (y0 - rad) * 2,
                               (x0 + rad) * 2, (y0 + rad) * 2),
                              outline=(12, 101, 124, alpha), width=5)
    return im.resize(SIZE, Image.Resampling.LANCZOS)


def protected_check():
    protected = old.read(WORK / "protected-before.json")
    # Another independent session is upgrading the installed skill concurrently.
    # It is outside this task; never restore/overwrite that session's changes.
    # Python cache files are derived artifacts, not accepted source/media.
    protected = {p: digest for p, digest in protected.items()
                 if "/__pycache__/" not in p.replace("\\", "/")
                 and "/.codex/skills/codex-iab-video-recording/" not in p.replace("\\", "/")}
    bad = [p for p, digest in protected.items() if old.sha(Path(p)) != digest]
    assert not bad, f"Protected files changed: {bad}"
    return len(protected)


def prepare():
    REVIEW.mkdir(exist_ok=True)
    assert not (REVIEW / "configuration-and-evidence.json").exists(), "Preparation already complete"
    overlay_dir = WORK / "overlays"
    overlay_dir.mkdir(exist_ok=True)
    protected_check()
    plan = old.read(PLAN)
    provenance = old.read(HERE / "recording-provenance.json")
    for take in provenance["takes"]:
        manifest = ROOT / take["manifest"]
        assert old.sha(manifest) == take["manifest_sha256"]
    active, max_pixels, comparison_count, uncovered_cursor_frames = [], 0, 0, []
    for n in range(FRAMES):
        t = n / FPS
        live = [a for a in plan["annotations"] if
                a["video_interval_s"][0] <= t < a["video_interval_s"][1]]
        if not live:
            continue
        im = draw_overlay(t, live)
        alpha = im.getchannel("A")
        assert alpha.getbbox()
        assert alpha.crop((0, 996, 1920, 1080)).getbbox() is None
        max_pixels = max(max_pixels, 1920 * 1080 - alpha.histogram()[0])
        # Retained effects are pixel-identical outside the removed tag footprint.
        # A prior drag label painted over a few arrow-tail pixels; removing that
        # tag correctly reveals the original arrow underneath rather than erasing it.
        with Image.open(old.WORK / f"overlay-{n:04d}.png") as prior:
            diff = ImageChops.difference(im, prior.convert("RGBA"))
            support = alpha.point(lambda x: 255 if x else 0)
            for a in live:
                if a["kind"] == "drag_endpoints":
                    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 36)
                    right = 1050 + (ImageDraw.Draw(im).textlength(a["label_text"], font=font) + 20) / 2
                    tag_box = (1047, 508, math.ceil(right) + 3, 538)
                    if any(ImageChops.multiply(c, support).crop(tag_box).getbbox()
                           for c in diff.split()):
                        uncovered_cursor_frames.append(n)
                    ImageDraw.Draw(support).rectangle(tag_box, fill=0)
            assert all(ImageChops.multiply(c, support).getbbox() is None
                       for c in diff.split()), f"Retained effect changed at frame {n}"
        comparison_count += 1
        im.save(overlay_dir / f"{n:04d}.png", compress_level=1)
        active.append(n)
    assert len(plan["annotations"]) == 12 and max_pixels / (1920 * 1080) < .02
    # The old introductory note is not part of the scientific UI/subtitles.
    assert not set(range(12, 90)).intersection(active)
    evidence = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "render_configuration": {"engineering_labels": False, "introductory_engineering_note": False,
                                 "cursor_glyphs": True, "click_rings": True,
                                 "control_outlines": True, "slider_endpoints": True,
                                 "interpolated_motion": False, "native_mouse_capture_claim": False},
        "annotation_plan": str(PLAN.relative_to(ROOT)), "annotation_plan_sha256": old.sha(PLAN),
        "active_frames": active, "nonempty_overlay_frames": len(active),
        "retained_effect_frame_comparisons": comparison_count,
        "retained_effects_pixel_identical_outside_removed_tag_footprint": True,
        "cursor_tail_uncovered_by_tag_removal_frames": uncovered_cursor_frames,
        "maximum_annotation_canvas_fraction": max_pixels / (1920 * 1080),
        "subtitle_strip_alpha": "ZERO", "unchanged_annotations": plan["annotations"],
        "protected_files": protected_check(), "new_browser_actions": 0, "new_model_calls": 0,
        "method": "Recompose accepted original browser MP4s with identical verified effect layers; omit all overlay text tags and introduction. No erasure/inpainting."
    }
    write(REVIEW / "configuration-and-evidence.json", evidence)
    print("PREPARED", len(active), "effect frames;", comparison_count,
          "retained effect comparisons; protected", evidence["protected_files"], flush=True)
    # Short source-based PNG previews first; final MP4 frames are inspected later.
    for t in (28.33, 47.2, 58.25, 108.8, 136.8, 177.45):
        n = round(t * FPS)
        src = OUT / "oxyproof-browser-demo-subtitled.mp4"
        raw = old.run([BIN / "ffmpeg.exe", "-v", "error", "-n", "-ss", n / FPS,
                       "-threads", "1", "-i", src, "-frames:v", "1", "-threads", "1",
                       REVIEW / f"preview-source-{n}.png"])
        with Image.open(REVIEW / f"preview-source-{n}.png") as frame:
            frame = frame.convert("RGB")
            if n in active:
                with Image.open(overlay_dir / f"{n:04d}.png") as ann:
                    frame.paste(ann, (0, 0), ann)
            frame.save(REVIEW / f"preview-final-{n}.png")


def render():
    active = set(old.read(REVIEW / "configuration-and-evidence.json")["active_frames"])
    for variant in ("clean", "subtitled"):
        src = OUT / f"oxyproof-browser-demo-{variant}.mp4"
        dest = OUT / f"oxyproof-browser-demo-final-{variant}.mp4"
        assert not dest.exists(), "Refuse to overwrite output"
        chunks = []
        for start in range(0, FRAMES, 900):
            count = min(900, FRAMES - start)
            encoded = WORK / f"segment-{variant}-{start:04d}.mp4"
            assert not encoded.exists(), "Refuse to overwrite private segment"
            prefix = f"segment-{variant}-{start:04d}"
            with (WORK / f"{prefix}-decode.log").open("xb") as de, (WORK / f"{prefix}-encode.log").open("xb") as en:
                # Accurate seek during transcoding, then exact integer frame count.
                dec = subprocess.Popen([str(x) for x in [BIN / "ffmpeg.exe", "-v", "error", "-threads", "1",
                    "-ss", start / FPS, "-i", src, "-map", "0:v:0", "-an", "-frames:v", count,
                    "-filter_threads", "1", "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1"]],
                    stdout=subprocess.PIPE, stderr=de)
                enc = subprocess.Popen([str(x) for x in [BIN / "ffmpeg.exe", "-v", "error", "-n",
                    "-thread_queue_size", "1", "-f", "rawvideo", "-pixel_format", "rgb24",
                    "-video_size", "1920x1080", "-framerate", FPS, "-i", "pipe:0", "-filter_threads", "1",
                    "-vf", "scale=in_range=pc:out_range=tv,format=yuv420p", "-an", "-frames:v", count,
                    "-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency", "-crf", "14",
                    "-threads", "1", "-pix_fmt", "yuv420p", "-color_range", "tv", encoded]],
                    stdin=subprocess.PIPE, stderr=en)
                try:
                    frame_bytes = SIZE[0] * SIZE[1] * 3
                    for n in range(start, start + count):
                        raw = dec.stdout.read(frame_bytes)
                        assert len(raw) == frame_bytes, f"Truncated original frame {n}"
                        if n in active:
                            im = Image.frombytes("RGB", SIZE, raw)
                            with Image.open(WORK / "overlays" / f"{n:04d}.png") as ann:
                                im.paste(ann, (0, 0), ann)
                            raw = im.tobytes()
                        enc.stdin.write(raw)
                    assert not dec.stdout.read(1), "Unexpected extra segment frames"
                    dec.stdout.close()
                    enc.stdin.close()
                    assert dec.wait() == 0 and enc.wait() == 0, "See private segment logs"
                finally:
                    for child in (dec, enc):
                        if child.poll() is None:
                            child.kill()
                            child.wait()
            probe = json.loads(old.run([BIN / "ffprobe.exe", "-v", "error", "-show_streams", "-of", "json", encoded]))
            assert int(probe["streams"][0]["nb_frames"]) == count
            chunks.append((encoded, count))
            print("SEGMENT_COMPLETE", variant, start + count, "/", FRAMES, flush=True)
        concat = WORK / f"final-{variant}.ffconcat"
        with concat.open("x", encoding="utf-8") as f:
            f.write("ffconcat version 1.0\n")
            for encoded, count in chunks:
                f.write(f"file '{encoded.as_posix()}'\nduration {count / FPS:.12f}\n")
        old.run([BIN / "ffmpeg.exe", "-v", "error", "-n", "-f", "concat", "-safe", "0", "-i", concat,
                 "-map", "0:v:0", "-c:v", "copy", "-bsf:v", "h264_metadata=video_full_range_flag=0",
                 "-an", "-movflags", "+faststart", dest])
        print("RENDERED", dest.name, flush=True)
    protected_check()


def verify():
    media = []
    select = "+".join(f"eq(n,{round(t * FPS)})" for t in MOMENTS)
    for variant in ("clean", "subtitled"):
        path = OUT / f"oxyproof-browser-demo-final-{variant}.mp4"
        info = json.loads(old.run([BIN / "ffprobe.exe", "-v", "error", "-show_streams",
                                  "-show_format", "-of", "json", path]))
        assert len(info["streams"]) == 1
        s = info["streams"][0]
        assert [s[k] for k in ("codec_name", "width", "height", "pix_fmt", "r_frame_rate", "nb_frames")] == [
            "h264", 1920, 1080, "yuv420p", "30/1", "5850"]
        assert s["color_range"] == "tv" and float(info["format"]["duration"]) == 195
        packets = json.loads(old.run([BIN / "ffprobe.exe", "-v", "error", "-select_streams", "v:0",
                                      "-show_entries", "packet=pts_time,duration_time", "-of", "json", path]))["packets"]
        assert len(packets) == FRAMES
        assert all(abs(float(p["pts_time"]) - n / FPS) < .00001
                   and abs(float(p["duration_time"]) - 1 / FPS) < .00001
                   for n, p in enumerate(packets)), "Gap/duplicate/timing drift at a segment boundary"
        import struct
        atoms = []
        with path.open("rb") as f:
            while header := f.read(8):
                length, kind = struct.unpack(">I4s", header)
                header_length = 8
                if length == 1:
                    length = struct.unpack(">Q", f.read(8))[0]
                    header_length = 16
                atoms.append(kind.decode("ascii"))
                if length == 0:
                    break
                f.seek(length - header_length, 1)
        assert atoms.index("moov") < atoms.index("mdat"), "Faststart metadata missing"
        proc = subprocess.run([str(x) for x in [BIN / "ffmpeg.exe", "-hide_banner", "-v", "info",
            "-threads", "1", "-xerror", "-i", path, "-filter_threads", "1", "-vf",
            "blackdetect=d=0:pic_th=0.98:pix_th=0.02", "-f", "null", "-"]], capture_output=True, text=True)
        (REVIEW / f"{variant}-full-decode.log").write_text(proc.stderr, encoding="utf-8")
        assert proc.returncode == 0, proc.stderr[-2000:]
        assert "black_start:" not in proc.stderr, "Unexpected nearly-black frames"
        old.run([BIN / "ffmpeg.exe", "-v", "error", "-n", "-threads", "1", "-filter_threads", "1",
                 "-i", path, "-vf", f"select='{select}'", "-fps_mode", "vfr", "-frames:v", len(MOMENTS),
                 "-threads", "1", "-q:v", "2", REVIEW / f"{variant}-qa-%02d.jpg"])
        contact = Image.new("RGB", (1920, math.ceil(len(MOMENTS) / 4) * 300), "#111418")
        d = ImageDraw.Draw(contact)
        for i, t in enumerate(MOMENTS):
            with Image.open(REVIEW / f"{variant}-qa-{i + 1:02d}.jpg") as im:
                thumb = im.resize((480, 270), Image.Resampling.LANCZOS)
            x, y = i % 4 * 480, i // 4 * 300
            contact.paste(thumb, (x, y))
            d.text((x + 8, y + 275), f"{t:.2f} s", fill="white")
        contact.save(REVIEW / f"{variant}-contact.jpg", quality=94)
        media.append({"file": path.name, "bytes": path.stat().st_size, "sha256": old.sha(path),
                      "width": 1920, "height": 1080, "fps": 30, "frames": 5850,
                      "duration_s": 195, "audio_streams": 0, "codec": "h264", "pixel_format": "yuv420p",
                      "color_range": "tv", "full_decode": "PASS", "black_frame_detection": "NONE",
                      "packet_timestamp_check": "PASS: all 5850 frames at n/30 seconds, no gaps/duplicates",
                      "faststart": True})
        print("FULL_DECODE_PASS", path.name, flush=True)
    # Explicit scientific-disclosure and subtitle timing checks, without inference.
    srt = (OUT / "oxyproof-browser-demo.srt").read_text(encoding="utf-8")
    for disclosure in ("Calculated fits, not measured crossovers", "No\nuncertainty bounds",
                       "recorded DeepSeek", "No new inference", "Independent auditing",
                       "INSUFFICIENT_EVIDENCE"):
        assert disclosure in srt
    import re
    cues = re.findall(r"(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)", srt)
    assert len(cues) == 25
    def seconds(text):
        h, m, s = text.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    assert all(0 <= seconds(a) < seconds(b) <= 195 for a, b in cues)
    assert all(seconds(cues[i][1]) <= seconds(cues[i + 1][0]) for i in range(24))
    write(REVIEW / "verification.json", {
        "technical_status": "PASS", "visual_review": "PENDING",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(), "media": media,
        "protected_files_unchanged": protected_check(), "subtitle_cues": len(cues),
        "srt_sha256": old.sha(OUT / "oxyproof-browser-demo.srt"),
        "subtitle_timing": "Original burned-in subtitle footage retained without retiming; annotation alpha zero below y=996",
        "scientific_disclosures": "PRESERVED", "new_browser_actions": 0, "new_model_calls": 0,
        "application_tests": "NOT_RUN: media-only edit", "browser_continuous_playback": "NOT_RUN in this polish revision"})
    print("VERIFICATION_PASS; visual inspection pending;", protected_check(), "protected files unchanged", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "render", "verify"))
    args = parser.parse_args()
    {"prepare": prepare, "render": render, "verify": verify}[args.action]()
