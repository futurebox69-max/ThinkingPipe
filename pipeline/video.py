"""Step 4: 영상 생성 — Veo 3.1 + gTTS 음성 합성"""

import os
from pathlib import Path


def generate_video(
    script_data: dict, config: dict, output_dir: str, dry_run: bool = False
) -> dict:
    """대본에서 TTS 음성을 생성하고, Veo 3.1 영상 프롬프트를 준비한다."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    tts_path = out / "narration.mp3"
    video_path = out / "video.mp4"

    if dry_run:
        # Write placeholder files
        tts_path.write_text("[DRY-RUN] TTS audio placeholder")
        video_path.write_text("[DRY-RUN] Video placeholder")

        veo_prompt = _build_veo_prompt(script_data)
        return {
            "tts_path": str(tts_path),
            "video_path": str(video_path),
            "veo_prompt": veo_prompt,
            "status": "dry-run",
        }

    # --- TTS via gTTS ---
    from gtts import gTTS

    tts_config = config.get("tts", {})
    tts = gTTS(
        text=script_data["script"],
        lang=tts_config.get("lang", "ko"),
        slow=tts_config.get("slow", False),
    )
    tts.save(str(tts_path))

    # --- Veo 3.1 prompt (manual step — print for user) ---
    veo_prompt = _build_veo_prompt(script_data)

    return {
        "tts_path": str(tts_path),
        "video_path": str(video_path),
        "veo_prompt": veo_prompt,
        "status": "tts-complete, video-prompt-ready",
    }


def _build_veo_prompt(script_data: dict) -> str:
    """Veo 3.1에 넣을 영상 생성 프롬프트를 조립한다."""
    topic = script_data.get("title", "사물")
    sections = script_data.get("sections", [])

    scene_descriptions = []
    for s in sections:
        scene_descriptions.append(f"[{s['time']}] {s['label']}: {s['text']}")

    return f"""\
Cinematic 9:16 vertical short film. 60 seconds.
Subject: {topic} — extreme close-up, soft studio lighting.
Style: Minimal, contemplative, warm color grading. Shallow depth of field.
Camera: Slow dolly-in, occasional macro detail shots.
Mood: Quiet introspection turning to warmth.

Scene breakdown:
{chr(10).join(scene_descriptions)}

No text overlays. No background music. Voice-over will be added separately.
"""
