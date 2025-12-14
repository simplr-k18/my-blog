import os
import re
import sys
from datetime import datetime
from pathlib import Path

# --- Configuration ---
ARTICLES_DIR = "articles"
INDEX_FILE = "index.html"

# --- Dependency Check ---
try:
    import docx
    import fitz  # PyMuPDF
except ImportError:
    print("Error: Missing libraries. Please run: pip install python-docx PyMuPDF")
    sys.exit(1)

def clean_text(text):
    """Cleans up text artifacts and whitespace."""
    text = text.replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_list_item(text):
    """Checks if text starts with a bullet point marker."""
    # Matches: •, ●, -, *, 1., etc at start of line
    return re.match(r'^[\u2022\u25cf\-\*●]\s', text) or re.match(r'^\d+\.\s', text)

def process_pdf(filepath):
    """Advanced PDF extraction using visual blocks."""
    doc = fitz.open(filepath)
    structured_content = []
    
    for page in doc:
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: b[1]) # Sort vertically
        
        for b in blocks:
            text = clean_text(b[4])
            if not text:
                continue
            
            # Identify type
            if is_list_item(text):
                # Clean the bullet point
                text = re.sub(r'^[\u2022\u25cf\-\*●]\s*', '', text)
                structured_content.append({'type': 'list_item', 'text': text})
            elif re.match(r'^(\d+\.|[IVX]+\.)\s', text) or (len(text) < 60 and not text.endswith('.')):
                # Header detection: Numbered or Short & No Period
                level = 'h2' if len(text) < 40 else 'h3'
                structured_content.append({'type': level, 'text': text})
            else:
                structured_content.append({'type': 'p', 'text': text})
                
    return structured_content

def process_docx(filepath):
    """Process DOCX with style awareness."""
    doc = docx.Document(filepath)
    structured_content = []
    
    for p in doc.paragraphs:
        text = clean_text(p.text)
        if not text:
            continue
            
        if p.style.name.startswith('Heading'):
            level = 'h2' if '1' in p.style.name else 'h3'
            structured_content.append({'type': level, 'text': text})
        elif p.style.name.startswith('List') or is_list_item(text):
            text = re.sub(r'^[\u2022\u25cf\-\*●]\s*', '', text)
            structured_content.append({'type': 'list_item', 'text': text})
        else:
            structured_content.append({'type': 'p', 'text': text})
                
    return structured_content

