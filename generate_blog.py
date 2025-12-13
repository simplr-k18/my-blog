import os
import re
from datetime import datetime
from pathlib import Path
import sys

# --- Dependencies for file conversion ---
# You'll need to install these:
# pip install python-docx PyMuPDF
try:
    import docx
    import fitz  # PyMuPDF
except ImportError:
    print("Warning: 'python-docx' and 'PyMuPDF' are required for .docx and .pdf conversion. Please run: pip install python-docx PyMuPDF")

# Configuration

def extract_metadata_from_html(filepath):
    """Extract title and first meaningful paragraph from HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title
    title_match = re.search(r'<div class="archive-title">(.*?)</div>', content, re.DOTALL)
    title = title_match.group(1) if title_match else "Untitled"
    
    # Extract excerpt
    excerpt_match = re.search(r'<span class="archive-excerpt">(.*?)</span>', content, re.DOTALL)
    excerpt = excerpt_match.group(1).strip() if excerpt_match else "No excerpt available."

    # Extract tags
    tags_match = re.search(r'data-tags="([^"]+)"', content)
    tags_str = tags_match.group(1) if tags_match else ""
    tags = tags_str.split(',')

    # Extract date
    date_match = re.search(r'<div class="archive-date">(.*?)</div>', content)
    date_str = date_match.group(1).strip() if date_match else "Date unknown"
    
    # Get file modification time
    mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
    date_str = mod_time.strftime("%B %Y")
    
    return {
        'title': title,
        'excerpt': excerpt,
        'date': date_str, # We'll use the one from the HTML content
        'filename': os.path.basename(filepath),
        'tags': tags,
        'tags_str': tags_str
    }

def create_toc_item(heading_text):
    """Creates a TOC list item from a heading."""
    href = heading_text.lower().replace(' ', '-')
    href = re.sub(r'[^a-z0-9-]', '', href)
    return f'<li><a href="#{href}">{heading_text}</a></li>'

def create_heading_element(heading_text):
    """Creates an H2 element with an ID from a heading."""
    id_attr = heading_text.lower().replace(' ', '-')
    id_attr = re.sub(r'[^a-z0-9-]', '', id_attr)
    return f'<h2 id="{id_attr}">{heading_text}</h2>'

def convert_file_to_html(filepath, title):
    """Convert .txt, .docx, or .pdf file to a beautiful HTML article."""
    
    content = ""
    file_ext = Path(filepath).suffix.lower()

    try:
        if file_ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_ext == '.docx':
            doc = docx.Document(filepath)
            content = "\n\n".join([p.text for p in doc.paragraphs if p.text])
        elif file_ext == '.pdf':
            with fitz.open(filepath) as doc:
                content = ""
                for page in doc:
                    content += page.get_text()
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    except NameError:
        print(f"ERROR: Cannot process {file_ext}. Make sure required libraries are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        sys.exit(1)

    # Process content into HTML paragraphs and headings
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    html_content = ""
    toc_items = []
    
    for para in paragraphs:
        # Simple heading detection: all caps or starts with #
        if (para.isupper() and len(para) < 80) or para.startswith('#'):
            heading_text = para.lstrip('# ').strip()
            html_content += create_heading_element(heading_text) + "\n"
            toc_items.append(create_toc_item(heading_text))
        else:
            # Regular paragraph, check for bold/italic markers
            para = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', para)
            para = re.sub(r'\*(.*?)\*', r'<em>\1</em>', para)
            html_content += f"<p>{para}</p>\n"

    toc_html = "\n                ".join(toc_items)

    # Use the new, consistent HTML template
    article_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    <!-- Fonts: Fraunces (Editorial/Human) & Inter (UI/Clean) -->
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
        .back-link svg {{ color: var(--text-muted); }}

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

        article p, article ul {{
            margin-bottom: 1.5em;
        }}

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

        article strong {{
            font-weight: 600;
        }}

        article em {{
            font-style: italic;
            color: var(--text-secondary);
        }}

        .sidebar {{
            position: sticky;
            top: 50vh;
            transform: translateY(-50%);
            align-self: start;
            display: none;
        }}

        .toc-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .toc-list a {{
            cursor: pointer;
            text-decoration: none;
            color: var(--text-muted);
            font-size: 0.9rem;
            padding: 6px 12px;
            border-radius: 6px;
            transition: color 0.2s, background-color 0.2s, font-weight 0.2s;
        }}
        .toc-list a:hover {{
            color: var(--text-main);
            background-color: #F0F0F0;
        }}
        .toc-list a.active {{
            color: var(--text-main);
            font-weight: 600;
        }}

        @media (max-width: 600px) {{
            .page-layout {{ padding: 60px 24px; }}
            .article-header h1 {{ font-size: 2.5rem; }}
            article h2 {{ font-size: 1.8rem; }}
            article h3 {{ font-size: 1.3rem; }}
        }}

        @media (min-width: 1024px) {{
            .page-layout {{
                grid-template-columns: 200px 1fr;
            }}
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
            <ul class="toc-list">
                {toc_html}
            </ul>
        </aside>

        <main class="main-content">
            <header class="article-header">
                <h1>{title}</h1>
                <p class="date">{datetime.now().strftime("%B %d, %Y")}</p>
            </header>
            
            <article>
{html_content}
            </article>
        </main>
    </div>
</body>
</html>"""
    
    return html

def main():
    """Main function to generate blog"""
    
    # Create articles directory if it doesn't exist
    Path("articles").mkdir(exist_ok=True)
    
    # Check for --convert flag
    if len(sys.argv) >= 4 and sys.argv[1] == "--convert":
        text_file = sys.argv[2]
        article_title = " ".join(sys.argv[3:]) # Allow titles with spaces
        
        # Generate HTML filename from title
        filename = article_title.lower().replace(' ', '-')
        filename = re.sub(r'[^a-z0-9-]', '', filename)
        output_path = f"articles/{filename}.html"
        
        print(f"Converting '{text_file}' to '{output_path}'...")
        
        # Convert file to HTML
        article_html = convert_file_to_html(text_file, article_title)
        
        # Save HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(article_html)
        
        print(f"✓ Converted '{text_file}' to '{output_path}'")
        print(f"✓ Title: {article_title}")
    
    # Scan articles directory for HTML files
    articles_dir = Path("articles")
    article_files = list(articles_dir.glob("*.html"))
    
    if not article_files:
        print("\nNo articles found in articles/ directory. Run with --convert to create one.")
        return
    
    print(f"\nFound {len(article_files)} articles. Index page is managed manually.")
    print("To create a new article, run:")
    print('python generate_blog.py --convert "path/to/your/file.txt" "Your Article Title"')

if __name__ == "__main__":
    main()