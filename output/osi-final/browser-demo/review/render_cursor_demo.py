"""Add sparse evidence-grounded annotations to accepted MP4s, without browser calls.

Pointers identify logged call targets/endpoints, never a measured system cursor.
Where pre-click geometry moved or is absent, use a labeled control highlight.
"""
import argparse
import bisect
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
REVIEW=OUT/'review/cursor'
WORK=ROOT/'.local/cursor-overlay'
BIN=ROOT/'.local/media-tools/ffmpeg-essentials/ffmpeg-9.0.2-essentials_build/bin'
FPS=30;FRAMES=5850;SIZE=(1920,1080)

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
    p=subprocess.run([str(a) for a in args],capture_output=True,text=True)
    if p.returncode:raise RuntimeError(f'{p.returncode}: {p.stderr}')
    return p.stdout
def source_frame(take,t):
    folder=ROOT/'.local/browser-demo-capture'/take;m=read(folder/'capture-manifest.json')
    f=m['frames'][max(0,bisect.bisect_right([f['t'] for f in m['frames']],t)-1)]
    path=folder/f['file'];assert sha(path)==f['sha256']
    with Image.open(path) as im:canvas=ImageOps.fit(im.crop((0,0,1749,984)),SIZE,Image.Resampling.LANCZOS)
    return canvas,{'file':str(path.relative_to(ROOT)),'t':f['t'],'sha256':f['sha256']}