def process_txt(filepath):
    """Process TXT file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    structured_content = []
    
    for line in lines:
        text = clean_text(line)
        if not text:
            continue
            
        if is_list_item(text):
            text = re.sub(r'^[\u2022\u25cf\-\*●]\s*', '', text)
            structured_content.append({'type': 'list_item', 'text': text})
        elif len(text) < 60 and not text.endswith('.'):
             structured_content.append({'type': 'h2', 'text': text})
        else:
            structured_content.append({'type': 'p', 'text': text})
            
    return structured_content

def generate_html_body(structured_data):
    """Converts structured data into HTML tags with smart list grouping."""
    html_output = ""
    toc_items = []
    excerpt = ""
    
    in_list = False
    
    for item in structured_data:
        # Capture first paragraph as excerpt
        if not excerpt and item['type'] == 'p':
            excerpt = item['text']

        # Handle List Grouping
        if item['type'] == 'list_item':
            if not in_list:
                html_output += "<ul>\n"
                in_list = True
            html_output += f"    <li>{item['text']}</li>\n"
            continue
        elif in_list:
            html_output += "</ul>\n"
            in_list = False
            
        # Handle Headings
        if item['type'] in ['h2', 'h3']:
            anchor_id = re.sub(r'[^a-z0-9-]', '', item['text'].lower().replace(' ', '-'))
            html_output += f'<{item["type"]} id="{anchor_id}">{item["text"]}</{item["type"]}>\n'
            
            if len(item['text']) > 3:
                toc_items.append(f'<li><a href="#{anchor_id}">{item["text"]}</a></li>')
        else:
            # Simple formatting
            text = item['text']
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            html_output += f'<p>{text}</p>\n'
            
    if in_list:
        html_output += "</ul>\n"
        
    return html_output, "\n".join(toc_items), excerpt

def create_full_html(title, body_content, toc_content, date_str):
    """Generates the Article HTML file."""
    
    # CSS Fix: Sidebar position changed from 'top: 50vh' to 'top: 120px' to prevent jitter
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

    <style>
        :root {{
            --bg-color: #FAFAFA;
            --surface: #FFFFFF;
            --text-main: #202020;
            --text-muted: #737373;
            --border: #E5E5E5;
            --text-secondary: #555;
            --accent: #333;
            --radius: 12px;
            --easing: cubic-bezier(0.2, 0.8, 0.2, 1);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}

        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
        }}

        .page-layout {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 60px;
            max-width: 1200px;
            margin: 0 auto;
            padding: 80px 24px;
            position: relative;
        }}

        .main-content {{
            max-width: 800px;
            width: 100%;
        }}

        .back-link {{
            position: fixed;
            top: 24px;
            left: calc(max(24px, 50% - 600px + 24px));
            z-index: 100;
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--text-main);
            text-decoration: none;
            font-size: 0.9rem;
            padding: 10px 16px;
            border-radius: 100px;
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.6);
            transition: all 0.3s var(--easing);
        }}
        .back-link:hover {{
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
            transform: translateY(-2px);
        }}

        .article-header h1 {{
            font-family: 'Fraunces', serif;
            font-size: 3.5rem;
            font-weight: 400;
            line-height: 1.2;
            letter-spacing: -0.03em;
            margin-bottom: 16px;
        }}

        .article-header .date {{
            color: var(--text-muted);
            margin-bottom: 60px;
        }}

        article {{
            font-size: 1.1rem;
            color: var(--text-main);
        }}

        article p {{ margin-bottom: 1.5em; }}
        article ul {{ margin-bottom: 1.5em; padding-left: 1.5em; }}
        article li {{ margin-bottom: 0.5em; padding-left: 0.5em; }}

        article h2, article h3 {{
            font-family: 'Fraunces', serif;
            font-weight: 500;
            letter-spacing: -0.02em;
            line-height: 1.3;
            margin-bottom: 1em;
        }}

        article h2 {{
            font-size: 2rem;
            margin-top: 3em;
            padding-top: 1em;
            border-top: 1px solid var(--border);
        }}

        article h3 {{
            font-size: 1.5rem;
            margin-top: 2.5em;
        }}

        article strong {{ font-weight: 600; color: var(--accent); }}

        /* Fixed Sidebar Logic */
        .sidebar {{
            position: sticky;
            top: 120px; /* Fixed distance from top */
            align-self: start;
            display: none;
            height: fit-content;
        }}

        .toc-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
            border-left: 1px solid var(--border);
            padding-left: 20px;
        }}

        .toc-list a {{
            cursor: pointer;
            text-decoration: none;
            color: var(--text-muted);
            font-size: 0.9rem;
            transition: color 0.2s;
            display: block;
        }}
        .toc-list a:hover {{ color: var(--text-main); }}

        @media (max-width: 600px) {{
            .page-layout {{ padding: 60px 24px; }}
            .article-header h1 {{ font-size: 2.5rem; }}
        }}

        @media (min-width: 1024px) {{
            .page-layout {{ grid-template-columns: 200px 1fr; }}
            .sidebar {{ display: block; }}
        }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        All Writings
    </a>

    <div class="page-layout">
        <aside class="sidebar">
            <div style="font-family: 'Fraunces', serif; margin-bottom: 16px; font-size: 0.9rem;">Contents</div>
            <ul class="toc-list">
                {toc_content}
            </ul>
        </aside>

        <main class="main-content">
            <header class="article-header">
                <h1>{title}</h1>
                <p class="date">{date}</p>
            </header>
            
            <article>
{body_content}
            </article>
        </main>
    </div>
</body>
</html>"""
    return template.format(
        title=title, 
        date=date_str,
        body_content=body_content,
        toc_content=toc_content
    )

