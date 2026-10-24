"""第1回 宿題（発展）: 応答時間とトークン数を、モデル×質問で計測する。

使い方:
    uv run python -m scripts.benchmark
結果は lectures/01/results.csv に保存される。
"""

import csv
import time
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import errors

from app.config import get_api_key

MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]

# 出力の長さが変わるように、性質の違う3問を用意する
QUESTIONS = {
    "short": "LoRAとは何か、一文で答えてください。",
    "course": "AIE2026の講座の宿題にある「3レベル」とは何ですか？",
    "long": "LoRAの仕組みを、数式も交えて詳しく説明してください。",
}

RUNS = 3  # 各組み合わせの実行回数

# 毎分の上限に当たらないよう、呼び出しの間隔（秒）をモデルごとに空ける
# flash-lite は毎分15回、3.8-flash は毎分5回が上限（スライドの実測値）
INTERVAL = {"gemini-3.5-flash-lite": 5, "gemini-3.8-flash": 15}

OUTPUT = Path("lectures/01/results.csv")
FIELDS = [
    "time", "model", "question", "run", "elapsed_sec",
    "prompt_tokens", "output_tokens", "thoughts_tokens", "total_tokens",
    "status", "error",
]


def measure(client: genai.Client, model: str, question: str) -> dict:
    """1回呼び出して、応答時間とトークン数を返す。エラーも記録する。"""
    start = time.perf_counter()
    try:
        response = client.models.generate_content(model=model, contents=question)
    except errors.APIError as e:
        elapsed = time.perf_counter() - start
        return {"elapsed_sec": round(elapsed, 2), "status": e.code, "error": e.message}

    elapsed = time.perf_counter() - start
    usage = response.usage_metadata
    return {
        "elapsed_sec": round(elapsed, 2),
        "prompt_tokens": usage.prompt_token_count if usage else None,
        "output_tokens": usage.candidates_token_count if usage else None,
        "thoughts_tokens": usage.thoughts_token_count if usage else None,
        "total_tokens": usage.total_token_count if usage else None,
        "status": 200,
        "error": "",
    }


def main() -> None:
    client = genai.Client(api_key=get_api_key())
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for model in MODELS:
            for qid, question in QUESTIONS.items():
                for run in range(1, RUNS + 1):
                    result = measure(client, model, question)
                    row = {
                        "time": datetime.now().isoformat(timespec="seconds"),
                        "model": model,
                        "question": qid,
                        "run": run,
                        **result,
                    }
                    writer.writerow(row)
                    f.flush()  # 途中で止まっても、そこまでの結果は残す
                    print(row)
                    time.sleep(INTERVAL[model])


if __name__ == "__main__":
    main()