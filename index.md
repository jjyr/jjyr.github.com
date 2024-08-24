---
layout: page
title: Articles
---

<section>
  {% if site.posts[0] %}

    {%for post in site.posts %}
        <li class="posts">
          <time>{{ post.date | date: '%Y/%m/%d' }}</time>
          <a class="post-link" href="{{ post.url | prepend: site.baseurl | replace: '//', '/' }}">
            {{ post.title }}
          </a>
        </li>
    {% endfor %}

  {% endif %}
</section>
