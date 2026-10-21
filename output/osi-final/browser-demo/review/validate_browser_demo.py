"""Verify the video-only revision against real downloads and preserved evidence.

This does not call the application, an LLM, or any external service.
"""
import hashlib
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
BIN = ROOT / '.local/media-tools/ffmpeg-essentials/ffmpeg-9.0.2-essentials_build/bin'

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
    result=subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f'Command failed ({result.returncode}): {result.stderr}')
    return result.stdout

def main():
    proof = read(OUT/'review/recording-provenance.json')
    checks = []
    media = []
    for variant in ('clean', 'subtitled'):
        p = OUT/f'oxyproof-browser-demo-{variant}.mp4'
        meta = json.loads(run([BIN/'ffprobe.exe','-v','error','-show_streams','-show_format','-of','json',p]))
        streams = meta['streams']; assert len(streams) == 1
        s = streams[0]
        assert (s['codec_name'],s['width'],s['height'],s['pix_fmt'],s['r_frame_rate']) == ('h264',1920,1080,'yuv420p','30/1')
        assert s['color_range'] == 'tv' and int(s['nb_frames']) == 5850
        assert abs(float(meta['format']['duration'])-195) < .001
        run([BIN/'ffmpeg.exe','-v','error','-threads','2','-xerror','-i',p,'-f','null','-'])
        media.append({'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'duration_s':float(meta['format']['duration']),
                      'dimensions':[s['width'],s['height']],'codec':s['codec_name'],'pixel_format':s['pix_fmt'],
                      'fps':s['r_frame_rate'],'frames':int(s['nb_frames']),'audio_streams':0,'full_decode':'PASS'})
        print('MEDIA_PASS',p.name,flush=True)
    checks.append('Both files: 195 seconds, H.264, 1920x1080, 30 fps, 5850 frames, no audio, complete decode')
    text = (OUT/'oxyproof-browser-demo.srt').read_text(encoding='utf-8').strip()
    cues = text.split('\n\n'); assert len(cues) == 25
    last = 0
    def seconds(s):
        h,m,s,ms = map(int,re.split('[:,]',s)); return h*3600+m*60+s+ms/1000
    for i,cue in enumerate(cues,1):
        lines=cue.splitlines(); assert int(lines[0]) == i and 1<=len(lines[2:])<=2
        a,b=map(seconds,lines[1].split(' --> ')); assert last<=a<b<=195
        assert max(map(len,lines[2:]))<=50 and len(' '.join(lines[2:]))/(b-a)<20
        last=b
    checks.append('25 ordered minimal-English subtitle cues: at most two lines, 50 characters per line, under 20 characters/second')
    preserved = read(OUT/'review/protected-before.json')
    assert all(sha(ROOT/p)==digest for p,digest in preserved.items())
    checks.append(f'{len(preserved)} protected old media, PDF, submission copy, replay archives and budget-ledger hashes unchanged')
    download = read(OUT/'review/browser-export-proof.json')
    exported = OUT/'review/exported-decision.json'
    assert sha(exported)==download['sha256']==sha(Path(download['downloaded_file']))
    assert exported.stat().st_size==download['bytes']==141505
    d = read(exported); ref=read(ROOT/'artifacts/scientific_acceptance.json')
    assert d['source']['dataset_sha256']==ref['dataset_sha256']=='8ec66b131bae79f8520f7cf40e91e2be2541995939bc43b744eaac627f4fad34'
    assert d['validated_arguments']['row_ids']==[1,2,3]
    assert [d['validated_arguments'][k] for k in ('temperature_min_k','temperature_max_k')]==[700,1000]
    assert d['runtime_mode']=='OFFLINE_DETERMINISTIC'
    assert d['units']=={'temperature':'K','conductivity':'S/cm','activation_energy':'meV','prefactor':'K S/cm'}
    assert [v['ordering'] for v in d['selected_rankings']]==[[1,2,3],[3,2,1]]
    for endpoint in ref['endpoints']:
        ranking=next(v for v in d['selected_rankings'] if v['temperature_k']==endpoint['temperature_k'])
        value=next(v['conductivity_s_cm'] for v in ranking['values'] if v['row_id']==endpoint['row_id'])
        assert math.isclose(value,float(endpoint['sigma_s_cm_decimal']),rel_tol=1e-12)
    roots=d['execution_trace']['scientific_result']['continuous_crossings_k']
    assert all(math.isclose(a,b['production_root_k'],abs_tol=1e-9) for a,b in zip(roots,ref['roots'],strict=True))
    checks.append('Actual downloaded JSON and preview byte-identical; rows, units, orders, six conductivity values and three analytical roots match the saved independent decimal reference')
    sources=[]
    for take in proof['takes']:
        mpath=ROOT/take['manifest']; assert sha(mpath)==take['manifest_sha256']
        m=read(mpath); cut=take['source_range_s'][1]
        assert m['started_steps']==m['scheduled_steps'] and not m.get('error')
        assert all(not e.get('failed') and e['completed_t']<cut for e in m['events'] if e['kind']=='ui-step')
        assert not m['ui_operation_outside_capture_cut']
        sources.append({'take':take['take'],'capture_average_fps':take['capture_average_fps'],
                        'max_sample_gap_s':take['max_sample_gap_s'],'frames_used':take['source_frames_used']})
    checks.append('Eight accepted source takes: scheduled actions completed within cuts, manifest hashes valid, playback speed 1x')
    # Extract actual decoded final frames, rather than using source frames for visual QA.
    moments=[2,8,16,20,24,29,33,42,49,54,64,71,80,86,91,94,100,105,111,116,122,128,132,137,141,148,156,162,169,173,178,184,189,193,194.5]
    qa=OUT/'review/screenshots';qa.mkdir(exist_ok=True)
    # One decoder process bounds process/thread overhead on the owner's busy Windows host.
    select='+'.join(f'eq(n,{round(t*30)})' for t in moments)
    run([BIN/'ffmpeg.exe','-v','error','-y','-threads','2','-filter_threads','1',
         '-i',OUT/'oxyproof-browser-demo-subtitled.mp4','-vf',f"select='{select}'",
         '-fps_mode','vfr','-frames:v',len(moments),'-threads','2','-q:v','2',qa/'decoded-%02d.jpg'])
    contact=Image.new('RGB',(1920,9*298),'#111418');draw=ImageDraw.Draw(contact)
    for i,t in enumerate(moments):
        p=qa/f'frame-{t:05.1f}s.jpg'
        p.write_bytes((qa/f'decoded-{i+1:02}.jpg').read_bytes())
        with Image.open(p) as im:thumb=im.resize((480,270),Image.Resampling.LANCZOS)
        x=(i%4)*480;y=(i//4)*298;contact.paste(thumb,(x,y));draw.text((x+8,y+274),f'{t:05.1f} s',fill='white')
    contact.save(qa/'contact-sheet.jpg',quality=94)
    result={'status':'PASS','scope':'Video-only technical/evidence checks; visual/manual and browser playback evidence reported separately',
            'verified_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'media':media,'source_takes':sources,
            'export_sha256':sha(exported),'scientific_reference':'artifacts/scientific_acceptance.json',
            'system_cursor':'UNAVAILABLE','full_user_request_acceptance':'PARTIAL',
            'visual_qa_images':len(moments),'protected_files_unchanged':len(preserved)}
    (OUT/'review/verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__': main()
