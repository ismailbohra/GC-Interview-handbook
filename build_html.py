"""
Convert interview_questions.md into a beautiful self-contained HTML page.
Uses markdown + Pygments for syntax highlighting.
"""

import html as html_module
import re

MD_PATH = "interview_questions.md"
HTML_PATH = "index.html"


def parse_md(text: str) -> str:
    """Convert markdown to HTML with code highlighting."""
    lines = text.split("\n")
    out = []
    in_code = False
    code_lang = ""
    code_buf = []
    section_id = 0
    question_id = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code fence
        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_lang = line[3:].strip() or "text"
                code_buf = []
            else:
                code_text = html_module.escape("\n".join(code_buf))
                out.append(
                    f'<div class="code-block">'
                    f'<div class="code-header"><span class="code-lang">{html_module.escape(code_lang)}</span>'
                    f'<button class="copy-btn" onclick="copyCode(this)">Copy</button></div>'
                    f'<pre><code class="language-{html_module.escape(code_lang)}">{code_text}</code></pre></div>'
                )
                in_code = False
                code_lang = ""
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Title
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            out.append(f'<h1 class="main-title">{html_module.escape(title)}</h1>')
            i += 1
            continue

        # Section heading
        if line.startswith("## "):
            section_id += 1
            title = line[3:].strip()
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            out.append(
                f'<section class="topic-section" id="section-{slug}">'
                f'<h2 class="section-title" data-section="{section_id}">'
                f'<span class="section-number">{section_id:02d}</span>{html_module.escape(title)}</h2>'
            )
            i += 1
            continue

        # Question heading
        if line.startswith("### Question:"):
            question_id += 1
            title = line[len("### Question:") :].strip()
            out.append(
                f'<div class="question-card" id="q-{question_id}">'
                f'<div class="question-header" onclick="toggleAnswer(this)">'
                f'<h3><span class="q-number">Q{question_id}</span>{html_module.escape(title)}</h3>'
                f'<span class="toggle-icon">▼</span></div>'
                f'<div class="answer-body">'
            )
            i += 1
            continue

        # "Answer:" label
        if line.strip() == "Answer:":
            i += 1
            continue

        # Blank line
        if line.strip() == "":
            i += 1
            continue

        # Inline formatting
        processed = process_inline(line)
        out.append(f"<p>{processed}</p>")
        i += 1

    # Close any open question cards
    body = "\n".join(out)
    # Each question card needs closing </div></div>
    # We'll handle this with a post-processing pass
    return body, question_id, section_id


def process_inline(text: str) -> str:
    """Handle inline markdown: bold, italic, code, links, math."""
    text = html_module.escape(text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r'<code class="inline-code">\1</code>', text)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    # $math$
    text = re.sub(r"\$([^$]+)\$", r'<span class="math">\1</span>', text)
    return text


def build_sidebar(md_text: str) -> str:
    """Build sidebar navigation from sections."""
    sections = re.findall(r"^## (.+)$", md_text, re.MULTILINE)
    items = []
    for idx, title in enumerate(sections, 1):
        # Skip headings that are inside code blocks (Prerequisites, Setup, Run, Test)
        if title.strip() in ("Prerequisites", "Setup", "Run", "Test"):
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        items.append(
            f'<a href="#section-{slug}" class="nav-item" data-section="{idx}">'
            f'<span class="nav-number">{idx:02d}</span>'
            f'<span class="nav-text">{html_module.escape(title)}</span></a>'
        )
    return "\n".join(items)


def build_html(md_text: str) -> str:
    body_content, total_q, total_s = parse_md(md_text)
    sidebar = build_sidebar(md_text)

    # Post-process: close question cards properly
    # Strategy: every time we see a new question-card or section or end, close previous
    final_lines = []
    open_cards = 0
    open_sections = 0
    for line in body_content.split("\n"):
        # Close previous card before a new one or a new section
        if (
            'class="question-card"' in line or 'class="topic-section"' in line
        ) and open_cards > 0:
            final_lines.append("</div></div>")  # close answer-body + question-card
            open_cards -= 1
        if 'class="topic-section"' in line and open_sections > 0:
            final_lines.append("</section>")
            open_sections -= 1

        final_lines.append(line)

        if 'class="question-card"' in line:
            open_cards += 1
        if 'class="topic-section"' in line:
            open_sections += 1

    # Close any remaining
    if open_cards > 0:
        final_lines.append("</div></div>")
    if open_sections > 0:
        final_lines.append("</section>")

    body_html = "\n".join(final_lines)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Python Core GC-Interview Handbook</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/sql.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/dockerfile.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/json.min.js"></script>