def update_index_file(article_filename, title, date_str, excerpt, tags_list):
    """Updates index.html with new article and tags."""
    
    if not os.path.exists(INDEX_FILE):
        print(f"Warning: {INDEX_FILE} not found. Skipped index update.")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Tags in Sidebar
    # Find the tags list
    tag_section_match = re.search(r'<ul class="tags-list">(.*?)</ul>', html, re.DOTALL)
    if tag_section_match:
        existing_tags_html = tag_section_match.group(1)
        new_tags_html = existing_tags_html
        
        for tag in tags_list:
            clean_tag = tag.strip()
            # Simple check if tag exists in list (avoid duplicates)
            if f'data-tag="{clean_tag}"' not in new_tags_html:
                new_tags_html += f'\n                <li><a data-tag="{clean_tag}">{clean_tag}</a></li>'
        
        html = html.replace(existing_tags_html, new_tags_html)
        print("✓ Updated Tags sidebar in index.html")

    # 2. Add New Article to List
    # Create HTML block for new article
    tags_html = "\n".join([f'<span class="tag">{t.strip()}</span>' for t in tags_list])
    tags_attr = ",".join([t.strip() for t in tags_list])
    
    # Truncate excerpt
    clean_excerpt = excerpt[:100] + "..." if len(excerpt) > 100 else excerpt
    
    new_article_html = f"""
                <!-- {title} -->
                <a href="{ARTICLES_DIR}/{article_filename}" class="archive-item" data-tags="{tags_attr}">
                    <div class="archive-date">{date_str}</div>
                    <div class="archive-content">
                        <div class="archive-title">{title}</div>
                        <span class="archive-excerpt">{clean_excerpt}</span>
                        <div class="archive-tags">
                            {tags_html}
                        </div>
                    </div>
                    <div class="archive-arrow">→</div>
                </a>
"""

    # Insert after the opening div of post-list
    list_start_marker = '<div class="archive-list" id="post-list">'
    if list_start_marker in html:
        html = html.replace(list_start_marker, list_start_marker + new_article_html)
        print("✓ Added new article to index.html list")
    else:
        print("Warning: Could not find 'post-list' div in index.html")

    # Write back
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    if len(sys.argv) < 3:
        print('Usage: python generate_blog.py --convert "file.pdf" "Title" "Tag1,Tag2"')
        return

    if sys.argv[1] == "--convert":
        filepath = sys.argv[2]
        title = sys.argv[3]
        
        # Get Tags (Optional 4th argument)
        tags_input = sys.argv[4] if len(sys.argv) > 4 else "General"
        tags_list = [t.strip() for t in tags_input.split(',')]
        
        file_ext = Path(filepath).suffix.lower()
        print(f"Processing {file_ext} file...")
        
        structured_data = []
        if file_ext == '.pdf':
            structured_data = process_pdf(filepath)
        elif file_ext == '.docx':
            structured_data = process_docx(filepath)
        elif file_ext == '.txt':
            structured_data = process_txt(filepath)
        else:
            print("Unsupported format.")
            return

        body_html, toc_html, excerpt = generate_html_body(structured_data)
        
        # Determine Date
        short_date = datetime.now().strftime("%b %Y") # Nov 2025
        long_date = datetime.now().strftime("%B %d, %Y") # November 14, 2025
        
        full_html = create_full_html(title, body_html, toc_html, long_date)
        
        # Save output
        Path(ARTICLES_DIR).mkdir(exist_ok=True)
        filename = re.sub(r'[^a-z0-9-]', '', title.lower().replace(' ', '-')) + ".html"
        output_path = Path(ARTICLES_DIR) / filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_html)
            
        print(f"✓ Generated Article: {output_path}")
        
        # Update Index
        update_index_file(filename, title, short_date, excerpt, tags_list)

if __name__ == "__main__":
    main()