#!/usr/bin/env python3
"""
Utility script to analyze and query presenter information from NBER videos JSON.
"""

import json
from collections import defaultdict, Counter
from typing import List, Dict, Any

def load_videos(filename: str = "nber_videos_transcripts.json") -> List[Dict[str, Any]]:
    """Load videos from JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_all_presenters(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get all presenters with their video information."""
    all_presenters = []
    for video in videos:
        if 'presenters' in video:
            for presenter in video['presenters']:
                all_presenters.append({
                    'name': presenter['name'],
                    'affiliation': presenter['affiliation'],
                    'video_id': video['id'],
                    'video_title': video['title'],
                    'video_url': video['url']
                })
    return all_presenters

def get_affiliation_stats(videos: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get statistics about affiliations."""
    affiliation_counts = Counter()
    for video in videos:
        if 'presenters' in video:
            for presenter in video['presenters']:
                affiliation_counts[presenter['affiliation']] += 1
    return dict(affiliation_counts)

def get_presenter_stats(videos: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get statistics about individual presenters."""
    presenter_counts = Counter()
    for video in videos:
        if 'presenters' in video:
            for presenter in video['presenters']:
                presenter_counts[presenter['name']] += 1
    return dict(presenter_counts)

def search_presenters(videos: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Search for presenters by name or affiliation."""
    query_lower = query.lower()
    results = []
    
    for video in videos:
        if 'presenters' in video:
            for presenter in video['presenters']:
                if (query_lower in presenter['name'].lower() or 
                    query_lower in presenter['affiliation'].lower()):
                    results.append({
                        'name': presenter['name'],
                        'affiliation': presenter['affiliation'],
                        'video_title': video['title'],
                        'video_url': video['url']
                    })
    
    return results

def print_summary(videos: List[Dict[str, Any]]):
    """Print a comprehensive summary of the data."""
    print("=== NBER VIDEOS PRESENTER ANALYSIS ===\n")
    
    # Basic stats
    total_videos = len(videos)
    videos_with_presenters = sum(1 for v in videos if v.get('presenters'))
    total_presenters = sum(v.get('num_presenters', 0) for v in videos)
    
    print(f"Total videos: {total_videos}")
    print(f"Videos with presenters: {videos_with_presenters}")
    print(f"Total presenters: {total_presenters}")
    print(f"Average presenters per video: {total_presenters/total_videos:.1f}")
    
    # Affiliation stats
    affiliation_stats = get_affiliation_stats(videos)
    print(f"\nUnique affiliations: {len(affiliation_stats)}")
    
    print("\n=== TOP AFFILIATIONS ===")
    for affiliation, count in sorted(affiliation_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{affiliation}: {count} presenter(s)")
    
    # Presenter stats
    presenter_stats = get_presenter_stats(videos)
    multiple_videos = {name: count for name, count in presenter_stats.items() if count > 1}
    
    if multiple_videos:
        print(f"\n=== PRESENTERS IN MULTIPLE VIDEOS ===")
        for name, count in sorted(multiple_videos.items(), key=lambda x: x[1], reverse=True):
            print(f"{name}: {count} video(s)")
    
    # Videos with most presenters
    print(f"\n=== VIDEOS WITH MOST PRESENTERS ===")
    videos_by_presenters = sorted(videos, key=lambda x: x.get('num_presenters', 0), reverse=True)
    for video in videos_by_presenters[:5]:
        print(f"{video.get('num_presenters', 0)} presenters: {video['title'][:80]}...")

def main():
    """Main function with interactive menu."""
    videos = load_videos()
    
    while True:
        print("\n" + "="*50)
        print("NBER VIDEOS PRESENTER ANALYZER")
        print("="*50)
        print("1. Show summary statistics")
        print("2. Search presenters by name or affiliation")
        print("3. Show all presenters by affiliation")
        print("4. Show videos with most presenters")
        print("5. Export presenter data to CSV")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            print_summary(videos)
        
        elif choice == '2':
            query = input("Enter search term (name or affiliation): ").strip()
            if query:
                results = search_presenters(videos, query)
                if results:
                    print(f"\nFound {len(results)} result(s):")
                    for result in results:
                        print(f"- {result['name']}, {result['affiliation']}")
                        print(f"  Video: {result['video_title'][:60]}...")
                        print(f"  URL: {result['video_url']}")
                        print()
                else:
                    print("No results found.")
        
        elif choice == '3':
            affiliation_stats = get_affiliation_stats(videos)
            print("\n=== ALL AFFILIATIONS ===")
            for affiliation, count in sorted(affiliation_stats.items()):
                print(f"{affiliation}: {count} presenter(s)")
        
        elif choice == '4':
            print("\n=== VIDEOS BY PRESENTER COUNT ===")
            videos_by_presenters = sorted(videos, key=lambda x: x.get('num_presenters', 0), reverse=True)
            for i, video in enumerate(videos_by_presenters, 1):
                print(f"{i}. {video.get('num_presenters', 0)} presenters: {video['title']}")
        
        elif choice == '5':
            import csv
            all_presenters = get_all_presenters(videos)
            filename = "nber_presenters.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'affiliation', 'video_title', 'video_url'])
                writer.writeheader()
                writer.writerows(all_presenters)
            print(f"Exported {len(all_presenters)} presenters to {filename}")
        
        elif choice == '6':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