<style>
:root {{
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: #1c2128;
    --bg-code: #0d1117;
    --bg-sidebar: #0d1117;
    --border: #30363d;
    --border-highlight: #58a6ff;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --text-muted: #6e7681;
    --accent: #58a6ff;
    --accent-green: #3fb950;
    --accent-purple: #bc8cff;
    --accent-orange: #d29922;
    --accent-red: #f85149;
    --accent-gradient: linear-gradient(135deg, #58a6ff 0%, #bc8cff 100%);
    --shadow: 0 8px 24px rgba(0,0,0,0.4);
    --radius: 12px;
    --sidebar-width: 280px;
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
    scroll-padding-top: 20px;
}}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.7;
    font-size: 15px;
}}

/* Sidebar */
.sidebar {{
    position: fixed;
    left: 0;
    top: 0;
    width: var(--sidebar-width);
    height: 100vh;
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    z-index: 100;
    padding: 20px 0;
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
}}

.sidebar-header {{
    padding: 10px 20px 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 10px;
}}

.sidebar-header h2 {{
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.sidebar-header .stats {{
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 8px;
}}

.nav-item {{
    display: flex;
    align-items: center;
    padding: 10px 20px;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.2s;
    border-left: 3px solid transparent;
}}

.nav-item:hover {{
    color: var(--text-primary);
    background: var(--bg-secondary);
    border-left-color: var(--accent);
}}

.nav-item.active {{
    color: var(--accent);
    background: rgba(88, 166, 255, 0.08);
    border-left-color: var(--accent);
}}

.nav-number {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-muted);
    margin-right: 12px;
    min-width: 24px;
}}

.nav-text {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* Main content */
.main-content {{
    margin-left: var(--sidebar-width);
    max-width: 900px;
    padding: 40px 50px 100px;
}}

.main-title {{
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 8px;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.main-title + p {{
    color: var(--text-secondary);
    font-size: 16px;
    margin-bottom: 40px;
    line-height: 1.6;
}}

/* Sections */
.topic-section {{
    margin-bottom: 50px;
}}

.section-title {{
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
    padding-bottom: 12px;
    margin-bottom: 24px;
    border-bottom: 2px solid var(--border);
    display: flex;
    align-items: center;
    gap: 14px;
}}

.section-number {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    color: var(--bg-primary);
    background: var(--accent-gradient);
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 600;
}}

/* Question cards */
.question-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 16px;
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
}}

.question-card:hover {{
    border-color: var(--border-highlight);
    box-shadow: 0 4px 16px rgba(88, 166, 255, 0.06);
}}

.question-header {{
    padding: 18px 24px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    user-select: none;
    transition: background 0.15s;
}}

.question-header:hover {{
    background: rgba(88, 166, 255, 0.04);
}}

.question-header h3 {{
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
    line-height: 1.5;
}}

.q-number {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--accent);
    background: rgba(88, 166, 255, 0.1);
    padding: 3px 8px;
    border-radius: 5px;
    font-weight: 600;
    white-space: nowrap;
    flex-shrink: 0;
}}

.toggle-icon {{
    color: var(--text-muted);
    font-size: 12px;
    transition: transform 0.3s;
    flex-shrink: 0;
    margin-left: 12px;
}}

.question-card.collapsed .toggle-icon {{
    transform: rotate(-90deg);
}}

.question-card.collapsed .answer-body {{
    display: none;
}}

.answer-body {{
    padding: 0 24px 24px;
    border-top: 1px solid var(--border);
}}

.answer-body p {{
    margin-top: 16px;
    color: var(--text-secondary);
    line-height: 1.8;
}}

.answer-body p:first-child {{
    margin-top: 20px;
}}

/* Code blocks */
.code-block {{
    margin: 16px 0;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: var(--bg-code);
}}

.code-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
}}

.code-lang {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
}}

.copy-btn {{
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: var(--text-muted);
    background: transparent;
    border: 1px solid var(--border);
    padding: 3px 10px;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
}}

.copy-btn:hover {{
    color: var(--accent);
    border-color: var(--accent);
}}

.copy-btn.copied {{
    color: var(--accent-green);
    border-color: var(--accent-green);
}}

pre {{
    margin: 0;
    padding: 16px;
    overflow-x: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
}}

pre code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    line-height: 1.6;
    tab-size: 4;
}}

/* Inline code */
.inline-code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88em;
    background: rgba(88, 166, 255, 0.1);
    color: var(--accent);
    padding: 2px 7px;
    border-radius: 5px;
    border: 1px solid rgba(88, 166, 255, 0.15);
}}

/* Math */
.math {{
    font-family: 'JetBrains Mono', monospace;
    font-style: italic;
    color: var(--accent-purple);
    font-size: 0.95em;
}}

