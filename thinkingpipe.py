#!/usr/bin/env python3
"""ThinkingPipe — 사물쇼츠 AI 영상 자동화 파이프라인 CLI

Thinking OS 5단계(현상→패턴→구조→전제해체→재설계)를
60초 사물 독백 대본에 적용하여 쇼츠 영상을 자동 생성합니다.

Usage:
    python thinkingpipe.py --topic "연필"
    python thinkingpipe.py --topic "연필" --dry-run
    python thinkingpipe.py --topic "우산" --output ./output/umbrella
"""

import sys
from pathlib import Path
from datetime import datetime

import click
import yaml
from rich.console import Console
from rich.panel import Panel

from pipeline.idea import generate_idea
from pipeline.script import generate_script
from pipeline.hook import optimize_hook
from pipeline.video import generate_video
from pipeline.thumbnail import generate_thumbnail
from pipeline.review import review_gate
from pipeline.upload import upload_video

console = Console()


def load_config(config_path: str = "config.yaml") -> dict:
    """설정 파일을 로드한다."""
    p = Path(config_path)
    if p.exists():
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    return {}


@click.command()
@click.option("--topic", required=True, help="사물 주제 (예: 연필, 우산, 지우개)")
@click.option("--dry-run", is_flag=True, default=False, help="API 호출 없이 파이프라인 테스트")
@click.option("--output", default=None, help="출력 디렉토리 (기본: ./output/{topic}_{timestamp})")
@click.option("--config", default="config.yaml", help="설정 파일 경로")
@click.option("--auto-approve", is_flag=True, default=False, help="모든 검수 게이트 자동 승인")
def main(topic: str, dry_run: bool, output: str, config: str, auto_approve: bool):
    """ThinkingPipe — 사물쇼츠 AI 영상 자동화 파이프라인"""
    cfg = load_config(config)

    # Output directory
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"./output/{topic}_{timestamp}"
    Path(output).mkdir(parents=True, exist_ok=True)

    mode = "[DRY-RUN]" if dry_run else "[LIVE]"
    console.print(
        Panel(
            f"[bold cyan]ThinkingPipe {mode}[/bold cyan]\n"
            f"사물: [bold]{topic}[/bold]\n"
            f"출력: {output}",
            title="🎬 사물쇼츠 파이프라인",
            border_style="cyan",
        )
    )

    # ── Step 1: 아이디어 프레임 생성 ──
    console.print("\n[bold]Step 1/6 — 아이디어 프레임 생성[/bold]")
    idea = generate_idea(topic, cfg, dry_run=dry_run)

    if not review_gate("아이디어 프레임", idea, dry_run=dry_run, auto_approve=auto_approve):
        _abort()

    # ── Step 2: 60초 대본 생성 ──
    console.print("\n[bold]Step 2/6 — 60초 독백 대본 생성[/bold]")
    script_data = generate_script(idea, cfg, dry_run=dry_run)

    if not review_gate("대본", script_data, dry_run=dry_run, auto_approve=auto_approve):
        _abort()

    # ── Step 3: 훅 최적화 ──
    console.print("\n[bold]Step 3/6 — 훅 최적화[/bold]")
    hook_result = optimize_hook(script_data, cfg, dry_run=dry_run)

    if not review_gate("훅 최적화", hook_result, dry_run=dry_run, auto_approve=auto_approve):
        _abort()

    # Apply recommended hook
    rec_idx = hook_result.get("recommended", 0)
    if hook_result.get("alternatives"):
        new_hook = hook_result["alternatives"][rec_idx]["hook"]
        script_data["sections"][0]["text"] = new_hook
        # Rebuild full script with new hook
        script_data["script"] = " ".join(s["text"] for s in script_data["sections"])

    # ── Step 4: 영상 + TTS 생성 ──
    console.print("\n[bold]Step 4/6 — TTS 음성 + 영상 프롬프트 생성[/bold]")
    video_result = generate_video(script_data, cfg, output, dry_run=dry_run)

    if not review_gate("영상 생성", video_result, dry_run=dry_run, auto_approve=auto_approve):
        _abort()

    # ── Step 5: 썸네일 생성 ──
    console.print("\n[bold]Step 5/6 — 썸네일 생성[/bold]")
    thumb_result = generate_thumbnail(script_data, cfg, output, dry_run=dry_run)

    if not review_gate("썸네일", thumb_result, dry_run=dry_run, auto_approve=auto_approve):
        _abort()

    # ── Step 6: 업로드 준비 ──
    console.print("\n[bold]Step 6/6 — 업로드 준비[/bold]")
    upload_result = upload_video(
        script_data, video_result, thumb_result, output, cfg, dry_run=dry_run
    )

    # ── 완료 ──
    console.print()
    console.print(
        Panel(
            f"[bold green]파이프라인 완료![/bold green]\n\n"
            f"📁 {output}\n"
            f"상태: {upload_result['status']}",
            title="✅ ThinkingPipe 완료",
            border_style="green",
        )
    )


def _abort():
    """검수 거부 시 파이프라인을 중단한다."""
    console.print("\n[red]파이프라인이 중단되었습니다.[/red]")
    sys.exit(1)


if __name__ == "__main__":
    main()
