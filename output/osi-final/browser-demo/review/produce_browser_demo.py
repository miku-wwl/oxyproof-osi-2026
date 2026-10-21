"""Render genuine full-application IAB operations, without an explainer template.

Requires the preserved private skill captures. No browser, model or scientific engine calls.
"""
import bisect
import hashlib
import json
import subprocess
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
RAW=ROOT/'.local/browser-demo-capture'
WORK=ROOT/'.local/browser-demo-render'
BIN=ROOT/'.local/media-tools/ffmpeg-essentials/ffmpeg-9.0.2-essentials_build/bin'
TAKES=[('A1',12),('A2',23),('B',40),('B-roots',20),('C',40),('D',30),('E',25),('F-ready',5)]
# Only the capture interface's unused right/bottom padding is removed.
# The entire rendered webpage, including sidebar and scrollbar, remains visible.
CROP=(0,0,1749,984)
CUES=[
(.8,6,'OxyProof: a real, evidence-grounded research workflow.'),
(6.3,11.5,'Select the published Huang source group.'),
(13,22,'Choose source rows 1, 2 and 3.'),
(23.5,27,'Set the interval to 700-1000 K.'),
(28.3,34,'Click Analyze. The backend calculates the curves.'),
(35.3,40,'Published fits, explicit units and evidence limits.'),
(40.5,46,'700 K: source-row order 1 > 2 > 3.'),
(47.5,55,'Drag the actual slider; ordering changes with temperature.'),
(59,67,'1000 K: source-row order 3 > 2 > 1.'),
(70.3,74.5,'Return to 700 K for a direct comparison.'),
(79,84.5,'Inspect the analytical crossing near 776 K.'),
(85,90,'Then inspect the model crossings near 818 K and 854 K.'),
(90.3,94.8,'Calculated fits, not measured crossovers. No uncertainty bounds.'),
(96,102.7,'Open Research Agent and its recorded DeepSeek evidence.'),
(103.3,109.8,'Load saved genuine API traces. No new inference.'),
(110.2,117.5,'Replay B: DeepSeek selected analyze_temperature_interval.'),
(119.3,126.5,'Inspect validated arguments and the local scientific result.'),
(130.2,134.8,'Independent auditing controls the scientific conclusion.'),
(136.3,142.5,'Replay C: 600 C, 10% humidity and 10,000 operating hours.'),
(143,149.3,'The model proposed screening; the independent guard checks the requirements.'),
(150,157,'No scientific tool executed. No candidates recommended.'),
(158,164.7,'INSUFFICIENT_EVIDENCE: OxyProof abstains.'),
(166,174.5,'Return to the source rows, DOI and published fit parameters.'),
(176.5,181.8,'Click Export JSON to download the actual decision report.'),
(183,189.5,'Inspect a byte-identical local copy of the downloaded JSON.'),
]
NARRATION=[
(0,35,'Open the dashboard, select evidence and run the analysis',
 'Here is OxyProof, running locally with 483 published records. I open the Temperature Decision Explorer and choose the Huang bulk-conductivity source group. I clear the selection, then choose source rows one, two and three. These records share a reported method and measured temperature range. I set the analysis interval from 700 to 1000 kelvin, and click Analyze. The backend now computes the conductivity curves using the published fits.'),
(35,75,'Operate the actual temperature controls',
 'The curves are calculations from curated experimental fit parameters. At 700 kelvin, the conditional order is one, two, three. I now drag the actual temperature control through the interval. The selected fits and the relative conductivities change. At 1000 kelvin, the order has reversed: three, two, one. Clicking back to 700 kelvin makes the difference clear. This is a conditional comparison within one source group, rather than a universal ranking across experiments.'),
(75,95,'Inspect crossings and limits',
 'Here are the analytical model crossings, near 776, 818 and 854 kelvin. They are calculated intersections, not measured crossover temperatures. Published T-star boundaries are reviewed separately. Uncertainty bounds are unavailable, and original sample conditions still need checking.'),
(95,135,'Load genuine evidence and click Replay B',
 'Next I open the Research Agent and load the recorded DeepSeek acceptance traces. This replays genuine API executions captured earlier; it does not make a new model request. I select Replay B. DeepSeek Flash chose the temperature-interval analysis tool. Here are its validated arguments, followed by the deterministic scientific result and independent evidence audit. The model selects a bounded tool, while the local physics engine determines the numbers. Provider prose cannot introduce scientific evidence.'),
(135,165,'Click Replay C and inspect abstention',
 'Now I click Replay C. This question asks for operation at 600 degrees Celsius, ten percent humidity and ten thousand hours of stability. The model proposed screening and flagged unsupported requirements. The independent validator retained both conditions and blocked scientific execution. No calculation tool ran and no candidates were recommended. The result is insufficient evidence, with future measurements proposed rather than invented.'),
(165,190,'Export and inspect actual evidence',
 'I return to the original records and source DOI. The low- and high-temperature fit parameters, units and evidence limits remain visible. I click Export JSON, then open a byte-identical local copy of the downloaded file. It preserves the source records, calculation trace, rankings and warnings for review.'),
(190,195,'Return to the dashboard',
 'OxyProof makes the scientific decision, and its limits, inspectable.'),
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def wrap(s): return textwrap.wrap(s,50,break_long_words=False,break_on_hyphens=False)
def run(args): subprocess.run([str(x) for x in args],check=True)
def caption(t): return next((s for a,b,s in CUES if a<=t<b),'')
def final_overlay(im,text):
    if not text:return im
    im=im.convert('RGBA'); layer=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(layer)
    lines=wrap(text); assert len(lines)<=2
    d.rectangle((0,996,1920,1080),fill=(0,0,0,185))
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',30)
    y=1000 if len(lines)==2 else 1017
    for line in lines:
        w=d.textlength(line,font=font);d.text(((1920-w)/2,y),line,font=font,fill='white');y+=35
    return Image.alpha_composite(im,layer).convert('RGB')

def main():
    previous=0
    for a,b,s in CUES:
        assert previous<=a<b<=195 and len(wrap(s))<=2 and len(s)/(b-a)<20
        previous=b
    OUT.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    (OUT/'oxyproof-browser-demo.srt').write_text('\n'.join(
        f'{i}\n{stamp(a)} --> {stamp(b)}\n'+ '\n'.join(wrap(s))+'\n'
        for i,(a,b,s) in enumerate(CUES,1)),encoding='utf-8')
    words=sum(len(s.split()) for _,_,_,s in NARRATION)
    md=['# OxyProof browser-operation narration','',
        f'03:15 / 195 seconds. {words} spoken words; {words/195*60:.1f} words/minute including pauses.',
        'Silent masters: owner voice recording is pending. Minimal SRT cues summarize the visible actions; they are intentionally shorter than this full narration.',
        'Use normal spoken English. Kelvin has no degrees. DeepSeek is pronounced "deep seek"; JSON is "JAY-sun".',
        'All clicks/scrolls/dragging shown are genuine IAB operations. The API capture does not include the system mouse pointer; no fake cursor was added.', '']
    for a,b,title,s in NARRATION:
        md.extend([f'## {stamp(a)[:8]} - {stamp(b)[:8]} | {title}','',s,''])
    (OUT/'BROWSER_DEMO_NARRATION.md').write_text('\n'.join(md),encoding='utf-8')
    entries={'clean':[],'subtitled':[]}; cache={}; overlay_cache={};offset=0;provenance=[]
    actions=[]
    for name,duration in TAKES:
        folder=RAW/name;mp=folder/'capture-manifest.json';m=json.loads(mp.read_text(encoding='utf-8'))
        assert m['source_browser']=='Codex In-app Browser' and m['status']=='CAPTURED_UNVERIFIED'
        assert not m.get('error') and m['duration_seconds']>=duration
        fs=[f for f in m['frames'] if f['t']<duration]
        assert all(b['t']>a['t'] for a,b in zip(fs,fs[1:]))
        dims=set()
        for f in fs:
            p=(folder/f['file']).resolve();assert p.is_relative_to(folder.resolve()) and sha(p)==f['sha256']
            with Image.open(p) as im:dims.add(im.size)
        assert dims=={(1921,1081)},f'Review a changed capture size: {name}: {dims}'
        for e in m['events']:
            if e['kind']=='ui-step':
                assert not e.get('failed') and e.get('completed_t',1e9)<duration
                actions.append({'take':name,'action':e['label'],'video_request_s':round(offset+e['requested_t'],3),
                                'video_complete_s':round(offset+e['completed_t'],3)})
        provenance.append({'take':name,'manifest':str(mp.relative_to(ROOT)),'manifest_sha256':sha(mp),
            'video_interval_s':[offset,offset+duration],'source_range_s':[0,duration],
            'capture_average_fps':m['average_acquisition_fps'], 'max_sample_gap_s':m['max_inter_sample_gap_seconds'],
            'source_dimensions':sorted(dims),'source_frames_used':len(fs),'playback_speed':1})
        times=[0]+[f['t'] for f in fs[1:]]
        cuts=sorted(set(times+[duration]+[t-offset for a,b,s in CUES for t in (a,b) if offset<t<offset+duration]
                        +[t-offset for t in [192] if offset<t<offset+duration]))
        for a,b in zip(cuts,cuts[1:]):
            f=fs[bisect.bisect_right(times,a)-1];key=f['sha256'];global_time=offset+(a+b)/2
            if key not in cache:
                with Image.open(folder/f['file']) as im:
                    canvas=ImageOps.fit(im.convert('RGB').crop(CROP),(1920,1080),Image.Resampling.LANCZOS)
                file=WORK/f'clean-{len(cache):05}.jpg';canvas.save(file,quality=97,subsampling=0);cache[key]=file
            clean=cache[key]
            closing=global_time>=192
            for variant in entries:
                text=('https://github.com/miku-wwl/oxyproof-osi-2026' if closing else
                      caption(global_time) if variant=='subtitled' else '')
                if text:
                    k=(str(clean),text)
                    if k not in overlay_cache:
                        file=WORK/f'caption-{len(overlay_cache):05}.jpg'
                        with Image.open(clean) as im:final_overlay(im,text).save(file,quality=97,subsampling=0)
                        overlay_cache[k]=file
                    file=overlay_cache[k]
                else:file=clean
                entries[variant].append((file,b-a))
        offset+=duration
        print('COMPOSED',name,duration,flush=True)
    assert offset==195
    proof={'skill_display_name':'IAB Browser Video','skill_id':'codex-iab-video-recording',
        'skill_path':'C:/Users/weila/.codex/skills/codex-iab-video-recording/SKILL.md',
        'browser':{'name':'ChatGPT in-app browser','type':'iab','browser_id':'2','application_tab_id':'1'},
        'method':'Actual skill capture_iab.mjs; actual render_iab.py preflight; verified timestamped raw frames rendered here',
        'previous_explainer_reused':False,'previous_raw_frames_inspected':True,
        'recapture_reason':'Complete selection/Analyze/Replay-C/download-preview action chain, consistent current 700-1000 K request and higher-resolution source; earlier originals preserved',
        'source_screenshot_dimensions':[1921,1081],'source_padding_crop':list(CROP),
        'crop_reason':'Unused capture-interface padding at right/bottom removed after raw-frame inspection; rendered webpage/sidebar/scrollbar retained',
        'effective_webpage_crop_dimensions':[1749,984],'effective_scale_to_export':[1920/1749,1080/984],
        'native_1080p_capture_claimed':False,'export_dimensions':[1920,1080],'export_fps':30,
        'source_acquisition_is_native_30fps':False,'duration_s':195,'silent':True,
        'system_mouse_pointer_capture':'UNAVAILABLE','synthetic_cursor_added':False,
        'native_browser_chrome_capture':False,'webpage_visible_canvas_fraction_clean':1.0,
        'minimum_unobscured_webpage_fraction_with_caption':(1080-84)/1080,
        'permanent_title_banner':False,'commentary_sidebar':False,'presentation_template':False,
        'closing_url_overlay_seconds':[192,195],'new_provider_calls':0,'takes':provenance,'actions':actions}
    (OUT/'review/recording-provenance.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    for variant,items in entries.items():
        lines=['ffconcat version 1.0']
        for file,gap in items:lines += [f"file '{file.as_posix()}'",'option framerate 1000',f'duration {gap:.9f}']
        lines += [f"file '{items[-1][0].as_posix()}'",'option framerate 1000']
        concat=WORK/f'{variant}.ffconcat';concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        dest=OUT/f'oxyproof-browser-demo-{variant}.mp4'
        run([BIN/'ffmpeg.exe','-v','error','-n','-f','concat','-safe','0','-i',concat,
            '-vf','scale=in_range=pc:out_range=tv,format=yuv420p','-frames:v','5850','-r','30','-fps_mode','cfr',
            '-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-color_range','tv',
            '-threads','4','-movflags','+faststart',dest])
        print('RENDERED',dest.name,flush=True)

if __name__=='__main__':main()