def prepare():
    REVIEW.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    p=read(OUT/'review/recording-provenance.json')
    assert p['source_screenshot_dimensions']==[1921,1081] and p['source_padding_crop']==[0,0,1749,984]
    assert p['export_dimensions']==[1920,1080] and p['duration_s']==195
    takes={t['take']:t for t in p['takes']};manifests={}
    for name,t in takes.items():
        mpath=ROOT/t['manifest'];assert sha(mpath)==t['manifest_sha256']
        m=read(mpath);assert m['viewport_css_pixels']['width']==1934 and m['viewport_css_pixels']['height']==1088
        manifests[name]=m
    protected=[OUT/f for f in ('oxyproof-browser-demo-clean.mp4','oxyproof-browser-demo-subtitled.mp4',
               'oxyproof-browser-demo.srt','BROWSER_DEMO_NARRATION.md','BROWSER_DEMO_ACCEPTANCE.md',
               'review/recording-provenance.json','review/slider-operation-proof.json','review/exported-decision.json')]
    protected += [ROOT/x for x in read(OUT/'review/protected-before.json')]
    protected += [ROOT/'AGENTS.md',ROOT/'pyproject.toml',ROOT/'uv.lock',ROOT/'frontend/package-lock.json']
    write(REVIEW/'protected-before.json',{str(x.relative_to(ROOT)):sha(x) for x in dict.fromkeys(protected)})
    # CSS viewport occupies the recorded content rectangle. Validate every mapped target
    # on the preserved frame; do NOT multiply coordinates by DPR a second time.
    # ImageOps.fit uses a common scale and a centered 0.1875px vertical source trim.
    scale=1920/1749
    fit_y_trim=(984-1080/scale)/2
    def mapped(point):
        raw=(point['x']*1749/point['width'],point['y']*984/point['height'])
        return [raw[0]*scale,(raw[1]-fit_y_trim)*scale]
    def event(take,label):return next(e for e in manifests[take]['events'] if e['label']==label)
    annotations=[]
    def add(take,label,kind,start,end,rect,reason='',text=None):
        e=event(take,label);offset=takes[take]['video_interval_s'][0]
        pt=e.get('point');a={'id':f'{take}:{label}','take':take,'label':label,'kind':kind,
            'logged_kind':e['kind'],'call_interval_s':[offset+e['requested_t'],offset+e['completed_t']],
            'video_interval_s':[start,end],'target_rect_output_px':rect,'source_point':pt,
            'output_point':mapped(pt) if pt and kind=='logged_target' else None,
            'label_text':text or ('Logged target' if kind=='logged_target' else f'Control highlight · {label}'),
            'reason':reason,'native_cursor_claim':False,'click_ring_duration_s':.4 if kind=='logged_target' else 0}
        if a['output_point']:
            x,y=a['output_point'];l,t,r,b=rect;assert l<=x<=r and t<=y<=b,a
        assert start<end and offset+e['requested_t']<=start<=offset+e['completed_t']
        annotations.append(a)
    add('A1','source-selector','logged_target',4.05,4.94,[344,521,1818,560])
    add('A1','select-published-Huang-group','control_highlight',6.08,6.85,[344,521,1818,560],
        'selectOption has no pointer event/coordinates; highlight the verified selected control', 'Control highlight · source selected')
    add('A2','row-1','control_highlight',15.22,15.90,[346,528,667,551],
        'Logged pre-scroll center maps to row 2 after automatic scrolling; omit pointer','Control highlight · row 1')
    add('A2','row-2','control_highlight',17.13,17.83,[346,557,667,578],
        'Pre-scroll center becomes stale after this click too; track the actual row label instead of drawing a pointer','Control highlight · row 2')
    add('A2','row-3','control_highlight',19.22,19.78,[346,528,667,551],
        'Logged pre-scroll center maps to row 4 after automatic scrolling; omit pointer','Control highlight · row 3')
    add('A2','analyze-interval','logged_target',28.14,28.90,[1238,517,1818,560])
    proof=read(OUT/'review/slider-operation-proof.json')
    for i,(label,op) in enumerate(zip(['actual-slider-drag-first-step','actual-slider-drag-second-step','actual-slider-drag-to-1000K'],proof['recorded_operations'],strict=True)):
        e=event('B',label);a=35+e['requested_t'];z=35+e['completed_t']
        ends=[mapped({'x':x,'y':y,'width':1934,'height':1088}) for x,y in (op['from'],op['to'])]
        assert op['before']!=op['after']
        assert all(365<=x<=1798 and 478<=y<=499 for x,y in ends)
        annotations.append({'id':f'B:drag-{i+1}','take':'B','label':label,'kind':'drag_endpoints',
            'call_interval_s':[a,z],'video_interval_s':[a,z+.4], 'source_from_css':op['from'],'source_to_css':op['to'],
            'output_endpoints':ends,'target_rect_output_px':[364,476,1799,501],
            'before_index':op['before'],'after_index':op['after'],
            'label_text':'Logged drag endpoints · no measured pointer path',
            'native_cursor_claim':False,'intermediate_pointer_samples':0,'connecting_trajectory_added':False,
            'reason':'Two recorded endpoints only; display separate endpoint pointers with a gap, without inventing an intervening pointer trajectory'})
    add('C','Replay-B','control_highlight',108.28,109.02,[422,521,495,559],
        'Point null: locator auto-scrolls into view; use visible Replay B control','Control highlight · Replay B')
    add('D','Replay-C','control_highlight',136.25,136.98,[500,521,574,559],
        'Pre-scroll point at bottom edge is invalid after auto-scroll and overlaps existing subtitles; omit pointer','Control highlight · Replay C')
    add('E','Export-JSON','control_highlight',177.25,178.08,[1653,520,1800,561],
        'Point null: control becomes visible after locator auto-scroll; use actual export control','Control highlight · Export JSON')
    for a in annotations:
        assert 0<=a['video_interval_s'][0]<a['video_interval_s'][1]<195
        for key in ('call_interval_s','video_interval_s'):a[key]=[round(x,9) for x in a[key]]
    plan={'method':'Sparse annotated reconstruction from genuine IAB input-call logs, with visual fail-closed target validation',
        'native_system_cursor_capture':False,'new_browser_actions':0,'new_model_calls':0,
        'accepted_timeline_s':195,'fps':FPS,'frames':FRAMES,
        'source_capture_px':[1921,1081],'css_viewport_px':[1934,1088],
        'recorded_dpr':manifests['A1']['viewport_css_pixels']['pixelRatio'],
        'content_rect_source_px':[0,0,1749,984],
        'css_to_source_scale':[1749/1934,984/1088],
        'registration_qualification':'Content-rectangle registration checked on preserved controls, not independently measured native pointer pixels; stale/missing point targets fail closed to labeled highlights',
        'imageops_fit_scale':scale,'imageops_fit_source_vertical_trim_each_edge_px':fit_y_trim,
        'mapping':'raw_x=css_x*1749/1934; raw_y=css_y*984/1088; out_x=raw_x*1920/1749; out_y=(raw_y-0.09375)*1920/1749',
        'input_time_qualification':'IAB method request/completion windows, not measured OS down/up timestamps. Click rings start at logged-call cue time; no sub-frame precision is claimed.',
        'annotations':annotations}
    track_controls(plan,takes,manifests)
    write(REVIEW/'annotation-plan.json',plan)
    # Visually review before/after frames at the actual cut-relative times.
    pairs=[('A2',3.2,3.8,'row-1'),('A2',5.2,5.8,'row-2'),('A2',7.2,7.8,'row-3'),
           ('A2',16.05,17.3,'analyze-interval'),('B',12,13.6,'drag-1'),('B',17,18.6,'drag-2'),('B',22,23.6,'drag-3'),
           ('C',13.1,14.1,'Replay-B'),('D',1.02,2.1,'Replay-C'),('E',12.1,13.2,'Export-JSON')]
    records=[]
    for take,a,b,label in pairs:
        frames=[]
        for phase,t in [('before',a),('after',b)]:
            im,record=source_frame(take,t);im.save(REVIEW/f'{label}-{phase}.jpg',quality=96)
            record['phase']=phase;frames.append(record)
        records.append({'action':label,'take':take,'frames':frames})
    write(REVIEW/'source-state-evidence.json',records)
    make_overlay(plan)
    print('PREPARED',len(annotations),'annotations; no browser/model calls',flush=True)

