"""Step 1: 사물 아이디어 확장 -- Thinking OS 5단계 프레임 설계"""

IDEA_PROMPT = """\
당신은 '사물쇼츠' 크리에이터입니다.
주어진 사물을 주인공으로, Thinking OS 5단계 독백 프레임을 설계하세요.
반드시 작성자가 전달하려는 메시지를 중심으로 5단계를 구성하세요.

## Thinking OS 5단계
1. 현상 -- 이 사물이 매일 겪는 당연한 현실
2. 패턴 -- 사람들이 이 사물을 대하는 반복 패턴
3. 구조 -- 왜 그 패턴이 유지되는지 숨은 구조
4. 전제 해체 -- "그게 정말 당연한가?" 뒤집기
5. 재설계 -- 사물이 제안하는 새로운 관계

## 사물: {topic}
## 전달 메시지: {message}

## 출력 형식 (JSON)
{{
  "topic": "사물명",
  "message": "작성자가 전달하려는 메시지 (원문 그대로)",
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


def generate_idea(topic: str, config: dict, dry_run: bool = False, message: str = "") -> dict:
    """사물 주제 + 전달 메시지에서 Thinking OS 5단계 아이디어 프레임을 생성한다."""
    if dry_run:
        return {
            "topic": topic,
            "message": message,
            "persona": f"쓰이고 닳아가면서도 말 못 하는 {topic}의 목소리",
            "stage1_phenomenon": f"{topic}은 매일 쓰이지만, 누구도 그 존재를 의식하지 않는다",
            "stage2_pattern": f"필요할 때만 찾고, 다 쓰면 버린다 -- 그게 {topic}과의 관계 전부다",
            "stage3_structure": f"'도구는 기능이 전부'라는 효율의 논리가 {topic}을 투명하게 만든다",
            "stage4_deconstruct": f"정말 {topic}은 기능 외에 아무 의미도 없는 걸까?",
            "stage5_redesign": f"{message}",
            "hook_question": f"지금 손에 든 {topic}, 이름이 뭔지 아세요?",
            "emotional_arc": "무관심 -> 자각 -> 불편 -> 성찰 -> 따뜻한 결심",
        }

    import anthropic
    client = anthropic.Anthropic()
    claude_config = config.get("claude", {})

    resp = client.messages.create(
        model=claude_config.get("model", "claude-sonnet-4-6-20250514"),
        max_tokens=claude_config.get("max_tokens", 4096),
        messages=[{"role": "user", "content": IDEA_PROMPT.format(topic=topic, message=message)}],
    )

    import json
    text = resp.content[0].text
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])
