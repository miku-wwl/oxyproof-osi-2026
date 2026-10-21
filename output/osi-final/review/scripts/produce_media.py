"""Reproducible silent edit of genuine timestamped IAB captures; no browser or model calls.

Run with the existing private capture directory. Raw frames are never packaged.
"""
import bisect
import hashlib
import json
import subprocess
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output/osi-final"
RAW = ROOT / ".local/osi-final-capture"
WORK = ROOT / ".local/osi-final-render"
FF = ROOT / ".local/media-tools/ffmpeg-essentials/ffmpeg-9.0.2-essentials_build/bin/ffmpeg.exe"
FP = FF.with_name("ffprobe.exe")
FONT = Path("C:/Windows/Fonts/segoeui.ttf")
BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")
SCENES = [
    ("scene1",25,"01  THE RESEARCH QUESTION", "A decision that depends on temperature"),
    ("scene2a",35,"02  FLAGSHIP SCIENCE", "Same source group. A different preferred material."),
    ("scene2b",25,"02  MODEL INTERSECTIONS", "Calculated crossings and fit boundaries are different events"),
    ("scene3a",10,"03  GENUINE MODEL EVIDENCE", "Load archived DeepSeek executions"),
    ("scene3b",35,"03  GENUINE MODEL EVIDENCE", "Scenario B: the model selects an interval-analysis tool"),
    ("scene4",40,"04  SCIENTIFIC ABSTENTION", "Unsupported conditions stop a recommendation"),
    ("scene5",30,"05  REPRODUCIBILITY", "Inspect the source. Export the decision."),
    ("closing",15,"06  OXYPROOF", "AI can assist the decision without inventing the science"),
]
TAKE_NAMES={"scene4":"scene4-final", "scene5":"scene5-final"}
CUES = [
(.5,5.1,"What if the best material changes when the operating temperature changes?"),
(5.3,10.1,"Oxygen-ion conductors matter to electrochemical technologies, but selection is conditional."),
(10.3,15.1,"A choice at one temperature may change across a device's working range."),
(15.3,20.1,"Researchers also need comparable measurements, explicit models and traceable evidence."),
(20.3,24.8,"OxyProof brings those checks into a research workbench that makes its limits visible."),
(25.2,30.8,"We start with three published bulk-conductivity records from the same curated source group."),
(31,35.4,"They share a reported method and measured range: 600 to 1100 kelvin."),
(35.6,39.8,"At 700 kelvin, row one leads: one, then two, then three."),
(40,48.7,"Move the actual temperature control, and the conditional model ordering begins to change."),
(49,54.3,"At 1000 kelvin, row three leads: three, then two, then one."),
(54.5,59.8,"The result follows activation energies, prefactors and the selected temperature regimes."),
(60,65.1,"Analytical crossings are audited separately from changes in the selected fitted regime."),
(65.3,70.7,"The model intersections are near 776, 818 and 854 kelvin, inside valid joint regimes."),
(70.9,76.3,"These are calculated intersections of fitted models, not experimentally measured crossovers."),
(76.5,80.7,"At a published T-star boundary, the affected source row is withheld."),
(80.9,84.8,"No uncertainty bounds are available. Experimental confirmation is needed."),
(85.3,90.5,"Next, we load saved traces from three genuine DeepSeek API acceptance calls."),
(90.7,95.7,"These executions were captured earlier; playback makes no new model request."),
(95.9,101,"Scenario B asks how the named Huang group's ranking changes with temperature."),
(101.2,106.3,"DeepSeek Flash selected the allowlisted temperature-interval analysis tool."),
(106.5,111.5,"The interface shows the real provider identity and the model-selected operation."),
(111.7,117,"Validated arguments retain 700 to 1000 kelvin, bulk conductivity and three source rows."),
(117.2,123,"The model selects the tool. The validated physics engine supplies the numerical results."),
(123.2,129.6,"Independent auditing controls the verdict and explains the validated result."),
(130.3,135.4,"Now add demanding requirements: 600 degrees Celsius and ten percent humidity."),
(135.6,140.7,"Also require stability for ten thousand operating hours, rather than just conductivity."),
(140.9,146,"The recorded model proposed screening and flagged unsupported requirements."),
(146.2,151.3,"Independent validation checked the original request, retaining humidity and lifetime."),
(151.5,156.6,"The available records do not establish those properties, so scientific execution was blocked."),
(156.8,162,"No scientific calculation tool ran, and no unsupported recommendation was produced."),
(162.2,166.1,"The result is insufficient evidence, with a proposed future measurement."),
(166.3,169.8,"When evidence is missing, OxyProof refuses to guess."),
(170.3,176,"Every result remains tied to the published dataset, original source rows and explicit units."),
(176.2,181.8,"The parameters, selected regimes and evidence limits remain visible for researcher review."),
(182,188.8,"Shared source metadata supports comparison, but sample conditions still need review."),
(189,194.6,"The actual JSON export preserves the source records and deterministic calculation trace."),
(194.8,199.7,"Warnings and code fingerprints travel with the report, supporting offline reproduction."),
(200.3,205.2,"OxyProof explains when the answer changes and why it changes."),
(205.4,209.8,"It also shows where the evidence stops, so a researcher can decide what to check next."),
(210,214.6,"AI can assist scientific decision-making without being allowed to invent the science."),
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def font(size,bold=False): return ImageFont.truetype(str(BOLD if bold else FONT),size)
def stamp(t):
    ms=round(t*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
def wrap(value,width=49): return textwrap.wrap(value,width=width,break_long_words=False,break_on_hyphens=False)
def addtext(draw,xy,value,size=27,bold=False,fill="#d1e6e4",width=None,spacing=10):
    x,y=xy
    lines=[line for paragraph in value.split("\n")
           for line in (wrap(paragraph,width) if width and paragraph else [paragraph])]
    for line in lines:
        draw.text((x,y),line,font=font(size,bold),fill=fill); y+=size+spacing
    return y

def editorial(source,name,section,title):
    im=Image.new("RGB",(1920,1080),"#102930"); d=ImageDraw.Draw(im)
    d.rectangle((0,0,1920,96),fill="#143a41")
    addtext(d,(28,18),"OXYPROOF",30,True,"#f4f7f3")
    addtext(d,(248,15),title,29,True,"#ffffff")
    replay=name in ("scene3a","scene3b","scene4")
    mode=("Recorded genuine DeepSeek API execution - replay, not a new model call" if replay
          else "OFFLINE_DETERMINISTIC  |  Published data  |  Conditional model calculations")
    addtext(d,(248,58),mode,23,False,"#b9e4d0" if not replay else "#ffe0a5")
    if source is not None:
        view=ImageOps.contain(source.convert("RGB"),(1536,864),Image.Resampling.LANCZOS)
        im.paste(view,(20+(1536-view.width)//2,110+(864-view.height)//2))
    d=ImageDraw.Draw(im)
    addtext(d,(1584,119),section,19,True,"#9bc9c1",width=23)
    d.line((1584,183,1890,183),fill="#466168",width=2)
    if name=="scene1":
        addtext(d,(1584,214),"What if the best material changes?",38,True,"#ffffff",width=14,spacing=7)
        addtext(d,(1584,480),"483 published records\n\nReal calculations\n\nExplicit limits",28,width=22)
    elif name=="scene2a":
        addtext(d,(1584,215),"MODEL ORDER",23,True)
        addtext(d,(1584,282),"700 K",34,True,"#b5e7d8")
        addtext(d,(1584,333),"1 > 2 > 3",43,True,"#ffffff")
        addtext(d,(1584,435),"1000 K",34,True,"#b5e7d8")
        addtext(d,(1584,486),"3 > 2 > 1",43,True,"#ffffff")
        addtext(d,(1584,636),"Rows 1 / 2 / 3\nBulk · two-probe AC\n600-1100 K",24,width=22)
    elif name=="scene2b":
        addtext(d,(1584,215),"MODEL ROOTS",24,True)
        addtext(d,(1584,281),"~776 K\n~818 K\n~854 K",43,True,"#ffffff",spacing=22)
        addtext(d,(1584,531),"Calculated fit intersections.\n\nNot measured crossovers.\n\nNo validated uncertainty bounds.",26,width=21)
    elif name=="scene3a":
        addtext(d,(1584,218),"ARCHIVED EVIDENCE",29,True,"#ffe0a5",width=17)
        addtext(d,(1584,355),"21 OCT 2026\n\n3 genuine calls\n\nNo fresh inference",29,width=19)
    elif name=="scene3b":
        addtext(d,(1584,215),"DeepSeek\ndeepseek-flash",29,True,"#ffe0a5")
        addtext(d,(1584,350),"MODEL SELECTS\nInterval analysis\n\nENGINE COMPUTES\nValidated physics\n\nGUARD AUDITS\nEvidence verdict",24,width=23)
    elif name=="scene4":
        addtext(d,(1584,215),"600 °C\n10% humidity\n10,000 hours",32,True,"#ffe0a5",spacing=22)
        addtext(d,(1584,447),"INSUFFICIENT\nEVIDENCE",32,True,"#ffffff")
        addtext(d,(1584,568),"No executed scientific tool.\n\nNo recommendation.\n\nIndependent guard enforced.",25,width=22)
    elif name=="scene5":
        addtext(d,(1584,215),"FOLLOW THE EVIDENCE",32,True,"#ffffff",width=15)
        addtext(d,(1584,385),"Source DOI\nOriginal rows\nParameters + units\nSelected regimes\nAudit warnings\nCode fingerprint\n\nReal JSON export",25,width=23,spacing=14)
    elif name=="closing":
        d.rectangle((0,96,1920,990),fill="#102930")
        addtext(d,(110,170),"OxyProof",80,True,"#ffffff")
        addtext(d,(115,308),"When the answer changes, explain why.",49,True,"#b5e7d8")
        addtext(d,(115,410),"And show where the evidence stops.",49,True,"#b5e7d8")
        addtext(d,(115,580),"Real scientific data. Bounded AI tools.\nDeterministic physics. Independent evidence auditing.",33,spacing=16)
        addtext(d,(115,755),"Open Scientific Intelligence Hackathon 2026",31,True)
        addtext(d,(115,825),"github.com/miku-wwl/oxyproof-osi-2026",34,True,"#ffffff")
    return im

def caption_at(t):
    return next((s for a,b,s in CUES if a<=t<b),"")
def with_caption(im,value):
    im=im.copy(); d=ImageDraw.Draw(im)
    if value:
        lines=wrap(value)
        assert len(lines)<=2
        y=996 if len(lines)==2 else 1015
        for line in lines:
            f=font(32); width=d.textlength(line,font=f)
            assert width<1830
            d.text(((1920-width)/2,y),line,font=f,fill="#ffffff"); y+=38
    return im

def write_copy():
    # The editable SRT and narration contain exactly the same spoken words.
    previous=0
    for a,b,value in CUES:
        assert previous<=a<b<=215 and len(wrap(value))<=2 and len(value)/(b-a)<20
        previous=b
    (OUT/"video/oxyproof-final.srt").write_text("\n".join(
        f"{i}\n{stamp(a)} --> {stamp(b)}\n"+"\n".join(wrap(s))+"\n"
        for i,(a,b,s) in enumerate(CUES,1)),encoding="utf-8")
    groups=[(0,25,"Problem and research question","Dashboard and Temperature Decision Explorer."),
        (25,85,"The conditional ranking reversal","Curves, actual slider, 700 K / 1000 K rankings, analytic event cards and T* warnings."),
        (85,130,"Real DeepSeek evidence, replayed","Load archive, replay B, show provider/tool, validated arguments, science and audit."),
        (130,170,"Scientific abstention","Replay C; original humidity/lifetime question, model proposal, no executed tool, insufficient evidence."),
        (170,200,"Reproducibility","Original source rows, fit parameters/units, real decision JSON download."),
        (200,215,"Closing","Editorial closing card and verified public GitHub URL.")]
    words=sum(len(s.split()) for _,_,s in CUES)
    md=["# OxyProof narration - final silent edit", "",
        f"Video: 03:35 (215 seconds). {words} spoken words; {words/215*60:.1f} words/minute including pauses.",
        "Owner-recorded voice is pending. No artificial voice or narration audio has been generated.",
        "Speak naturally, leave the indicated pauses, and use the SRT as the cue sheet. Replay is historical execution, never fresh inference.", ""]
    for a,b,title,visual in groups:
        md += [f"## {stamp(a)[:8]} - {stamp(b)[:8]} | {title}", "", f"Visual: {visual}", "",
               " ".join(s for x,y,s in CUES if a<=x<b), ""]
    md += ["## Pronunciation and recording notes", "",
           "- OxyProof: OX-ee-proof. DeepSeek: deep seek. API: A-P-I. JSON: JAY-sun.",
           "- Kelvin has no 'degrees'. Say 'degrees Celsius' for 600 °C.",
           "- Say the root values as approximately seven hundred seventy-six, eight hundred eighteen, and eight hundred fifty-four kelvin.",
           "- The formula is sigma equals A divided by T, times the exponential of minus activation energy over Boltzmann's constant times T.",
           "- Source rows are curated published records, not new experiments. No validated uncertainty bounds exist here.",
           "- A later voice mix should retain this clean master and be checked again for duration, audibility and synchronization.", ""]
    (OUT/"narration/NARRATION_FINAL.md").write_text("\n".join(md),encoding="utf-8")

def render():
    assert FF.is_file() and FP.is_file()
    WORK.mkdir(parents=True,exist_ok=True)
    clean_dir=WORK/"clean-frames"; sub_dir=WORK/"subtitled-frames"
    clean_dir.mkdir(exist_ok=True); sub_dir.mkdir(exist_ok=True)
    entries={"clean":[],"subtitled":[]}; sources=[]; offset=0.; cache={}; subcache={}
    for name,duration,section,title in SCENES:
        if name=="closing":
            frames=[{"t":0,"sha256":"closing","file":None}]; manifest=None
        else:
            manifest_path=RAW/TAKE_NAMES.get(name,name)/"capture-manifest.json"
            manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
            assert manifest["source_browser"]=="Codex In-app Browser"
            assert manifest["status"]=="CAPTURED_UNVERIFIED" and not manifest.get("error")
            assert manifest["duration_seconds"]>=duration
            frames=[f for f in manifest["frames"] if f["t"]<duration]
            assert all(b["t"]>a["t"] for a,b in zip(frames,frames[1:]))
            for f in frames:
                p=(manifest_path.parent/f["file"]).resolve()
                assert p.is_relative_to(manifest_path.parent)
                assert sha(p)==f["sha256"]
            dimensions=set()
            for f in frames:
                with Image.open(manifest_path.parent/f["file"]) as pic: dimensions.add(pic.size)
            sources.append({"scene":name,"manifest":str(manifest_path.relative_to(ROOT)),
                "manifest_sha256":sha(manifest_path),"source_dimensions":sorted(dimensions),
                "capture_average_fps":manifest["average_acquisition_fps"],
                "max_capture_gap_seconds":manifest["max_inter_sample_gap_seconds"],
                "captured_seconds":manifest["duration_seconds"],"edit_range_seconds":[0,duration],
                "playback_speed":1,"source_frames":len(frames),
                "distinct_images":len(set(f["sha256"] for f in frames)),"events":manifest["events"]})
        times=[0]+[f["t"] for f in frames[1:]]
        cuts=sorted(set(times+[duration]+[t-offset for a,b,s in CUES for t in (a,b) if offset<t<offset+duration]))
        for a,b in zip(cuts,cuts[1:]):
            idx=bisect.bisect_right(times,a)-1; f=frames[idx]
            key=(name,f["sha256"])
            if key not in cache:
                source=Image.open(RAW/TAKE_NAMES.get(name,name)/f["file"]) if f["file"] else None
                canvas=editorial(source,name,section,title)
                if source: source.close()
                file=clean_dir/f"frame-{len(cache):05}.jpg"; canvas.save(file,quality=97,subsampling=0)
                cache[key]=file
            file=cache[key]; entries["clean"].append((file,b-a))
            cap=caption_at(offset+(a+b)/2); skey=(str(file),cap)
            if skey not in subcache:
                file2=sub_dir/f"frame-{len(subcache):05}.jpg"
                with Image.open(file) as img: with_caption(img,cap).save(file2,quality=97,subsampling=0)
                subcache[skey]=file2
            entries["subtitled"].append((subcache[skey],b-a))
        offset+=duration
        print(f"COMPOSED {name} duration={duration}",flush=True)
    assert offset==215
    (OUT/"review/capture-and-edit-provenance.json").write_text(json.dumps({
        "method":"Actual installed skill capture_iab.mjs; preflight encoded/decoded with render_iab.py; this script composes timestamped source frames with editorial labels and SRT-matched captions",
        "skill_path":"C:/Users/weila/.codex/skills/codex-iab-video-recording/SKILL.md",
        "requested_skill_identified":True,"installed_skill_name":"codex-iab-video-recording",
        "installed_display_name":"IAB Browser Video",
        "identity_source":"C:/Users/weila/.codex/skills/codex-iab-video-recording/agents/openai.yaml",
        "source_browser":{"name":"ChatGPT in-app browser","type":"iab","id":"2","tab_id":"1"},
        "sources":sources,"total_duration_seconds":offset,"export_fps":30,
        "native_1080p30_claimed":False,"system_cursor_captured":False,
        "editing":"Each take trimmed to whole-second duration, 1x speed. Entire viewport aspect-fitted at 1536x864. Editorial header/side rail and 15-second closing card; no UI reconstruction or invented cursor. No music/audio.",
        "old_video_reused":False,"old_video_reason":"1440x1000 source includes baked captions incompatible with requested clean master; inspected and preserved",
        "new_provider_calls":0,"replay_source":"artifacts/deepseek_live_acceptance.json",
        "replay_sha256":sha(ROOT/"artifacts/deepseek_live_acceptance.json"),
        "budget_ledger_sha256":sha(ROOT/".local/deepseek-phase262-budget.json"),
    },indent=2)+"\n",encoding="utf-8")
    for variant,items in entries.items():
        if "--subtitles-only" in sys.argv and variant=="clean":
            continue
        concat=WORK/f"{variant}.ffconcat"; lines=["ffconcat version 1.0"]
        for file,gap in items:
            lines += [f"file '{file.as_posix()}'","option framerate 1000",f"duration {gap:.9f}"]
        lines += [f"file '{items[-1][0].as_posix()}'","option framerate 1000"]
        concat.write_text("\n".join(lines)+"\n",encoding="utf-8")
        dest=OUT/f"video/oxyproof-final-{variant}.mp4"
        subprocess.run([str(FF),"-v","error","-n","-f","concat","-safe","0","-i",str(concat),
            "-vf","scale=in_range=pc:out_range=tv,format=yuv420p","-frames:v","6450","-r","30",
            "-fps_mode","cfr","-an","-c:v","libx264","-preset","veryfast","-crf","18",
            "-pix_fmt","yuv420p","-color_range","tv","-threads","4","-movflags","+faststart",str(dest)],check=True)
        print(f"RENDERED {dest.name}",flush=True)

if __name__=="__main__":
    write_copy(); render()
