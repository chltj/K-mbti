from dataclasses import dataclass
from typing import Dict, Any, List
import re
from collections import Counter


@dataclass
class StyleResult:
    text: str
    char_count: int
    token_count: int
    sentence_count: int
    avg_sentence_length: float
    style_scores: Dict[str, float]
    mbti_result: str
    mbti_axis_percent: Dict[str, Dict[str, float]]
    comments: List[str]


def normalize_text(text: str) -> str:
    return text.strip()


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r"[.!?。\n]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def tokenize(text: str) -> List[str]:
    return text.split()


LEXICON = {
    "E": ["같이", "여러분", "ㅋㅋ", "ㅎㅎ", "재밌", "만나", "축구", "술", "사람들"],
    "I": ["혼자", "집", "조용", "생각", "책", "내향", "혼밥", "방구석"],
    "S": ["사실", "구체", "현실", "데이터", "수치", "경험적으로"],
    "N": ["아이디어", "영감", "가능성", "미래", "상상", "컨셉"],
    "T": ["논리", "효율", "합리", "분석", "객관", "결론"],
    "F": ["감정", "공감", "기분", "따뜻", "기억", "마음", "사랑"],
    "J": ["계획", "마감", "정리", "목표", "루틴", "체계", "일정"],
    "P": ["즉흥", "대충", "나중에", "유연", "자유", "그때그때"],
}

AXES = [("E", "I"), ("S", "N"), ("T", "F"), ("J", "P")]


def compute_style_scores(tokens: List[str]) -> Dict[str, float]:
    token_counts = Counter(tokens)
    scores = {k: 0.0 for k in LEXICON.keys()}

    for trait, words in LEXICON.items():
        for w in words:
            scores[trait] += token_counts.get(w, 0)

    return scores


def scores_to_axis_percent(scores: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    axis_percent = {}
    for a, b in AXES:
        a_score = scores.get(a, 0.0)
        b_score = scores.get(b, 0.0)
        total = a_score + b_score

        if total == 0:
            axis_percent[f"{a}{b}"] = {a: 50.0, b: 50.0}
        else:
            axis_percent[f"{a}{b}"] = {
                a: round(a_score / total * 100, 1),
                b: round(b_score / total * 100, 1),
            }

    return axis_percent


def axis_to_mbti(axis_percent: Dict[str, Dict[str, float]]) -> str:
    result_letters = []
    for axis in ["EI", "SN", "TF", "JP"]:
        a = axis[0]
        b = axis[1]
        pa = axis_percent[axis][a]
        pb = axis_percent[axis][b]
        result_letters.append(a if pa >= pb else b)
    return "".join(result_letters)


def generate_comments(axis_percent: Dict[str, Dict[str, float]]) -> list:
    comments = []
    ei = axis_percent["EI"]
    if ei["E"] > 60:
        comments.append("사교적이고 외향적인 표현이 많습니다.")
    elif ei["I"] > 60:
        comments.append("혼자만의 시간과 생각을 중시하는 말투입니다.")

    sn = axis_percent["SN"]
    if sn["S"] > 60:
        comments.append("구체적이고 사실 기반의 표현이 많습니다.")
    elif sn["N"] > 60:
        comments.append("아이디어와 가능성 중심의 말투가 돋보입니다.")

    tf = axis_percent["TF"]
    if tf["T"] > 60:
        comments.append("논리적이고 분석적인 표현이 강합니다.")
    elif tf["F"] > 60:
        comments.append("감정 중심적이고 공감적인 표현이 많습니다.")

    jp = axis_percent["JP"]
    if jp["J"] > 60:
        comments.append("체계적이고 계획적인 성향이 드러납니다.")
    elif jp["P"] > 60:
        comments.append("즉흥적이고 유연한 성향이 느껴집니다.")

    if not comments:
        comments.append("전체적으로 균형 잡힌 말투입니다.")

    return comments


def analyze_style(text: str) -> Dict[str, Any]:
    norm_text = normalize_text(text)
    sentences = split_sentences(norm_text)
    tokens = tokenize(norm_text)

    char_count = len(norm_text)
    token_count = len(tokens)
    sentence_count = len(sentences)
    avg_sentence_length = round(token_count / sentence_count, 2) if sentence_count else 0.0

    style_scores = compute_style_scores(tokens)

    return {
        "text": norm_text,
        "char_count": char_count,
        "token_count": token_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "style_scores": style_scores,
        "tokens": tokens,
        "sentences": sentences,
    }


def estimate_mbti(analysis: Dict[str, Any]) -> StyleResult:
    style_scores = analysis["style_scores"]
    axis_percent = scores_to_axis_percent(style_scores)
    mbti = axis_to_mbti(axis_percent)
    comments = generate_comments(axis_percent)

    return StyleResult(
        text=analysis["text"],
        char_count=analysis["char_count"],
        token_count=analysis["token_count"],
        sentence_count=analysis["sentence_count"],
        avg_sentence_length=analysis["avg_sentence_length"],
        style_scores=style_scores,
        mbti_result=mbti,
        mbti_axis_percent=axis_percent,
        comments=comments,
    )


if __name__ == "__main__":
    sample = "오늘은 친구들과 함께 축구하고 맥주 마셨는데 너무 즐거웠어!"
    a = analyze_style(sample)
    r = estimate_mbti(a)
    print(r)
