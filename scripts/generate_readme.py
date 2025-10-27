#!/usr/bin/env python3
"""
Generate README.md with Tech Stack icons (from repo languages & topics)
and GitHub stats cards (github-readme-stats).
"""

import os
from collections import Counter
from github import Github

def slugify_for_simpleicons(name: str) -> str:
    s = name.lower()
    s = s.replace('++', 'plusplus').replace('+', 'plus')
    s = s.replace('#', 'sharp')
    s = s.replace('.', '').replace(' ', '')
    return s

def make_icon_html(name):
    slug = slugify_for_simpleicons(name)
    url = f"https://cdn.simpleicons.org/{slug}"
    # fallback: show text if icon isn't present (the image might 404 in some rare names)
    return f'<img src="{url}" alt="{name}" width="36" style="margin:4px;" onerror="this.style.display=\'none\'" />'

def main():
    repo_env = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required in env")

    owner = (repo_env or "").split("/")[0] or os.environ.get("GITHUB_ACTOR")
    if not owner:
        raise SystemExit("Could not determine GitHub username. Set GITHUB_REPOSITORY or GITHUB_ACTOR in env.")

    gh = Github(token)
    user = gh.get_user(owner)

    # aggregate languages and topics
    lang_counts = Counter()
    topics = set()
    for r in user.get_repos():
        try:
            if r.archived:
                continue
            langs = r.get_languages()  # returns dict like {'Python': 12345, ...}
            for l, b in langs.items():
                lang_counts[l] += b
            # get_topics requires preview but PyGithub supports it via repo.get_topics()
            try:
                for t in r.get_topics():
                    topics.add(t)
            except Exception:
                pass
        except Exception:
            # some repos may be inaccessible; skip them
            pass

    top_langs = [l for l, _ in lang_counts.most_common(20)]

    # Build tech stack HTML row
    icons_html = []
    for name in top_langs:
        icons_html.append(make_icon_html(name))
    # also include topics as possible frameworks/tools
    for t in sorted(topics):
        icons_html.append(make_icon_html(t))

    tech_stack_html = "<p>\n  " + "\n  ".join(icons_html) + "\n</p>"

    # Build README content
    readme = f"""# 👋 Hi, I'm {owner}

## 💻 Tech Stack:
{tech_stack_html}

---

## 📊 GitHub Stats:
![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username={owner}&layout=compact&theme=dark)
![GitHub Stats](https://github-readme-stats.vercel.app/api?username={owner}&show_icons=true&theme=dark)

---

*This README is automatically generated — updated weekly by a GitHub Action.*
"""

    # Write README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print("README.md generated.")

if __name__ == "__main__":
    main()