def track_controls(plan,takes,manifests):
    # Track the visible CONTROL, never a missing pointer. Templates are actual
    # preserved text pixels; only vertical page reflow/scroll is permitted.
    refs={'row-1':('A2',3.2,[373,532,417,547]),
          'row-2':('A2',5.2,[373,560,417,574]),
          'row-3':('A2',7.2,[373,532,417,547]),
          'Replay-B':('C',13.3,[434,532,484,548]),
          'Replay-C':('D',1.3,[510,532,560,548]),
          'Export-JSON':('E',12.3,[1678,532,1789,548])}
    # Selected/hovered controls change text tone. Use verified before AND after
    # pixels so a faded selected "Row 2" cannot be confused with unchecked Row 3.
    after_refs={'row-1':(3.8,532),'row-2':(5.8,533),'row-3':(7.8,532),
                'Replay-B':(14.1,657),'Replay-C':(2.1,274),'Export-JSON':(13.2,532)}
    matches=[]
    for a in plan['annotations']:
        if a['label'] not in refs:continue
        take,ref_t,box=refs[a['label']];ref,record=source_frame(take,ref_t)
        template=ref.convert('L').crop(box);x0,y0,x1,y1=box;height=y1-y0
        after_t,after_y=after_refs[a['label']];after,after_record=source_frame(take,after_t)
        templates=[template,after.convert('L').crop((x0,after_y,x1,after_y+height))]
        score_limit=8 if a['label'].startswith('row-') else 16
        a['control_tracking']={'method':'Vertical template registration of actual control-label pixels; not pointer tracking',
            'reference_frame':record,'template_box_output_px':box,'score':'mean absolute grayscale pixel difference',
            'after_reference_frame':after_record,'after_template_box_output_px':[x0,after_y,x1,after_y+height],
            'maximum_allowed_score':score_limit,'rect_by_output_frame':{}}
        cache={};m=manifests[take];ts=[f['t'] for f in m['frames']];offset=takes[take]['video_interval_s'][0]
        for n in range(math.ceil(a['video_interval_s'][0]*FPS),math.ceil(a['video_interval_s'][1]*FPS)):
            t=n/FPS-offset;f=m['frames'][max(0,bisect.bisect_right(ts,t)-1)]
            if f['sha256'] not in cache:
                im,_=source_frame(take,t);gray=im.convert('L');scores=[]
                for y in range(120,970-height):
                    crop=gray.crop((x0,y,x1,y+height))
                    score=min(ImageStat.Stat(ImageChops.difference(tmpl,crop)).mean[0] for tmpl in templates)
                    scores.append((score,y))
                score,y=min(scores);assert score<score_limit,(a['id'],n,score,y)
                alternate=min(s for s,yy in scores if abs(yy-y)>height+4)
                assert alternate-score>.3,(a['id'],n,'ambiguous control registration',score,alternate)
                rect=a['target_rect_output_px'].copy();rect[1]+=y-y0;rect[3]+=y-y0
                assert 0<rect[1]<rect[3]<996
                cache[f['sha256']]=rect
                matches.append({'action':a['id'],'source_frame':f['file'],'source_sha256':f['sha256'],
                    'output_frame':n,'matched_text_top_y':y,'mean_absolute_difference':score,
                    'alternate_location_score':alternate,'target_rect':rect})
            a['control_tracking']['rect_by_output_frame'][str(n)]=cache[f['sha256']]
        print('CONTROL_TRACKED',a['id'],len(cache),'distinct original states',flush=True)
    write(REVIEW/'control-registration.json',matches)

