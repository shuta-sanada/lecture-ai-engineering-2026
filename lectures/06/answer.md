# 第6回 解答

## 演習

- STEP 1 のツールの名前：glossary_search_glossary
- STEP 2 の [tool call]：glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：
  - aws_aws___search_documentation({'topics': ['general'], 'search_phrase': 'Amazon S3 バージョニング 概要'})
  - aws_aws___search_documentation({'search_phrase': 'What is versioning in Amazon S3', 'topics': ['general']})
- 気づき・疑問：
  - 第5回までのエージェントと第6回のエージェントで、ツールの表示はどちらも「名前・説明文・引数」の形だった。ツールが手元の関数か MCP サーバーかは、モデルからは区別できない。
  - STEP 3 では、app/mcp_servers.json に書き足すだけで、コードを変えずにツールが増えた。fetch はページを読む前に robots.txt を確認しており、自動取得を断るサイトを読まない既定の動作が働いていた。
  - fetch_fetch の説明文には「このツールでインターネットに接続できるようになった」とあり、説明文がモデルのふるまいを変える指示として働く。出所の分からないサーバーを足すと、説明文でモデルを誘導されるおそれがあると考えた。
  - STEP 4 では、日本語の検索語で関係の薄い結果が返り、モデルが英語で検索し直して S3 の FAQ にたどり着いた。検索語しだいで結果が変わる点は第5回と同じだった。
  - 使えるツールが1個（STEP 2）、2個（STEP 3）、7個（STEP 4）と増えるにつれ、入力トークンは715、2,230、11,339と増えた。使わないツールの説明文も毎回モデルに渡されるため、サーバーを足すほど質問ごとの負担が大きくなる。

## 宿題

- 取り組んだレベル：発展
- やったこと：
  - 普段最もよく使う Claude Code を選び、MCP サーバーの設定方法を公式ドキュメントで調べ、演習の app/mcp_servers.json と比べた。
  - 調べた日付：2026年11月28日
  - 参照したドキュメント：https://code.claude.com/docs/en/mcp-quickstart 、https://code.claude.com/docs/en/mcp-configuration
- 結果：
  - 設定を書く場所：
    - Claude Code には有効範囲（スコープ）が3つあり、置き場所が異なる。local（既定。自分だけ・そのプロジェクトだけ）は ~/.claude.json のプロジェクトの項目、project（リポジトリを複製した全員）はプロジェクト直下の .mcp.json、user（自分だけ・全プロジェクト）は ~/.claude.json の最上位の mcpServers に保存される。
    - ファイルを手で書く方法のほか、`claude mcp add` コマンドで登録できる。`--scope project` や `--scope user` で範囲を選ぶ。
    - 演習では、エージェントが app/mcp_servers.json という1つのファイルだけを読んでいた。
  - コマンドで起動する書き方（演習の "command" にあたる部分）：
    - JSON では、演習と同じく mcpServers の下にサーバー名を置き、command と args を書く。Claude Code の例では "type": "stdio" も明記している。
    - コマンドでは `claude mcp add playwright -- npx -y @playwright/mcp@latest` のように、`--` のあとに起動するコマンドを書く。
  - URL で接続する書き方（演習の "url" にあたる部分）：
    - JSON では "type": "http" と "url" を書く。url があって type がない項目は設定エラーになる。type のない項目は、コマンドで起動するサーバーとして読まれるためである。
    - コマンドでは `claude mcp add --transport http 名前 URL` と書く。
    - 演習の aws の書き方（{"url": "..."} のみ）は、そのままでは Claude Code で動かない。
  - 有効になる範囲：
    - 演習の設定は、この講座のリポジトリのエージェントだけで有効だった。
    - Claude Code では、上記の3つのスコープから選べる。.mcp.json をリポジトリに commit すれば、チームで同じサーバーを共有できる。
  - 演習の app/mcp_servers.json との比較

    | 観点 | 演習（app/mcp_servers.json） | Claude Code |
    |---|---|---|
    | 置き場所 | app/mcp_servers.json の1つ | ~/.claude.json または .mcp.json |
    | 有効範囲 | このリポジトリのエージェントのみ | local／project／user から選ぶ |
    | コマンドで起動 | command と args | command と args（"type": "stdio" も書ける） |
    | URL で接続 | url のみ | "type": "http" と url（type がないとエラー） |
    | 登録の方法 | ファイルを手で書く | ファイルを書くか、claude mcp add |
    | 起動前の確認 | なし（書かれたものをそのまま起動） | project スコープのサーバーは初回に承認が必要 |

- 気づき・疑問：
  - 基本の形（mcpServers の下にサーバー名、command と args、または url）は共通で、演習で学んだ設定の読み方がそのまま通用した。一方で、URL の書き方のように細かな違いがあり、別のツールに設定を移すときは公式ドキュメントで確認する必要がある。
  - Claude Code は、project スコープのサーバーを初めて使うときに承認を求める。複製したリポジトリが、本人の同意なしに手元でプロセスを起動するのを防ぐためである。演習のエージェントは設定ファイルに書かれたものを確認なしで起動しており、スライドの「既製の外部ツールを足す前に確認する」を、Claude Code は仕組みとして組み込んでいると分かった。
  - Claude Code のドキュメントにも、接続したサーバーのツール名と指示が毎回のセッションに読み込まれ、コンテキストを消費するため、使わないサーバーは外すとよいとあった。演習で、ツールが7個に増えると入力トークンが11,339になった現象と一致する。
  - 今回はドキュメントで調べただけで、Claude Code で実際に設定を試してはいない。演習の aws の書き方が本当にエラーになるかは、実際に試して確かめたい。