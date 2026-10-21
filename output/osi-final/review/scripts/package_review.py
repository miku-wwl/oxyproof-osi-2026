"""Package only explicit production payload types; verify CRC, paths and every hash."""
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

OUT=Path(__file__).resolve().parents[2]
ZIP=OUT/"oxyproof-final-review-package.zip"
REPORT=OUT/"review/package-verification.json"
SUMS=OUT/"SHA256SUMS.txt"
allow={".mp4",".srt",".md",".pdf",".json",".png",".jpg",".svg",".csv",".py",".html",".txt"}
required=["video/oxyproof-final-clean.mp4","video/oxyproof-final-subtitled.mp4","video/oxyproof-final.srt",
          "narration/NARRATION_FINAL.md","submission/oxyproof-one-page-final.pdf","submission/SUBMISSION_FINAL.md",
          "submission/SOCIAL_POST_FINAL.md","review/VIDEO_ACCEPTANCE.md","review/SCIENTIFIC_CLAIMS_REVIEW.md",
          "review/SUBMISSION_CHECKLIST.md","review/PRODUCTION_HANDOVER.md","review/browser-playback.json"]
assert all((OUT/p).is_file() and (OUT/p).stat().st_size>0 for p in required)
assert not ZIP.exists(), "Preserve the prior ZIP before rebuilding."
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(p for p in OUT.rglob("*") if p.is_file() and p.suffix.lower() in allow and p not in (REPORT,SUMS))
for p in files:
    rel=p.relative_to(OUT)
    assert not any(part in {".env","node_modules",".venv","__pycache__",".local"} for part in rel.parts)
    if p.suffix in {".md",".json",".py",".html",".txt",".csv",".svg",".srt"}:
        body=p.read_text(encoding="utf-8")
        assert not re.search(r"\bsk-[A-Za-z0-9_-]{20,}\b",body), f"Secret-like credential: {rel}"
        assert not re.search(r"(?i)authorization\s*[:=]\s*[\"']?bearer\s+[A-Za-z0-9_.-]{20,}",body)
SUMS.write_text("".join(f"{sha(p)}  {p.relative_to(OUT).as_posix()}\n" for p in files),encoding="utf-8")
files.append(SUMS)
with zipfile.ZipFile(ZIP,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files: z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(ZIP) as z:
    names=z.namelist()
    assert len(names)==len(set(names))==len(files)
    assert z.testzip() is None
    for p in files:
        name=p.relative_to(OUT).as_posix(); path=PurePosixPath(name)
        assert not path.is_absolute() and ".." not in path.parts and "\\" not in name
        assert hashlib.sha256(z.read(name)).hexdigest()==sha(p)
checksum=sha(ZIP)
ZIP.with_suffix(".zip.sha256").write_text(f"{checksum}  {ZIP.name}\n",encoding="utf-8")
result={"status":"PASS","zip":ZIP.name,"sha256":checksum,"bytes":ZIP.stat().st_size,"entries":len(files),
        "crc":"PASS","paths":"PASS","duplicates":0,"entry_hashes":"PASS","credential_pattern_scan":"PASS",
        "excluded":"Raw captures, source browser state, environments, tools, full CSV, pycache, ZIP sidecar and this post-build report",
        "files":[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in files]}
REPORT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k!="files"},indent=2))