def make_overlay(plan):
    blank=WORK/'transparent.png';Image.new('RGBA',SIZE,(0,0,0,0)).save(blank)
    items=[];unique=0;active_frames=[]
    for n in range(FRAMES):
        t=n/FPS;live=[a for a in plan['annotations'] if a['video_interval_s'][0]<=t<a['video_interval_s'][1]]
        intro=.4<=t<3.0
        if live or intro:
            file=WORK/f'overlay-{n:04d}.png'
            # Resuming this preparation is safe: PNGs are deterministic for identical
            # active annotation records and drawing revision. Validate on reuse.
            signature=hashlib.sha256(json.dumps({'drawing_revision':1,'t':t,'live':live,'intro':intro},sort_keys=True).encode()).hexdigest()
            signature_file=file.with_suffix('.sha256')
            if not file.exists() or not signature_file.exists() or signature_file.read_text()!=signature:
                im=draw_overlay(t,live,intro);im.save(file,compress_level=1)
                signature_file.write_text(signature,encoding='ascii')
            unique+=1;active_frames.append(n)
        else:file=blank
        if items and file==items[-1][0]:items[-1]=(file,items[-1][1]+1)
        else:items.append((file,1))
    text=['ffconcat version 1.0']
    for path,count in items:text.extend([f"file '{path.as_posix()}'",'option framerate 30',f'duration {count/FPS:.12f}'])
    text.extend([f"file '{blank.as_posix()}'",'option framerate 30'])
    (WORK/'overlay.ffconcat').write_text('\n'.join(text)+'\n',encoding='utf-8')
    write(REVIEW/'overlay-schedule.json',{'active_frames':active_frames,'nonempty_frames':unique,
        'blank_frames':FRAMES-unique,'duration_s':195,'continuous_pointer_trace':False})

def draw_overlay(t,live,intro=False):
    scale=2;im=Image.new('RGBA',(3840,2160),(0,0,0,0));d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',36)
    def rect(box,alpha=210):
        box=[round(v*scale) for v in box]
        d.rounded_rectangle(box,radius=8,outline=(17,42,51,alpha),width=7)
        d.rounded_rectangle(box,radius=8,outline=(52,170,170,alpha),width=3)
    def tag(text,x,y):
        w=d.textlength(text,font=font)+20
        d.rounded_rectangle((x*2,y*2,x*2+w,y*2+48),radius=7,fill=(19,44,53,232))
        d.text((x*2+10,y*2+1),text,font=font,fill=(255,255,255,255))
    def cursor(p):
        x,y=p;pts=[(x+dx,y+dy) for dx,dy in [(0,0),(0,22),(6,17),(10,27),(14,25),(10,15),(18,15)]]
        d.polygon([(round(x*2),round(y*2)) for x,y in pts],fill='white',outline=(18,27,31,255),width=4)
    if intro:
        tag('Indicators reconstructed from IAB logs',1450,18)
        tag('Not native mouse capture',1450,45)
    for a in live:
        rect_now=a.get('control_tracking',{}).get('rect_by_output_frame',{}).get(str(round(t*FPS)),a['target_rect_output_px'])
        l,y,r,b=rect_now;start,end=a['video_interval_s']
        if a['kind']=='drag_endpoints':
            p,q=a['output_endpoints'];call_end=a['call_interval_s'][1]
            # No moving/interpolated arrow: only separately displayed logged endpoints.
            for x0,y0 in [p,q]:d.ellipse(((x0-5)*2,(y0-5)*2,(x0+5)*2,(y0+5)*2),outline=(35,136,148,180),width=3)
            if t<start+.27:cursor(p)
            elif t>=call_end-.33:cursor(q)
            tag(a['label_text'],1050,511)
        else:
            rect([l-3,y-3,r+3,b+3],alpha=160)
            if a['kind']=='logged_target':
                p=a['output_point'];cursor(p)
                dt=t-start
                if 0<=dt<.4:
                    rad=11+9*dt/.4;alpha=round(210*(1-dt/.4))
                    x0,y0=p;d.ellipse(((x0-rad)*2,(y0-rad)*2,(x0+rad)*2,(y0+rad)*2),outline=(12,101,124,alpha),width=5)
                if a['label']=='row-2':tag('Logged target · row 2',705,556)
                elif a['label']=='analyze-interval':tag('Logged target · Analyze',1460,480)
                else:tag('Logged target · source group',1450,488)
            else:
                if a['label'].startswith('row-'):tag(a['label_text'],705,y-1)
                elif a['label'] in ('Replay-B','Replay-C'):tag(a['label_text'],600,(y+b)/2-12)
                elif a['label']=='Export-JSON':tag(a['label_text'],1460,b+18)
                elif a['label']=='record-selector':tag(a['label_text'],1100,643)
                else:tag(a['label_text'],1450,488)
    return im.resize(SIZE,Image.Resampling.LANCZOS)

