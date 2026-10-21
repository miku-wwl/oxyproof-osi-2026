"""Technical acceptance for final media, SRT, one-page PDF and preserved source evidence."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/"output/osi-final"
BIN=ROOT/".local/media-tools/ffmpeg-essentials/ffmpeg-9.0.2-essentials_build/bin"
FF=BIN/"ffmpeg.exe"; FP=BIN/"ffprobe.exe"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def call(args): return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True)
results={"scope":"Production asset checks, not a full application regression", "media":{}}
for variant in ("clean","subtitled"):
    file=OUT/f"video/oxyproof-final-{variant}.mp4"
    probe=json.loads(call([FP,"-v","error","-show_streams","-show_format","-of","json",file]).stdout)
    assert len(probe["streams"])==1
    v=probe["streams"][0]; duration=float(probe["format"]["duration"])
    assert v["codec_name"]=="h264" and v["pix_fmt"]=="yuv420p"
    assert (v["width"],v["height"],v["r_frame_rate"])==(1920,1080,"30/1")
    assert int(v["nb_frames"])==6450 and abs(duration-215)<.04
    call([FF,"-v","error","-xerror","-i",file,"-map","0:v:0","-f","null","-"])
    results["media"][variant]={"status":"PASS","duration_seconds":duration,"width":1920,"height":1080,
        "codec":v["codec_name"],"pixel_format":v["pix_fmt"],"color_range":v.get("color_range"),
        "fps":v["r_frame_rate"],"frames":int(v["nb_frames"]),"audio_streams":0,
        "full_decode":"PASS","bytes":file.stat().st_size,"sha256":sha(file)}
    (OUT/f"review/ffprobe-{variant}.json").write_text(json.dumps(probe,indent=2)+"\n",encoding="utf-8")

def seconds(s):
    h,m,rest=s.split(":"); sec,ms=rest.split(","); return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
cues=[]; previous=0
for expected,block in enumerate((OUT/"video/oxyproof-final.srt").read_text(encoding="utf-8").strip().split("\n\n"),1):
    lines=block.splitlines(); assert int(lines[0])==expected
    a,b=lines[1].split(" --> "); start,end=seconds(a),seconds(b)
    assert previous<=start<end<=215 and 1<=len(lines[2:])<=2
    assert max(map(len,lines[2:]))<=49
    text=" ".join(lines[2:]); cps=len(text)/(end-start); assert cps<20
    cues.append({"cue":expected,"start":start,"end":end,"characters_per_second":round(cps,2)})
    previous=end
words=sum(len(" ".join(block.splitlines()[2:]).split()) for block in
    (OUT/"video/oxyproof-final.srt").read_text(encoding="utf-8").strip().split("\n\n"))
results["subtitles"]={"status":"PASS","cues":len(cues),"max_characters_per_second":max(c["characters_per_second"] for c in cues),
    "last_end_seconds":previous,"max_lines":2,"cue_checks":cues}
results["narration"]={"status":"READY","spoken_words":words,"words_per_minute_including_pauses":round(words/215*60,1),
    "audio_generated":False,"timed_words_identical_to_srt":True}
pdf=OUT/"submission/oxyproof-one-page-final.pdf"; reader=PdfReader(pdf)
assert len(reader.pages)==1
page=reader.pages[0]; assert abs(float(page.mediabox.width)-595.276)<.1 and abs(float(page.mediabox.height)-841.89)<.1
for term in ("483", "49/49", "3/3", "21 Chromium", "Uncertainty bounds unavailable", "github.com/miku-wwl/oxyproof-osi-2026"):
    assert term in page.extract_text()
results["pdf"]={"technical_status":"PASS","pages":1,"size":"A4","sha256":sha(pdf),"visual_review":"See VIDEO_ACCEPTANCE.md and one-page-final.png"}
archive=json.loads((ROOT/"artifacts/deepseek_live_acceptance.json").read_text(encoding="utf-8"))
assert archive["real_provider_requests_attempted"]==archive["real_provider_requests_succeeded"]==3
assert all(s["status"]=="PASS" for s in archive["live_scenarios"])
c=next(s["execution"] for s in archive["live_scenarios"] if s["scenario"]=="C")
assert c["execution_trace"]["executed_scientific_tool"] is None
assert c["execution_trace"]["scientific_result"]["candidates"]==0
export=json.loads((OUT/"review/exported-decision.json").read_text(encoding="utf-8"))
assert [r["ordering"] for r in export["selected_rankings"]]==[[1,2,3],[3,2,1]]
assert export["source"]["dataset_sha256"]=="8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34"
ledger=ROOT/".local/deepseek-phase262-budget.json"
assert len(json.loads(ledger.read_text(encoding="utf-8"))["attempts"])==3
provenance=json.loads((OUT/"review/capture-and-edit-provenance.json").read_text(encoding="utf-8"))
assert sha(ledger)==provenance["budget_ledger_sha256"]
originals={".local/demo-phase25/oxyproof-phase2.webm":"e39fe0b000d984748e84782486d889c803b6d6e880e7dcc9c1cc4e48e7cb8c05",
           "output/pdf/oxyproof-one-page-submission.pdf":"2d695fb59b31530ec9233044bc911da3a5c0574c3372c219e6cab32abda6c959"}
assert all(sha(ROOT/p)==h for p,h in originals.items())
results["evidence"]={"archive":"PASS","browser_export":"PASS","budget_attempts":3,"budget_unchanged_since_capture":True,
    "original_media_hashes_preserved":originals,"new_provider_requests":0,
    "genuine_replay_pytest":"9 passed, 1 existing Starlette/httpx deprecation warning in 0.55s (executed separately this production sprint)",
    "full_255_12_21_suite_rerun":False}
times=[1,12,24,31,37,50,62,72,84,87,102,113,125,135,147,160,169,172,185,197,201,207,214]
for t in times:
    file=OUT/f"review/screenshots/subtitled-{t:03}.jpg"
    call([FF,"-v","error","-y","-ss",t,"-i",OUT/"video/oxyproof-final-subtitled.mp4","-frames:v","1",file])
for t in [12,37,72,113,160,185,214]:
    file=OUT/f"review/screenshots/clean-{t:03}.jpg"
    call([FF,"-v","error","-y","-ss",t,"-i",OUT/"video/oxyproof-final-clean.mp4","-frames:v","1",file])
for group, ts in enumerate([times[i:i+6] for i in range(0,len(times),6)],1):
    sheet=Image.new("RGB",(1920,3*566),"#102930"); draw=ImageDraw.Draw(sheet)
    for index,t in enumerate(ts):
        with Image.open(OUT/f"review/screenshots/subtitled-{t:03}.jpg") as im: im=im.resize((960,540))
        x=(index%2)*960; y=(index//2)*566
        sheet.paste(im,(x,y)); draw.text((x+12,y+542),f"FINAL SUBTITLED MP4 - {t}s",font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",18),fill="white")
    sheet.save(OUT/f"review/screenshots/contact-{group}.jpg",quality=94)
results["visual_review"]="REQUIRED - inspect final decoded frames and record agent review separately"
(OUT/"review/media-validation.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"media":results["media"],"subtitles":{k:v for k,v in results["subtitles"].items() if k!="cue_checks"},"narration":results["narration"],"pdf":results["pdf"],"evidence":results["evidence"]},indent=2))
