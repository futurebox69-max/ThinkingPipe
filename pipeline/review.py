"""Step 6: 판단 게이트 -사람이 y/n으로 검수"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import json

console = Console()


def review_gate(
    stage_name: str, data: dict, dry_run: bool = False, auto_approve: bool = False
) -> bool:
    """파이프라인 중간에 사람이 결과를 확인하고 승인/거부한다.

    Returns:
        True if approved, False if rejected.
    """
    console.print()
    console.print(
        Panel(
            f"[bold yellow]검수 게이트: {stage_name}[/bold yellow]",
            border_style="yellow",
        )
    )

    # Pretty-print the data
    if isinstance(data, dict):
        _print_dict(data, stage_name)
    else:
        console.print(str(data))

    if dry_run or auto_approve:
        console.print("[dim]→ 자동 승인 (dry-run/auto)[/dim]")
        return True

    console.print()
    response = console.input("[bold]승인하시겠습니까? (y/n): [/bold]").strip().lower()
    approved = response in ("y", "yes", "ㅛ", "네")

    if approved:
        console.print("[green]>> 승인됨[/green]")
    else:
        console.print("[red]>> 거부됨 -- 파이프라인 중단[/red]")

    return approved


def _print_dict(data: dict, stage: str):
    """딕셔너리를 보기 좋게 출력한다."""
    if stage == "대본" and "sections" in data:
        # Script-specific display
        table = Table(title=data.get("title", "대본"), show_lines=True)
        table.add_column("시간", style="cyan", width=10)
        table.add_column("구간", style="yellow", width=12)
        table.add_column("텍스트", style="white")

        for s in data["sections"]:
            table.add_row(s["time"], s["label"], s["text"])

        console.print(table)
        console.print(f"[dim]글자 수: {data.get('char_count', '?')} | "
                      f"예상 시간: {data.get('estimated_seconds', '?')}초[/dim]")

    elif stage == "훅 최적화" and "alternatives" in data:
        console.print(f"[bold]현재 훅:[/bold] {data.get('original_hook', '')}")
        console.print(f"[dim]{data.get('analysis', '')}[/dim]")
        console.print()
        for i, alt in enumerate(data["alternatives"]):
            marker = " [green]* 추천[/green]" if i == data.get("recommended", -1) else ""
            console.print(f"  [{i+1}] {alt['hook']}{marker}")
            console.print(f"      [dim]{alt['strategy']}[/dim]")

    else:
        formatted = json.dumps(data, ensure_ascii=False, indent=2)
        console.print(formatted)
