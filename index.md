---
layout: page
title: Articles
---

<section>
  <div class="lang-tags"><a class="lang-tag" href="/tags/中文/">#中文</a> / <a class="lang-tag" href="/tags/english/">#English</a></div>
  {%for post in site.posts %}
      <li class="posts">
        <time>{{ post.date | date: '%Y/%m/%d' }}</time>
        <a class="post-link" href="{{ post.url | prepend: site.baseurl | replace: '//', '/' }}">
          {{ post.title }}
        </a>
      </li>
  {% endfor %}
</section>