def render():
    # Bounded frame streaming avoids sparse-image demux/filter memory growth on
    # the owner's busy Windows host. One original frame in -> one output frame.
    schedule=read(REVIEW/'overlay-schedule.json');active=set(schedule['active_frames'])
    for variant in ('clean','subtitled'):
        src=OUT/f'oxyproof-browser-demo-{variant}.mp4';dest=OUT/f'oxyproof-browser-demo-cursor-{variant}.mp4'
        assert not dest.exists(),f'Refuse to overwrite {dest}'
        encoded=WORK/f'encoded-rgb-{variant}.mp4'
        assert not encoded.exists(),f'Refuse to overwrite private encoded intermediate {encoded}'
        with (WORK/f'{variant}-decode.log').open('wb') as de, (WORK/f'{variant}-encode.log').open('wb') as en:
            dec=subprocess.Popen([str(x) for x in [BIN/'ffmpeg.exe','-v','error','-threads','1','-i',src,
                '-map','0:v:0','-an','-filter_threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1']],stdout=subprocess.PIPE,stderr=de)
            enc=subprocess.Popen([str(x) for x in [BIN/'ffmpeg.exe','-v','error','-n','-f','rawvideo','-pixel_format','rgb24',
                '-video_size','1920x1080','-framerate',FPS,'-i','pipe:0','-filter_threads','1',
                '-vf','scale=in_range=pc:out_range=tv,format=yuv420p','-an','-frames:v',FRAMES,
                '-c:v','libx264','-preset','veryfast','-crf','14','-threads','1','-pix_fmt','yuv420p',
                '-color_range','tv','-movflags','+faststart',encoded]],stdin=subprocess.PIPE,stderr=en)
            try:
                frame_bytes=SIZE[0]*SIZE[1]*3
                for n in range(FRAMES):
                    raw=dec.stdout.read(frame_bytes)
                    assert len(raw)==frame_bytes,f'Truncated original frame {n}'
                    if n in active:
                        im=Image.frombytes('RGB',SIZE,raw)
                        with Image.open(WORK/f'overlay-{n:04d}.png') as ann:im.paste(ann,(0,0),ann)
                        raw=im.tobytes()
                    enc.stdin.write(raw)
                    if n%900==0:print('STREAMING',variant,n,'/',FRAMES,flush=True)
                assert not dec.stdout.read(1),'Unexpected extra original video frames'
                dec.stdout.close();enc.stdin.close()
                assert dec.wait()==0 and enc.wait()==0,'See private bounded-pipeline decoder/encoder logs'
            finally:
                for child in (dec,enc):
                    if child.poll() is None:child.kill();child.wait()
        # Declare the already-converted limited range explicitly in H.264 VUI.
        # Stream copy changes metadata only; no extra image encoding or retiming.
        run([BIN/'ffmpeg.exe','-v','error','-n','-i',encoded,'-map','0:v:0','-c:v','copy',
             '-bsf:v','h264_metadata=video_full_range_flag=0','-an','-movflags','+faststart',dest])
        print('RENDERED',dest.name,flush=True)

