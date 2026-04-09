"""Step 1: 사물 아이디어 확장 — Thinking OS 5단계 프레임 설계"""

import anthropic

IDEA_PROMPT = """\
당신은 '사물쇼츠' 크리에이터입니다.
주어진 사물을 주인공으로, Thinking OS 5단계 독백 프레임을 설계하세요.

## Thinking OS 5단계
1. 현상 — 이 사물이 매일 겪는 당연한 현실
2. 패턴 — 사람들이 이 사물을 대하는 반복 패턴
3. 구조 — 왜 그 패턴이 유지되는지 숨은 구조
4. 전제 해체 — "그게 정말 당연한가?" 뒤집기
5. 재설계 — 사물이 제안하는 새로운 관계

## 사물: {topic}

## 출력 형식 (JSON)
{{
  "topic": "사물명",
  "persona": "이 사물의 성격/말투 (1줄)",
  "stage1_phenomenon": "현상 (1줄)",
  "stage2_pattern": "패턴 (1줄)",
  "stage3_structure": "구조 (1줄)",
  "stage4_deconstruct": "전제 해체 (1줄)",
  "stage5_redesign": "재설계 (1줄)",
  "hook_question": "첫 3초 질문 (시청자를 멈추게 하는 한 문장)",
  "emotional_arc": "감정 흐름 요약 (1줄)"
}}
"""


def generate_idea(topic: str, config: dict, dry_run: bool = False) -> dict:
    """사물 주제에서 Thinking OS 5단계 아이디어 프레임을 생성한다."""
    if dry_run:
        return {
            "topic": topic,
            "persona": f"[DRY-RUN] {topic}의 독백 페르소나",
            "stage1_phenomenon": "현상 — 매일 반복되는 일상",
            "stage2_pattern": "패턴 — 사람들의 무의식적 행동",
            "stage3_structure": "구조 — 그 패턴을 유지시키는 시스템",
            "stage4_deconstruct": "전제 해체 — 정말 그래야 하는가?",
            "stage5_redesign": "재설계 — 새로운 관계 제안",
            "hook_question": f"당신이 마지막으로 {topic}을 진심으로 바라본 게 언제였나요?",
            "emotional_arc": "무심 → 공감 → 불편 → 각성 → 따뜻함",
        }

    client = anthropic.Anthropic()
    claude_config = config.get("claude", {})

    message = client.messages.create(
        model=claude_config.get("model", "claude-sonnet-4-6-20250514"),
        max_tokens=claude_config.get("max_tokens", 4096),
        messages=[{"role": "user", "content": IDEA_PROMPT.format(topic=topic)}],
    )

    import json
    text = message.content[0].text
    # Extract JSON from response
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])
