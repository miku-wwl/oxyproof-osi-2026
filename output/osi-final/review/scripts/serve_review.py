"""Loopback-only finished-media review server with HTTP byte ranges; no app/model access."""
import argparse
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_head(self):
        self.byte_range=None
        path=Path(self.translate_path(self.path))
        if not path.is_file() or not self.headers.get("Range"):
            return super().send_head()
        size=path.stat().st_size
        match=re.fullmatch(r"bytes=(\d*)-(\d*)",self.headers["Range"])
        if not match or not any(match.groups()):
            self.send_error(416); return None
        first,last=match.groups()
        start=int(first) if first else max(0,size-int(last))
        end=min(int(last),size-1) if first and last else size-1
        if start>=size or end<start:
            self.send_response(416); self.send_header("Content-Range",f"bytes */{size}"); self.end_headers(); return None
        file=path.open("rb"); file.seek(start); self.byte_range=(start,end)
        self.send_response(206)
        self.send_header("Content-Type",self.guess_type(str(path)))
        self.send_header("Accept-Ranges","bytes")
        self.send_header("Content-Range",f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length",str(end-start+1))
        self.end_headers(); return file
    def end_headers(self):
        if self.path.endswith(".mp4") and not self.headers.get("Range"):
            self.send_header("Accept-Ranges","bytes")
        super().end_headers()
    def copyfile(self,source,outputfile):
        if self.byte_range is None: return super().copyfile(source,outputfile)
        remaining=self.byte_range[1]-self.byte_range[0]+1
        while remaining>0:
            block=source.read(min(1024*1024,remaining))
            if not block: break
            outputfile.write(block); remaining-=len(block)

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--port",type=int,default=8017); args=p.parse_args()
    print(f"Review only: http://127.0.0.1:{args.port}/review/REVIEW.html",flush=True)
    ThreadingHTTPServer(("127.0.0.1",args.port),Handler).serve_forever()
