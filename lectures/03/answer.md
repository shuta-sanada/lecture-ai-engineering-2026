# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
  - 第1回の app.ask は講座のことを知らないため、講座名を「AIエンジニア育成プログラム2026」と推測し、「レベル1〜3（入門・応用・挑戦）」という一般論をもっともらしく答えた
  - エージェントは用語集を検索してから答えたため、「基礎・実装・発展のどれか1つで完了」「原則として採点はしない」と、data/glossary.json の homework-levels の定義どおりに答えた。回答の最後に「関連する回：第1回」も付いた
- `--trace` で見えたツール呼び出し（ツール名と引数）：
  - 「LoRA とQLoRAの違いは？」：search_glossary({'query': 'LoRA'})、search_glossary({'query': 'QLoRA'}) の2回。docstring の「query には調べたい用語を1つだけ入れる」に従って、用語ごとに分けて検索していた
  - 「第2回の内容から確認問題を1問出して」：make_quiz({'lecture': 2}) の1回のみ。用語の意味を聞く質問ではないため、search_glossary は呼ばれなかった
- 1つの質問での LLM 呼び出し回数（`requests`）：
  - LoRA/QLoRA の質問は requests=2、tool_calls=2。1回目の呼び出しで2つの検索をまとめて依頼し、2回目で回答を生成したと考えられる
  - 確認問題の質問も requests=2、tool_calls=1
- 追加したツールと、docstring に書いた説明：
  - make_quiz(lecture: int) -> str。用語集から指定した回の用語を1つ選び、問題と答えを JSON 文字列で返す。該当する用語がない回は「用語集にありません」と返す
  - docstring：「指定した回（1始まりの整数）の用語から1つを選び、確認問題と答えを返す。『第2回の確認問題を出して』のように、復習用の問題を求められたときに使う。」
  - ツールは答えも返しているが、モデルは問題だけを出して答えを伏せた。INSTRUCTIONS の「宿題の答えそのものは書かず、考え方のヒントで導く」の影響ではないかと考えている

## 宿題

- 取り組んだレベル：発展（a）ADK で作り直す
- やったこと：
  - adk_agent/glossary_agent/ に agent.py と __init__.py を作成し、app/agent.py の INSTRUCTIONS と app/tools.py の3つのツール（search_glossary・get_lecture_summary・make_quiz）をそのまま ADK の Agent に渡した
  - adk run で起動し、演習と同じ3つの質問をした
- 結果：
  - 書き方の違い
    - Pydantic AI は Agent(instructions=...) を作ってから agent.tool_plain() でツールを1つずつ登録する。ADK は Agent(instruction=..., tools=[...]) とまとめて渡す
    - Pydantic AI はモデルを実行時に渡す（テストで TestModel に差し替えるため）。ADK は Agent の定義に model を直接書く
    - ADK は変数名 root_agent、フォルダと __init__.py の構成が決まっており、その規約に沿えば adk run で動く
  - 回答の違い
    - 3つの質問とも、演習とほぼ同じ内容だった（3レベルの定義、LoRA/QLoRA の違い、第2回の確認問題）。確認問題で答えを伏せる点も同じだった
    - ADK の CLI は Markdown を整形せず、** がそのまま表示された
    - ADK は1回の起動で会話が続き、セッションが .adk/session.db に保存された
  - ツールの呼ばれ方
    - adk run には --trace がないため、session.db 内のツール名を数えて確認した。search_glossary が6件、make_quiz が2件で、呼び出しと結果を1組とすると、それぞれ3回と1回呼ばれており、演習の --trace と一致した
    - ログでは、1つの質問ごとに LLM へのリクエストが2回ずつ送られていた（演習の requests=2 と同じ）
- 気づき・疑問：
  - 同じ指示とツールを渡せば、フレームワークを変えてもモデルのふるまいはほぼ変わらない。ふるまいを決めているのはフレームワークではなく、INSTRUCTIONS と docstring だと実感した
  - 一方で、何が呼ばれたかの見やすさはフレームワークで差がある。Pydantic AI は --trace で一目で分かったが、ADK の CLI ではログや保存された履歴を自分で調べる必要があった（adk web なら画面で確認できるかもしれない）
  - ADK でテスト時にモデルを差し替えるには、どう書くのがよいのか