/* Strong */
strong {{
    color: var(--text-primary);
    font-weight: 600;
}}

/* Top bar */
.top-bar {{
    position: sticky;
    top: 0;
    z-index: 50;
    background: rgba(13, 17, 23, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    padding: 12px 50px;
    margin-left: var(--sidebar-width);
    display: flex;
    align-items: center;
    gap: 16px;
}}

.search-box {{
    flex: 1;
    max-width: 480px;
    position: relative;
}}

.search-box input {{
    width: 100%;
    padding: 9px 14px 9px 38px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    outline: none;
    transition: border-color 0.2s;
}}

.search-box input:focus {{
    border-color: var(--accent);
}}

.search-box::before {{
    content: '🔍';
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 14px;
    pointer-events: none;
}}

.toolbar-actions {{
    display: flex;
    gap: 8px;
}}

.tool-btn {{
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: var(--text-secondary);
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    padding: 8px 14px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
    white-space: nowrap;
}}

.tool-btn:hover {{
    color: var(--text-primary);
    border-color: var(--accent);
}}

/* Progress indicator */
.progress-bar {{
    position: fixed;
    top: 0;
    left: var(--sidebar-width);
    right: 0;
    height: 3px;
    z-index: 200;
    background: var(--bg-secondary);
}}

.progress-fill {{
    height: 100%;
    background: var(--accent-gradient);
    width: 0%;
    transition: width 0.2s;
}}

/* Scroll to top */
.scroll-top {{
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: var(--accent);
    color: #fff;
    border: none;
    cursor: pointer;
    font-size: 18px;
    display: none;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow);
    transition: transform 0.2s, opacity 0.2s;
    z-index: 100;
}}

.scroll-top:hover {{
    transform: scale(1.1);
}}

/* Mobile */
.menu-toggle {{
    display: none;
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 200;
    width: 40px;
    height: 40px;
    border-radius: 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    color: var(--text-primary);
    font-size: 18px;
    cursor: pointer;
    align-items: center;
    justify-content: center;
}}

/* Sidebar overlay backdrop */
.sidebar-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    z-index: 99;
}}

.sidebar-overlay.active {{
    display: block;
}}

/* Tablet */
@media (max-width: 1100px) {{
    .main-content {{
        padding: 30px 30px 80px;
    }}
}}

/* Mobile */
@media (max-width: 900px) {{
    .sidebar {{
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        width: 280px;
        box-shadow: 4px 0 24px rgba(0,0,0,0.5);
    }}
    .sidebar.open {{
        transform: translateX(0);
    }}
    .main-content, .top-bar {{
        margin-left: 0;
    }}
    .progress-bar {{
        left: 0;
    }}
    .main-content {{
        padding: 24px 16px 80px;
    }}
    .top-bar {{
        padding: 10px 16px;
        padding-left: 58px;
        gap: 8px;
        flex-wrap: wrap;
    }}
    .menu-toggle {{
        display: flex;
    }}
    .search-box {{
        flex: 1 1 100%;
        max-width: 100%;
        order: 1;
    }}
    .toolbar-actions {{
        gap: 6px;
        order: 2;
        flex: 1 1 100%;
    }}
    .tool-btn {{
        padding: 6px 12px;
        font-size: 11px;
        flex: 1;
        text-align: center;
    }}
    .main-title {{
        font-size: 24px;
    }}
    .section-title {{
        font-size: 20px;
        gap: 10px;
    }}
    .section-number {{
        font-size: 12px;
        padding: 3px 8px;
    }}
    .question-header {{
        padding: 14px 16px;
    }}
    .question-header h3 {{
        font-size: 14px;
        gap: 8px;
    }}
    .answer-body {{
        padding: 0 16px 16px;
    }}
    .code-block {{
        border-radius: 8px;
        margin: 12px -8px;
    }}
    pre {{
        padding: 12px;
        font-size: 12px;
    }}
    pre code {{
        font-size: 12px;
        white-space: pre;
        word-break: normal;
        overflow-wrap: normal;
    }}
    .search-box input {{
        font-size: 14px;
        padding: 8px 12px 8px 36px;
    }}
    .scroll-top {{
        bottom: 20px;
        right: 16px;
        width: 40px;
        height: 40px;
        font-size: 16px;
    }}
    .inline-code {{
        font-size: 0.82em;
        word-break: break-word;
    }}
    .topic-section {{
        margin-bottom: 32px;
    }}
}}

