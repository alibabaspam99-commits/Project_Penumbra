#!/usr/bin/env python3
"""
Generate batch image review HTML pages.

Usage:
    python generate-batch.py --pattern "extracted_bar_*.png" --batch-size 10 --output-prefix review
    python generate-batch.py --files "image1.png,image2.png,..." --title "Redaction Review"
"""

import argparse
import glob
import os
from pathlib import Path

def generate_batch_html(filenames, batch_num=1, output_file=None, title="Image Batch Review"):
    """Generate single batch HTML page."""
    
    items_html = ""
    for idx, filename in enumerate(filenames, 1):
        items_html += f'''        <div class="item">
            <div class="number">{idx}</div>
            <img src="{filename}" alt="Item {idx}">
        </div>\n'''
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>{title} - Batch {batch_num}</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f0f0f0; padding: 20px; margin: 0; }}
        h1 {{ text-align: center; color: #333; }}
        .instructions {{ max-width: 1200px; margin: 0 auto 20px; 
                       background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; border-radius: 4px; }}
        .gallery {{ display: flex; flex-wrap: wrap; gap: 20px; 
                  justify-content: center; background: white; padding: 20px; border-radius: 8px; }}
        .item {{ display: flex; flex-direction: column; 
               align-items: center; gap: 10px; }}
        .number {{ font-size: 24px; font-weight: bold; color: red; 
                 background: #ffffcc; padding: 5px 15px; border-radius: 5px; 
                 border: 2px solid #ff0000; }}
        img {{ max-height: 250px; border: 1px solid #ccc; 
             border-radius: 4px; background: white; }}
    </style>
</head>
<body>
    <h1>{title} - Batch {batch_num}</h1>
    <div class="instructions">
        <h3>Instructions</h3>
        <p>Review the {len(filenames)} images below. Tell me which numbers have issues.</p>
    </div>
    
    <div class="gallery">
{items_html}    </div>
</body>
</html>'''
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(html)
        print(f"Created: {output_file}")
    else:
        print(html)
    
    return html

def main():
    parser = argparse.ArgumentParser(description="Generate batch image review HTML")
    parser.add_argument('--pattern', help='Glob pattern (e.g., "extracted_*.png")')
    parser.add_argument('--files', help='Comma-separated filenames')
    parser.add_argument('--batch-size', type=int, default=10, help='Images per batch')
    parser.add_argument('--output-prefix', default='batch_review', help='Output filename prefix')
    parser.add_argument('--title', default='Image Batch Review', help='Page title')
    
    args = parser.parse_args()
    
    # Get filenames
    if args.pattern:
        filenames = sorted(glob.glob(args.pattern))
    elif args.files:
        filenames = [f.strip() for f in args.files.split(',')]
    else:
        parser.error("Specify --pattern or --files")
    
    if not filenames:
        print("No files found!")
        return
    
    # Create batches
    batch_num = 1
    for i in range(0, len(filenames), args.batch_size):
        batch = filenames[i:i + args.batch_size]
        output = f"{args.output_prefix}_{batch_num:03d}.html"
        generate_batch_html(batch, batch_num, output, args.title)
        batch_num += 1

if __name__ == '__main__':
    main()
