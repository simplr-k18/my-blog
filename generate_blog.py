import os
import re
from datetime import datetime
from pathlib import Path

# Configuration
PORTFOLIO_URL = "https://simplr-k18.github.io/rishanth_reddy/"
BLOG_TITLE = "Essays"
BLOG_TAGLINE = "Thoughts on technology, design, and what matters."

def extract_metadata_from_html(filepath):
    """Extract title and first meaningful paragraph from HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    title = title_match.group(1) if title_match else "Untitled"
    
    # Extract first paragraph from article content
    article_match = re.search(r'<article>(.*?)</article>', content, re.DOTALL | re.IGNORECASE)
    if article_match:
        article_content = article_match.group(1)
        # Find first <p> tag content
        p_match = re.search(r'<p[^>]*>(.*?)</p>', article_content, re.DOTALL)
        if p_match:
            excerpt = p_match.group(1)
            # Remove HTML tags and clean up
            excerpt = re.sub(r'<[^>]+>', '', excerpt)
            excerpt = ' '.join(excerpt.split())  # Clean whitespace
            # Limit to ~150 characters
            if len(excerpt) > 150:
                excerpt = excerpt[:147] + "..."
        else:
            excerpt = "Read more..."
    else:
        excerpt = "Read more..."
    
    # Get file modification time
    mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
    date_str = mod_time.strftime("%B %Y")
    
    return {
        'title': title,
        'excerpt': excerpt,
        'date': date_str,
        'filename': os.path.basename(filepath)
    }

def generate_index_html(articles):
    """Generate the index.html with all articles"""
    
    articles_html = ""
    for i, article in enumerate(articles):
        delay = 0.3 + (i * 0.2)
        articles_html += f"""
            <article onclick="window.location.href='articles/{article['filename']}'">
                <div class="article-date">{article['date']}</div>
                <h2 class="article-title">
                    {article['title']}
                    <span class="arrow">→</span>
                </h2>
                <p class="article-excerpt">
                    {article['excerpt']}
                </p>
            </article>