/* Small phones */
@media (max-width: 480px) {{
    .main-content {{
        padding: 16px 12px 80px;
    }}
    .top-bar {{
        padding: 8px 12px;
        padding-left: 54px;
    }}
    .main-title {{
        font-size: 20px;
    }}
    .section-title {{
        font-size: 18px;
        flex-wrap: wrap;
    }}
    .question-header {{
        padding: 12px 14px;
    }}
    .question-header h3 {{
        font-size: 13px;
    }}
    .answer-body p {{
        font-size: 14px;
        line-height: 1.7;
    }}
    .code-block {{
        margin: 10px -6px;
    }}
    pre {{
        padding: 10px;
    }}
    pre code {{
        font-size: 11px;
    }}
    .search-box input {{
        font-size: 14px;
    }}
    .tool-btn {{
        padding: 6px 8px;
        font-size: 10px;
    }}
}}
</style>
</head>
<body>

<div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>

<button class="menu-toggle" id="menuToggle" onclick="toggleSidebar()">☰</button>
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<nav class="sidebar" id="sidebar">
    <div class="sidebar-header">
        <h2>Interview GC-Interview Handbook</h2>
        <div class="stats">{total_q} Questions · {total_s} Topics</div>
    </div>
    {sidebar}
</nav>

<div class="top-bar">
    <div class="search-box">
        <input type="text" id="searchInput" placeholder="Search questions... (Ctrl+K)" autocomplete="off">
    </div>
    <div class="toolbar-actions">
        <button class="tool-btn" onclick="expandAll()">Expand All</button>
        <button class="tool-btn" onclick="collapseAll()">Collapse All</button>
    </div>
</div>

<main class="main-content" id="content">
{body_html}
</main>

<button class="scroll-top" id="scrollTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

<script>
hljs.highlightAll();

// Toggle answer
function toggleAnswer(el) {{
    el.closest('.question-card').classList.toggle('collapsed');
}}

// Copy code
function copyCode(btn) {{
    const code = btn.closest('.code-block').querySelector('code').textContent;
    navigator.clipboard.writeText(code).then(() => {{
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => {{
            btn.textContent = 'Copy';
            btn.classList.remove('copied');
        }}, 2000);
    }});
}}

// Expand / Collapse all
function expandAll() {{
    document.querySelectorAll('.question-card').forEach(c => c.classList.remove('collapsed'));
}}
function collapseAll() {{
    document.querySelectorAll('.question-card').forEach(c => c.classList.add('collapsed'));
}}

// Search
const searchInput = document.getElementById('searchInput');
searchInput.addEventListener('input', function() {{
    const query = this.value.toLowerCase();
    document.querySelectorAll('.question-card').forEach(card => {{
        const text = card.textContent.toLowerCase();
        if (query === '' || text.includes(query)) {{
            card.style.display = '';
            if (query) card.classList.remove('collapsed');
        }} else {{
            card.style.display = 'none';
        }}
    }});
}});

// Ctrl+K shortcut
document.addEventListener('keydown', function(e) {{
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
    }}
    if (e.key === 'Escape') {{
        searchInput.blur();
        searchInput.value = '';
        searchInput.dispatchEvent(new Event('input'));
    }}
}});

// Scroll progress
window.addEventListener('scroll', function() {{
    const scrolled = window.scrollY;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const pct = total > 0 ? (scrolled / total) * 100 : 0;
    document.getElementById('progressFill').style.width = pct + '%';

    const btn = document.getElementById('scrollTop');
    btn.style.display = scrolled > 500 ? 'flex' : 'none';
}});

// Active sidebar item
const observer = new IntersectionObserver(entries => {{
    entries.forEach(entry => {{
        if (entry.isIntersecting) {{
            const id = entry.target.id;
            document.querySelectorAll('.nav-item').forEach(a => {{
                a.classList.toggle('active', a.getAttribute('href') === '#' + id);
            }});
        }}
    }});
}}, {{ rootMargin: '-20% 0px -70% 0px' }});

document.querySelectorAll('.topic-section').forEach(s => observer.observe(s));

// Toggle mobile sidebar
function toggleSidebar() {{
    document.querySelector('.sidebar').classList.toggle('open');
    document.getElementById('sidebarOverlay').classList.toggle('active');
    document.body.style.overflow = document.querySelector('.sidebar').classList.contains('open') ? 'hidden' : '';
}}

// Close mobile sidebar on nav click
document.querySelectorAll('.nav-item').forEach(a => {{
    a.addEventListener('click', () => {{
        document.querySelector('.sidebar').classList.remove('open');
        document.getElementById('sidebarOverlay').classList.remove('active');
        document.body.style.overflow = '';
    }});
}});
</script>
</body>
</html>"""


def main():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_output = build_html(md_text)

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"Generated {HTML_PATH} successfully!")
    print(f"File size: {len(html_output):,} bytes")


if __name__ == "__main__":
    main()
