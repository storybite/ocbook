# 책 원고 형식 (bookbot)

엔진의 빌드, 챗봇 색인, 블록 클릭, 책 수정이 모두 이 형식에 기대고 있습니다. 새 책도 이대로 씁니다. `python -m bookbot new`가 만드는 `src/ch01.html`이 최소 예입니다.

## 파일
- 장 하나 = `src/chNN.html` 한 파일. `NN`은 두 자리 숫자이고, 빌드는 파일 이름 순서로 이어 붙입니다. 부록도 `ch19.html`, `ch20.html`처럼 번호를 이어 씁니다.
- `_`로 시작하는 파일(예: `src/_table.html`)은 장이 아닙니다. `book.toml`의 `[build.includes]`로 장 본문 안의 자리표시를 바꿀 때 씁니다.

## 장과 절
```html
<section class="chapter" id="ch03">
<h1><span class="num">3장</span> 장 제목</h1>
<p class="lead">장 소개 한두 문장 (장 머리말)</p>

<h2 id="ch03-1">3.1 절 제목</h2>
… 블록들 …
<h2 id="ch03-2">3.2 절 제목</h2>
…
</section>
```
- 장은 `<section class="chapter" id="chNN">`이고, 그 안의 첫 `<h1>`이 장 제목입니다.
- 절은 따로 감싸지 않습니다. `<h2 id="chNN-M">`부터 다음 `<h2>` 앞까지가 한 절입니다. 첫 `<h2>` 앞은 장 머리말입니다.
- `id`는 책 전체에서 한 번만 씁니다. 빌드가 중복을 찾으면 실패합니다. 기존 `id`는 링크(`#ch03-2`)가 걸리므로 바꾸지 않습니다.
- 소절은 `<h3>`를 씁니다(색인의 단위는 `<h2>` 절입니다).

## 블록
| 블록 | 형식 |
|---|---|
| 문단 | `<p>` — 강조 `<b>`, 인라인 코드 `<code>` |
| 목록·표 | `<ul>`/`<ol>`, `<table>` |
| 코드 | `<pre><code><span class="src">파일 경로 — 설명</span>코드…</code></pre>` |
| 상자 | `<div class="box why|warn|note|use"><b>제목</b>…</div>` (why 설계 이유, warn 주의, note 참고, use 사용법) |
| 그림 | `<div class="mermaid">flowchart LR …</div>` 다음 `<p class="cap">그림 N-M 설명</p>` |

- 코드와 글 안의 `<`, `>`, `&`는 `&lt;` `&gt;` `&amp;`로 씁니다.
- 원고에 `<script>`, `on…=` 이벤트 속성, `<iframe>`·`<link>`·`<style>` 같은 외부 리소스 태그를 넣지 않습니다. 채팅 수정은 이런 수정을 거절합니다.
- 장 사이 링크는 `<a href="#ch05-3">5.3 …</a>`처럼 절 `id`로 겁니다.