def verify():
    p=read(REVIEW/'annotation-plan.json');protected=read(REVIEW/'protected-before.json')
    assert all(sha(ROOT/path)==digest for path,digest in protected.items())
    schedule=read(REVIEW/'overlay-schedule.json');assets=[];max_covered=0
    assert round(9.5*FPS) not in schedule['active_frames'],'Rejected disclosure annotation must be absent'
    for n in schedule['active_frames']:
        path=WORK/f'overlay-{n:04d}.png'
        with Image.open(path) as im:
            assert im.size==SIZE and im.mode=='RGBA'
            alpha=im.getchannel('A')
            assert alpha.crop((0,996,1920,1080)).getbbox() is None,'Annotation overlaps existing subtitles'
            max_covered=max(max_covered,SIZE[0]*SIZE[1]-alpha.histogram()[0])
        assets.append({'frame':n,'sha256':sha(path)})
    write(REVIEW/'overlay-hashes.json',assets)
    assert max_covered/(1920*1080)<.02,'Annotations must remain unobtrusive'
    checkbox_checks=[]
    for label,ts,ys in [('row-1',(3.2,3.8),(539,539)),('row-2',(5.2,5.8),(567,539)),('row-3',(7.2,7.8),(539,539))]:
        green=[]
        for t,y in zip(ts,ys,strict=True):
            im,_=source_frame('A2',t)
            green.append(sum(1 for r,g,b in im.crop((349,y-5,361,y+6)).get_flattened_data()
                             if r<100 and g>r*1.3 and g>b*1.05))
        assert green[0]<10 and green[1]>25,(label,green)
        checkbox_checks.append({'row':label,'source_times_s':ts,'observed_green_checkbox_pixels_before_after':green,'state_change':'unchecked -> checked'})
    write(REVIEW/'checkbox-state-checks.json',checkbox_checks)
    media=[]
    moments=[1,4.2,6.3,9.5,15.25,15.8,17.2,17.7,19.3,19.7,28.33,28.83,47.2,48.3,52.15,53.25,57.2,58.25,108.33,108.8,136.3,136.8,177.45,177.95,184,193]
    for variant in ('clean','subtitled'):
        path=OUT/f'oxyproof-browser-demo-cursor-{variant}.mp4'
        info=json.loads(run([BIN/'ffprobe.exe','-v','error','-show_streams','-show_format','-of','json',path]))
        assert len(info['streams'])==1;s=info['streams'][0]
        assert [s[k] for k in ('codec_name','width','height','pix_fmt','r_frame_rate','nb_frames')]==['h264',1920,1080,'yuv420p','30/1','5850']
        assert s['color_range']=='tv' and math.isclose(float(info['format']['duration']),195,abs_tol=.001)
        run([BIN/'ffmpeg.exe','-v','error','-threads','2','-xerror','-i',path,'-f','null','-'])
        media.append({'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'duration_s':195,
            'width':1920,'height':1080,'fps':30,'frames':5850,'audio_streams':0,'full_decode':'PASS'})
        print('FULL_DECODE_PASS',path.name,flush=True)
        select='+'.join(f'eq(n,{round(t*30)})' for t in moments)
        run([BIN/'ffmpeg.exe','-v','error','-y','-threads','2','-filter_threads','1','-i',path,
             '-vf',f"select='{select}'",'-fps_mode','vfr','-frames:v',len(moments),'-threads','2','-q:v','2',REVIEW/f'{variant}-qa-%02d.jpg'])
        contact=Image.new('RGB',(1920,math.ceil(len(moments)/4)*300),'#111418');d=ImageDraw.Draw(contact)
        for i,t in enumerate(moments):
            with Image.open(REVIEW/f'{variant}-qa-{i+1:02}.jpg') as im:thumb=im.resize((480,270),Image.Resampling.LANCZOS)
            x=i%4*480;y=i//4*300;contact.paste(thumb,(x,y));d.text((x+8,y+275),f'{t:.2f} s',fill='white')
        contact.save(REVIEW/f'{variant}-contact.jpg',quality=94)
    write(REVIEW/'verification.json',{'technical_status':'PASS','visual_review':'PENDING',
        'verified_at_utc':datetime.now(timezone.utc).isoformat(),'media':media,
        'protected_files_unchanged':len(protected),'timeline_s':195,'annotated_actions':len(p['annotations']),
        'overlay_nonempty_frames':len(assets),'subtitle_area_annotation_alpha':'ZERO on all 441 nonempty overlays',
        'maximum_annotation_canvas_fraction':max_covered/(1920*1080),
        'checkbox_state_changes':checkbox_checks,
        'original_srt_sha256':sha(OUT/'oxyproof-browser-demo.srt'),
        'application_tests':'NOT_RUN: media-only edit','new_browser_actions':0,'new_model_calls':0})
    print('VERIFICATION_PASS; visual review pending',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','render','verify']);args=ap.parse_args()
    {'prepare':prepare,'render':render,'verify':verify}[args.action]()
