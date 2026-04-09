"""Step 2: 60초 사물 독백 대본 생성 — Thinking OS 5단계 적용"""

SCRIPT_PROMPT = """\
당신은 사물쇼츠 대본 작가입니다.
아래 아이디어 프레임을 바탕으로 60초 분량의 사물 1인칭 독백 대본을 작성하세요.

## 아이디어 프레임
- 사물: {topic}
- 페르소나: {persona}
- 현상: {stage1_phenomenon}
- 패턴: {stage2_pattern}
- 구조: {stage3_structure}
- 전제 해체: {stage4_deconstruct}
- 재설계: {stage5_redesign}
- 훅 질문: {hook_question}
- 감정 흐름: {emotional_arc}

## 대본 규칙
1. 사물의 1인칭 독백 (나 = {topic})
2. 총 길이: 약 250~300자 (60초 TTS 기준)
3. 구조:
   - [0-3초] 훅 — 시청자를 멈추게 하는 질문/선언
   - [3-15초] 현상+패턴 — 공감 유도
   - [15-35초] 구조+전제 해체 — 반전과 통찰
   - [35-55초] 재설계 — 새로운 시선 제안
   - [55-60초] 마무리 — 여운을 남기는 한 문장
4. 말투: 담담하지만 따뜻한, 약간의 자조 섞인 독백체
5. 쉼표와 마침표로 호흡 조절

## 출력 형식 (JSON)
{{
  "title": "영상 제목 (유튜브 쇼츠용, 30자 이내)",
  "script": "전체 대본 텍스트",
  "sections": [
    {{"time": "0-3s", "label": "훅", "text": "..."}},
    {{"time": "3-15s", "label": "현상+패턴", "text": "..."}},
    {{"time": "15-35s", "label": "구조+전제해체", "text": "..."}},
    {{"time": "35-55s", "label": "재설계", "text": "..."}},
    {{"time": "55-60s", "label": "마무리", "text": "..."}}
  ],
  "char_count": 0,
  "estimated_seconds": 0
}}
"""


def generate_script(idea: dict, config: dict, dry_run: bool = False) -> dict:
    """아이디어 프레임에서 60초 사물 독백 대본을 생성한다."""
    if dry_run:
        topic = idea["topic"]
        script_text = (
            f"당신이 마지막으로 {topic}을 진심으로 바라본 게 언제였나요? "
            f"나는 {topic}입니다. 매일 당신 곁에 있지만, 당신은 나를 보지 않죠. "
            f"그게 익숙함의 구조입니다. 하지만 정말 그래야 할까요? "
            f"오늘, 나를 한 번만 다시 바라봐 주세요."
        )
        return {
            "title": f"[DRY-RUN] {topic}의 독백",
            "script": script_text,
            "sections": [
                {"time": "0-3s", "label": "훅", "text": f"당신이 마지막으로 {topic}을 진심으로 바라본 게 언제였나요?"},
                {"time": "3-15s", "label": "현상+패턴", "text": f"나는 {topic}입니다. 매일 당신 곁에 있지만, 당신은 나를 보지 않죠."},
                {"time": "15-35s", "label": "구조+전제해체", "text": "그게 익숙함의 구조입니다. 하지만 정말 그래야 할까요?"},
                {"time": "35-55s", "label": "재설계", "text": "오늘, 나를 한 번만 다시 바라봐 주세요."},
                {"time": "55-60s", "label": "마무리", "text": "...그게 시작이니까요."},
            ],
            "char_count": len(script_text),
            "estimated_seconds": 60,
        }

    import anthropic
    client = anthropic.Anthropic()
    claude_config = config.get("claude", {})

    message = client.messages.create(
        model=claude_config.get("model", "claude-sonnet-4-6-20250514"),
        max_tokens=claude_config.get("max_tokens", 4096),
        messages=[{"role": "user", "content": SCRIPT_PROMPT.format(**idea)}],
    )

    import json
    text = message.content[0].text
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])
