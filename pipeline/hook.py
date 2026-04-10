"""Step 3: 훅 최적화 — 첫 3초 질문/선언 강화"""

HOOK_PROMPT = """\
당신은 유튜브 쇼츠 훅 전문가입니다.
아래 대본의 훅(첫 3초)을 분석하고 3가지 대안을 제시하세요.

## 현재 훅
{current_hook}

## 전체 대본
{script}

## 훅 최적화 기준
1. 스크롤 멈춤 — 1초 안에 "뭐지?" 반응 유발
2. 사물 정체성 — 사물이 말한다는 반전 내포
3. 감정 유발 — 호기심, 불편함, 공감 중 하나
4. 길이 — 15자 이내 (3초 TTS 기준)

## 출력 형식 (JSON)
{{
  "original_hook": "현재 훅",
  "analysis": "현재 훅의 강점/약점 (2줄)",
  "alternatives": [
    {{"hook": "대안1", "strategy": "전략 설명"}},
    {{"hook": "대안2", "strategy": "전략 설명"}},
    {{"hook": "대안3", "strategy": "전략 설명"}}
  ],
  "recommended": 0,
  "reason": "추천 이유 (1줄)"
}}
"""


def optimize_hook(script_data: dict, config: dict, dry_run: bool = False) -> dict:
    """대본의 훅을 분석하고 최적화 대안을 생성한다."""
    current_hook = script_data["sections"][0]["text"]

    if dry_run:
        topic = script_data["title"].replace("[테스트] ", "").replace("[DRY-RUN] ", "").replace("의 독백", "")
        return {
            "original_hook": current_hook,
            "analysis": f"[테스트] 현재 훅이 {topic}의 핵심 메시지와 연결되는지 점검 필요",
            "alternatives": [
                {"hook": f"나는 {topic}인데, 할 말이 있어.", "strategy": "직접 선언형 -- 사물이 입을 여는 반전"},
                {"hook": f"당신이 버린 {topic}, 아직 거기 있어.", "strategy": "감정 충격형 -- 죄책감 유발"},
                {"hook": f"매일 쓰면서 한 번도 안 본 것.", "strategy": "공감 질문형 -- 시청자 자기 점검"},
            ],
            "recommended": 0,
            "reason": f"[테스트] 직접 선언이 사물쇼츠에서 스크롤 멈춤에 가장 효과적",
        }

    import anthropic
    client = anthropic.Anthropic()
    claude_config = config.get("claude", {})

    message = client.messages.create(
        model=claude_config.get("model", "claude-sonnet-4-6-20250514"),
        max_tokens=claude_config.get("max_tokens", 4096),
        messages=[
            {
                "role": "user",
                "content": HOOK_PROMPT.format(
                    current_hook=current_hook,
                    script=script_data["script"],
                ),
            }
        ],
    )

    import json
    text = message.content[0].text
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])