"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{BLOG_TITLE}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
            background: #ffffff;
            color: #1d1d1f;
            min-height: 100vh;
            padding: 80px 20px;
            line-height: 1.6;
            overflow-x: hidden;
        }}

        .container {{
            max-width: 680px;
            margin: 0 auto;
        }}

        header {{
            margin-bottom: 100px;
            opacity: 0;
            animation: slideUp 1s ease 0.1s forwards;
        }}

        .back-to-portfolio {{
            color: #06c;
            text-decoration: none;
            font-size: 0.95em;
            display: inline-block;
            margin-bottom: 40px;
            transition: opacity 0.3s ease;
        }}

        .back-to-portfolio:hover {{
            opacity: 0.7;
        }}

        h1 {{
            font-size: 3.5em;
            font-weight: 600;
            letter-spacing: -0.02em;
            margin-bottom: 20px;
            color: #1d1d1f;
        }}

        .intro {{
            font-size: 1.3em;
            color: #6e6e73;
            font-weight: 400;
            max-width: 500px;
        }}

        .essays {{
            display: flex;
            flex-direction: column;
            gap: 0;
        }}

        article {{
            border-bottom: 1px solid #e8e8ed;
            padding: 40px 20px;
            cursor: pointer;
            position: relative;
            opacity: 0;
            animation: slideUp 0.8s ease forwards;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            background: linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.01) 50%, rgba(0,0,0,0) 100%);
            background-size: 200% 100%;
            background-position: 100% 0;
        }}

        article:nth-child(1) {{ animation-delay: 0.3s; }}
        article:nth-child(2) {{ animation-delay: 0.5s; }}
        article:nth-child(3) {{ animation-delay: 0.7s; }}
        article:nth-child(4) {{ animation-delay: 0.9s; }}
        article:nth-child(5) {{ animation-delay: 1.1s; }}

        article:last-child {{
            border-bottom: none;
        }}

        article::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 0;
            height: 60%;
            background: #000;
            transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        article:hover {{
            padding-left: 32px;
            background-position: 0% 0;
        }}

        article:hover::before {{
            width: 3px;
        }}

        article:hover .article-title {{
            transform: translateX(8px);
            color: #000;
        }}

        article:hover .article-excerpt {{
            transform: translateX(8px);
            color: #1d1d1f;
        }}

        article:hover .arrow {{
            opacity: 1;
            transform: translateX(0);
        }}

        .article-date {{
            color: #86868b;
            font-size: 0.95em;
            margin-bottom: 12px;
            font-weight: 400;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .article-title {{
            font-size: 2em;
            font-weight: 600;
            margin-bottom: 16px;
            color: #1d1d1f;
            letter-spacing: -0.01em;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .arrow {{
            opacity: 0;
            transform: translateX(-10px);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 0.8em;
        }}

        .article-excerpt {{
            color: #6e6e73;
            font-size: 1.1em;
            line-height: 1.5;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        footer {{
            margin-top: 120px;
            padding-top: 40px;
            border-top: 1px solid #e8e8ed;
            text-align: center;
            color: #86868b;
            font-size: 0.9em;
            opacity: 0;
            animation: fadeIn 1s ease 1.2s forwards;
        }}

        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}

        html {{
            scroll-behavior: smooth;
        }}

        article:active {{
            transform: scale(0.99);
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 40px 20px;
            }}
            
            h1 {{
                font-size: 2.5em;
            }}
            
            header {{
                margin-bottom: 60px;
            }}
            
            .intro {{
                font-size: 1.1em;
            }}
            
            .article-title {{
                font-size: 1.6em;
            }}
            
            article {{
                padding: 30px 15px;
            }}

            article:hover {{
                padding-left: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="{PORTFOLIO_URL}" class="back-to-portfolio">← Back to Portfolio</a>
            <h1>{BLOG_TITLE}</h1>
            <p class="intro">{BLOG_TAGLINE}</p>
        </header>

        <div class="essays">
{articles_html}
        </div>

        <footer>
            <p>© {datetime.now().year}</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html

def convert_plain_text_to_html(text_content, title):
    """Convert plain text to beautiful HTML article"""
    
    # Split into paragraphs
    paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
    
    # Detect headings (lines that start with # or are all caps and short)
    html_content = ""
    for para in paragraphs:
        if para.startswith('#'):
            # Markdown-style heading
            level = len(para) - len(para.lstrip('#'))
            heading_text = para.lstrip('#').strip()
            html_content += f"<h2>{heading_text}</h2>\n\n"
        elif para.startswith('##'):
            heading_text = para.lstrip('#').strip()
            html_content += f"<h2>{heading_text}</h2>\n\n"
        elif para.isupper() and len(para) < 80:
            # All caps = heading
            html_content += f"<h2>{para}</h2>\n\n"
        else:
            # Regular paragraph
            html_content += f"<p>{para}</p>\n\n"
    
    article_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
            background: #ffffff;
            color: #1d1d1f;
            padding: 80px 20px;
            line-height: 1.7;
            animation: fadeIn 0.6s ease;
        }}

        .container {{
            max-width: 680px;
            margin: 0 auto;
        }}

        .back {{
            color: #06c;
            text-decoration: none;
            font-size: 0.95em;
            display: inline-block;
            margin-bottom: 60px;
            transition: opacity 0.3s ease;
        }}

        .back:hover {{
            opacity: 0.7;
        }}

        h1 {{
            font-size: 3em;
            font-weight: 600;
            letter-spacing: -0.02em;
            margin-bottom: 16px;
        }}

        .date {{
            color: #86868b;
            margin-bottom: 40px;
            font-size: 0.95em;
        }}

        article p {{
            font-size: 1.2em;
            margin-bottom: 24px;
            color: #1d1d1f;
            line-height: 1.6;
        }}

        article h2 {{
            font-size: 1.8em;
            font-weight: 600;
            margin-top: 48px;
            margin-bottom: 20px;
            letter-spacing: -0.01em;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @media (max-width: 600px) {{
            body {{ padding: 40px 20px; }}
            h1 {{ font-size: 2em; }}
            article p {{ font-size: 1.1em; }}
            article h2 {{ font-size: 1.5em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back">← Essays</a>
        
        <h1>{title}</h1>
        <p class="date">{datetime.now().strftime("%B %d, %Y")}</p>
        
        <article>
{html_content}
        </article>
    </div>
</body>
</html>"""
    
    return article_html

def main():
    """Main function to generate blog"""
    import sys
    
    # Create articles directory if it doesn't exist
    Path("articles").mkdir(exist_ok=True)
    
    # Check for --convert flag
    if len(sys.argv) >= 4 and sys.argv[1] == "--convert":
        text_file = sys.argv[2]
        article_title = sys.argv[3]
        
        # Read plain text file
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{text_file}' not found")
            return
        
        # Generate HTML filename from title
        filename = article_title.lower().replace(' ', '-')
        filename = re.sub(r'[^a-z0-9-]', '', filename)
        output_path = f"articles/{filename}.html"
        
        # Convert to HTML
        article_html = convert_plain_text_to_html(text_content, article_title)
        
        # Save HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(article_html)
        
        print(f"✓ Converted '{text_file}' to '{output_path}'")
        print(f"✓ Title: {article_title}")
    
    # Scan articles directory for HTML files
    articles_dir = Path("articles")
    article_files = list(articles_dir.glob("*.html"))
    
    if not article_files:
        print("No articles found in articles/ directory")
        return
    
    # Extract metadata from all articles
    articles = []
    for filepath in sorted(article_files, key=os.path.getmtime, reverse=True):
        metadata = extract_metadata_from_html(filepath)
        articles.append(metadata)
        print(f"Found: {metadata['title']}")
    
    # Generate index.html
    index_content = generate_index_html(articles)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_content)
    
    print(f"\n✓ Generated index.html with {len(articles)} article(s)")
    print("✓ Ready to commit and push!")

if __name__ == "__main__":
    main()