**OxyProof — owner narration mix acceptance**

```text
AUDIO_VIDEO_MUX_STATUS=PASS
VIDEO_PAYLOAD_PRESERVED=YES
OWNER_VOICE_USED=YES
VOICE_SPEED_AND_PITCH_PRESERVED=YES
FULL_AUDIO_VIDEO_DECODE=PASS
ORIGINAL_INPUTS_PRESERVED=YES
MANUAL_AUDIO_LISTENING=NOT_RUN
WORD_LEVEL_SYNC=NOT_CERTIFIED
PUBLICATION_STATUS=NOT_PUBLISHED
```

The owner's actual recording is combined with the accepted final cursor videos. Both narrated files are 195.000 seconds, 1920×1080, H.264/yuv420p/TV range, 30 fps / 5,850 frames, with AAC stereo audio at 48 kHz and faststart. Their encoded video payloads match the corresponding silent masters exactly: scientific values, genuine browser actions, cursor graphics, original subtitles and all scene timing are unchanged. Video was stream-copied, without image re-encoding.

| Output | Bytes | SHA-256 |
|---|---:|---|
| oxyproof-browser-demo-final-clean-narrated.mp4 | 17301371 | `1ba038f6a424d63a8dc79ade98ce7fd03e5c72c6bc599396d2802d1c9939530d` |
| oxyproof-browser-demo-final-subtitled-narrated.mp4 | 17993178 | `50049b6e146ec8ee68d8d6ca1f45b776f28ee616e0a451f070abbd0e24f4f412` |

The aligned standalone audio is `oxyproof-owner-narration-aligned.m4a`. Source recording: `20261022_123813.m4a`, 189.130667 seconds, AAC stereo/48 kHz, SHA-256 `e3a516cbadc13e5438ef91cb553101ca50cd713712b5ba4d1592d55b64a6f4ed`. The original file is untouched. Its private messaging-app path is kept in ignored `.local/narration-mix/source-config.json`, outside shareable documentation.

Audio processing uses a 70 Hz high-pass and measured two-pass dynamic loudness normalization, followed by AAC at 192 kb/s. The original voice, words, speed and pitch are retained. No music or generated voice was added. After encoding, actual integrated loudness is **-16.47 LUFS**, true peak **-0.55 dBTP**, and loudness range **4.10 LU**. The processing targets were -16 LUFS and -1.5 dBTP; those targets are distinct from the measured post-AAC values.

Main narration timing remains as recorded. A 4.65-second pause is inserted at source time 185.55 seconds, inside the measured quiet interval 185.285521–185.808521 seconds, detected below -48 dB. This moves the early closing line into the final dashboard section. The approximate last spoken sound moves to 193.303292 seconds, and the remaining tail is padded to 195 seconds. No speech was intentionally removed or sped up. Opening and ending fades are limited to 20 ms and 300 ms outside the spoken content. Chapter correspondence is approximate; word-perfect synchronization is not certified.

Original subtitles remain the 25 concise action/scientific-disclosure cues. They summarize the demonstration and are not a verbatim transcript of the owner's simplified narration. The earlier scientific limitations and historical DeepSeek replay labels remain visible.

Actual validation:

- Both complete audio/video streams decoded with FFmpeg `-xerror`, exit 0.
- Both files have 195-second video and audio, zero start offsets, and the expected dimensions, frame count and audio format.
- Encoded video payload hashes match the silent masters; both muxed audio payloads match the aligned M4A.
- Actual loudness and true peak passed the chosen -17.5 to -14.5 LUFS and below -0.5 dBTP checks.
- All **539 protected inputs** match their pre-mix hashes, including the original recording, silent media, source documents, source manifests and project files.
- Earlier final-polish visual validation is inherited because the complete encoded video payload is unchanged. No fresh subjective listening or continuous browser-player pass is claimed.

Commands actually executed from the repository root, both final stages exiting 0:

```powershell
.\.local\pdf-venv\Scripts\python.exe output/osi-final/browser-demo/review/mix_owner_narration.py mix
.\.local\pdf-venv\Scripts\python.exe output/osi-final/browser-demo/review/mix_owner_narration.py verify
```

The script refuses existing output files. Actual verification printed both `FULL_AUDIO_VIDEO_DECODE_PASS` lines and `VERIFICATION_PASS integrated_LUFS -16.47 true_peak_dBTP -0.55 protected 539`. Machine-readable evidence: [mix configuration](review/narration/mix-configuration.json), [verification](review/narration/verification.json), [audio measurements](review/narration/final-audio-loudness.log).

Local ASR was used only to help locate chapters. It misrecognizes names and some words, so its output was not used as subtitles, a certified transcript, or replacement speech. Tools: [whisper.cpp v1.8.4](https://github.com/ggml-org/whisper.cpp/releases/tag/v1.8.4) and the [official model repository](https://huggingface.co/ggerganov/whisper.cpp/tree/5359861). The Windows ZIP matched the published checksum; base.en-q5_1 inference ran locally on CPU. No audio was uploaded. Downloads, raw decoded audio, ASR outputs and logs remain under ignored `.local/` paths.

Limitations: the tool runtime explicitly does not support audio input, so manual listening, pronunciation/intelligibility judgement and subjective sound-quality review are **NOT RUN**. Owner playback is the next review step. The initial built-in Windows recognizer produced inaccurate results and an end-of-stream loop; that owned process was stopped and none of its output was used. Application tests were NOT RUN for this media-only task. Earlier browser playback limitations are not claimed resolved.

New files are the two narrated MP4s, aligned M4A, this report, `review/mix_owner_narration.py` and `review/narration/` evidence. No original script/SRT was rewritten. No application edit, browser recording, new scientific result, DeepSeek request, synthetic voice, dependency change to the application, commit, push, upload or submission occurred.
