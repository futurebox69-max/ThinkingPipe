"""Step 7: 업로드 준비 — 메타데이터 생성 및 업로드 안내"""

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def upload_video(
    script_data: dict,
    video_result: dict,
    thumb_result: dict,
    output_dir: str,
    config: dict,
    dry_run: bool = False,
) -> dict:
    """업로드용 메타데이터를 생성하고, 수동 업로드 가이드를 출력한다."""
    out = Path(output_dir)
    topic = script_data.get("title", "사물쇼츠")
    hook = script_data["sections"][0]["text"] if script_data.get("sections") else ""

    metadata = {
        "title": topic,
        "description": (
            f"{hook}\n\n"
            f"#사물쇼츠 #ThinkingOS #shorts\n\n"
            f"이 영상은 ThinkingPipe로 제작되었습니다.\n"
            f"사물의 시선으로 세상을 다시 봅니다."
        ),
        "tags": ["사물쇼츠", "ThinkingOS", "AI영상", "shorts", topic],
        "visibility": config.get("upload", {}).get("visibility", "private"),
        "files": {
            "video": video_result.get("video_path", ""),
            "thumbnail": thumb_result.get("thumbnail_path", ""),
            "narration": video_result.get("tts_path", ""),
        },
    }

    # Save metadata
    meta_path = out / "upload_metadata.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))

    # Save Veo prompt separately
    veo_path = out / "veo_prompt.txt"
    veo_prompt = video_result.get("veo_prompt", "")
    veo_path.write_text(veo_prompt)

    if not dry_run:
        console.print()
        console.print(
            Panel(
                "[bold green]업로드 준비 완료[/bold green]\n\n"
                f"📁 출력 폴더: {out}\n"
                f"🎬 영상: {metadata['files']['video']}\n"
                f"🖼️  썸네일: {metadata['files']['thumbnail']}\n"
                f"🎙️  나레이션: {metadata['files']['narration']}\n"
                f"📋 메타데이터: {meta_path}\n"
                f"🎨 Veo 프롬프트: {veo_path}\n\n"
                "[dim]YouTube Studio에서 수동 업로드하세요.[/dim]",
                border_style="green",
            )
        )

    return {
        "metadata_path": str(meta_path),
        "veo_prompt_path": str(veo_path),
        "metadata": metadata,
        "status": "dry-run" if dry_run else "ready-to-upload",
    }
