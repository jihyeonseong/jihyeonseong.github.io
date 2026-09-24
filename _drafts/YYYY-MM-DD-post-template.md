---
layout: post
title: English title
title_ko: 한국어 제목    # KO 로 볼 때 제목. 없으면 title 을 그대로 쓴다
date: 2026-01-01 10:00:00+0900
description: One-line summary (shown on the blog list card)
categories: papers      # 섹션. _config.yml 의 display_categories 와 이름을 맞춘다
tags: [conformal-prediction, time-series]   # 세부 주제. 여러 개 가능
# featured: true        # 블로그 맨 위에 고정하고 싶을 때
giscus_comments: true   # 댓글. EN 이면 영어 댓글, KO 면 한국어+영어 댓글이 보인다
                        # 이모지 리액션(👍❤️🎉)도 같이 붙는다
# related_posts: false  # 글 아래 '관련 글' 을 이 글에서만 끄고 싶을 때
---

<!--
  영어·한국어를 한 파일에 쓰고, 다크모드 옆 EN/KO 토글로 보이는 쪽만 바꾼다.
  - 두 블록 모두 markdown="1" 이 있어야 안의 마크다운(제목·수식·목록)이 렌더된다.
  - 블록의 <div> 줄과 </div> 줄 앞뒤로 빈 줄을 둔다.
  - 한쪽만 쓰면 토글은 안 뜨고 그 언어로 보인다.
-->

<div class="lang-en" markdown="1">

English body. Math: $$E = mc^2$$

Citation from `_bibliography/papers.bib`: {% cite seong2024dtf %}

</div>

<div class="lang-ko" markdown="1">

한국어 본문. 수식: $$E = mc^2$$

인용: {% cite seong2024dtf %}

</div>
