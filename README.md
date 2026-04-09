# ThinkingPipe

사물쇼츠 AI 영상 자동화 파이프라인.

**Thinking OS 5단계**(현상→패턴→구조→전제해체→재설계)를 60초 사물 독백 대본에 적용하여 유튜브 쇼츠를 자동 생성합니다.

## 파이프라인

```
사물 주제 → 아이디어 프레임 → 60초 대본 → 훅 최적화 → TTS+영상 → 썸네일 → 업로드 준비
         [검수]           [검수]        [검수]       [검수]      [검수]
```

각 단계마다 사람이 `y/n`으로 검수합니다.

## 빠른 시작

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key

# 드라이런 (API 호출 없이 파이프라인 테스트)
python thinkingpipe.py --topic "연필" --dry-run

# 실제 실행
python thinkingpipe.py --topic "연필"

# 자동 승인 모드
python thinkingpipe.py --topic "우산" --auto-approve
```

## 기술 스택

| 도구 | 용도 |
|------|------|
| Claude API | 아이디어/대본/훅 생성 |
| gTTS | 한국어 TTS 음성 합성 |
| Veo 3.1 | 영상 생성 (프롬프트 출력) |
| Pillow | 썸네일 이미지 생성 |
| Rich | CLI 인터페이스 |

## 프로젝트 구조

```
ThinkingPipe/
├── thinkingpipe.py          # CLI 메인
├── config.yaml              # 설정
├── requirements.txt
├── pipeline/
│   ├── idea.py              # Step 1: 아이디어 프레임
│   ├── script.py            # Step 2: 60초 대본
│   ├── hook.py              # Step 3: 훅 최적화
│   ├── video.py             # Step 4: TTS + 영상
│   ├── thumbnail.py         # Step 5: 썸네일
│   ├── review.py            # Step 6: 검수 게이트
│   └── upload.py            # Step 7: 업로드 준비
├── skills/
│   ├── 사물선정.md           # 사물 선정 가이드
│   ├── 대본작성.md           # 대본 작성 가이드
│   └── 훅최적화.md           # 훅 최적화 가이드
└── output/                  # 생성물 (gitignore)
```

## Thinking OS 5단계

| 단계 | 질문 | 대본 역할 |
|------|------|-----------|
| 1. 현상 | 이 사물이 매일 겪는 현실은? | 공감 진입점 |
| 2. 패턴 | 사람들이 이 사물을 대하는 반복 패턴은? | 익숙함 환기 |
| 3. 구조 | 왜 그 패턴이 유지되는가? | 통찰의 전환점 |
| 4. 전제 해체 | 그게 정말 당연한가? | 반전 |
| 5. 재설계 | 사물이 제안하는 새로운 관계는? | 감동/여운 |
