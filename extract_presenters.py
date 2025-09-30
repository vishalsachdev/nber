#!/usr/bin/env python3
"""
Script to extract presenters and their affiliations from NBER videos JSON
and modify the JSON structure to include this information.
"""

import json
import re
from typing import List, Dict, Any

def extract_presenters_from_description(description: str) -> List[Dict[str, str]]:
    """
    Extract presenters and their affiliations from the description text.
    
    Args:
        description: The video description text
        
    Returns:
        List of dictionaries with 'name' and 'affiliation' keys
    """
    presenters = []
    
    # Look for "Presented by:" or "Presented b:" (typo in some entries)
    # Capture everything until we hit a line that looks like a title (starts with capital letter and doesn't contain a comma)
    presenter_section_match = re.search(r'Presented b[yi]:\s*\n(.*?)(?=\n[A-Z][^,]*\n|\n\n|$)', description, re.DOTALL)
    
    # If that doesn't work, try a more flexible approach
    if not presenter_section_match:
        # Look for lines that start with a name followed by a comma and affiliation
        lines = description.split('\n')
        presenter_lines = []
        in_presenter_section = False
        
        for line in lines:
            line = line.strip()
            if 'Presented b' in line:
                in_presenter_section = True
                continue
            elif in_presenter_section:
                # Stop when we hit a line that looks like a title (no comma, starts with capital)
                if line and ',' not in line and line[0].isupper() and len(line) > 10:
                    break
                # Add lines that look like presenter info (contain comma)
                if line and ',' in line and not any(x in line.lower() for x in ['organizers', 'supported by', 'september']):
                    presenter_lines.append(line)
        
        if presenter_lines:
            presenter_text = '\n'.join(presenter_lines)
        else:
            return presenters
    else:
        presenter_text = presenter_section_match.group(1).strip()
    
    # Split by newlines and process each presenter
    presenter_lines = [line.strip() for line in presenter_text.split('\n') if line.strip()]
    
    for line in presenter_lines:
        # Skip empty lines
        if not line:
            continue
        
        # Skip lines that don't contain a comma (likely not presenter info)
        if ',' not in line:
            continue
            
        # Split by comma to separate name from affiliation
        parts = line.split(',')
        if len(parts) >= 2:
            name = parts[0].strip()
            # Join all parts after the first comma as affiliation
            affiliation = ','.join(parts[1:]).strip()
            
            # Skip if this looks like organizer info (contains "Organizers")
            if 'organizers' in affiliation.lower():
                continue
            
            presenters.append({
                'name': name,
                'affiliation': affiliation
            })
    
    return presenters

def modify_videos_json(input_file: str, output_file: str = None) -> None:
    """
    Modify the videos JSON to include presenter information.
    
    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output JSON file (defaults to input_file)
    """
    if output_file is None:
        output_file = input_file
    
    # Read the existing JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    # Process each video
    for video in videos:
        if 'description' in video:
            presenters = extract_presenters_from_description(video['description'])
            video['presenters'] = presenters
            video['num_presenters'] = len(presenters)
        else:
            video['presenters'] = []
            video['num_presenters'] = 0
    
    # Write the modified JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    
    print(f"Modified JSON saved to {output_file}")
    print(f"Processed {len(videos)} videos")

def print_presenter_summary(videos: List[Dict[str, Any]]) -> None:
    """
    Print a summary of all presenters found.
    
    Args:
        videos: List of video dictionaries
    """
    print("\n=== PRESENTER SUMMARY ===")
    
    all_presenters = []
    for video in videos:
        if 'presenters' in video:
            for presenter in video['presenters']:
                all_presenters.append({
                    'name': presenter['name'],
                    'affiliation': presenter['affiliation'],
                    'video_title': video['title']
                })
    
    # Group by affiliation
    affiliation_groups = {}
    for presenter in all_presenters:
        affiliation = presenter['affiliation']
        if affiliation not in affiliation_groups:
            affiliation_groups[affiliation] = []
        affiliation_groups[affiliation].append(presenter)
    
    print(f"\nTotal presenters: {len(all_presenters)}")
    print(f"Unique affiliations: {len(affiliation_groups)}")
    
    print("\n=== PRESENTERS BY AFFILIATION ===")
    for affiliation, presenters in sorted(affiliation_groups.items()):
        print(f"\n{affiliation} ({len(presenters)} presenters):")
        for presenter in presenters:
            print(f"  - {presenter['name']} (in: {presenter['video_title'][:60]}...)")

if __name__ == "__main__":
    input_file = "nber_videos.json"
    
    # Read the current JSON to show before/after
    with open(input_file, 'r', encoding='utf-8') as f:
        original_videos = json.load(f)
    
    print("=== BEFORE MODIFICATION ===")
    for i, video in enumerate(original_videos):
        print(f"{i+1}. {video['title']}")
        print(f"   Presenters: Not extracted")
    
    # Modify the JSON
    modify_videos_json(input_file)
    
    # Read the modified JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        modified_videos = json.load(f)
    
    print("\n=== AFTER MODIFICATION ===")
    for i, video in enumerate(modified_videos):
        print(f"{i+1}. {video['title']}")
        print(f"   Presenters ({video['num_presenters']}):")
        for presenter in video['presenters']:
            print(f"     - {presenter['name']}, {presenter['affiliation']}")
        print()
    
    # Print summary
    print_presenter_summary(modified_videos)
