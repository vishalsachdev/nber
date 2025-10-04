"""
Fix broken Google Scholar URLs for presenters
"""

import json

# Mapping of presenters to their correct Google Scholar URLs
CORRECTED_URLS = {
    "Aidan Toner-Rodgers": "https://scholar.google.com/citations?user=HGmipIYAAAAJ",
    "Ajay K. Agrawal": "https://scholar.google.com/citations?user=Ap_7FkwAAAAJ",
    "Andrey Fradkin": "https://scholar.google.com/citations?user=5qkgRKsAAAAJ",
    "Anton Korinek": "https://scholar.google.com/citations?user=zcleqRcAAAAJ",
    "Austan Goolsbee": "https://scholar.google.com/citations?user=6qFRybkAAAAJ",
    "Chad Syverson": "https://scholar.google.com/citations?user=xiSZ4cYAAAAJ",
    "Daron Acemoglu": "https://scholar.google.com/citations?user=l9Or8EMAAAAJ",
    "Diane Coyle": "https://scholar.google.com/citations?user=4VPmi2cAAAAJ",
    "Erik Brynjolfsson": "https://scholar.google.com/citations?user=lqyGZpQAAAAJ",
    "Gili Rusak": None,  # No Scholar profile found
    "Iain M. Cockburn": "https://scholar.google.com/citations?user=A85ndQgAAAAJ",
    "John J. Horton": "https://scholar.google.com/citations?user=L_O2kH0AAAAJ",
    "Paul M. Romer": "https://scholar.google.com/citations?user=b5oj894AAAAJ",
    "Peyman Shahidi": None,  # PhD student, may not have profile yet
    "Rebecca Henderson": "https://scholar.google.com/citations?user=zBQv1rIAAAAJ",
    "Scott Stern": "https://scholar.google.com/citations?user=5opEOuMAAAAJ",
    "Maxim Ventura-Bolet": None,  # No Scholar profile found
}

# Load the data
with open('nber_videos_transcripts.json', 'r') as f:
    videos = json.load(f)

print(f'Updating Google Scholar URLs...\n')

updates_made = 0
removed_urls = 0

for video in videos:
    for presenter in video.get('presenters', []):
        name = presenter['name']
        if name in CORRECTED_URLS:
            old_url = presenter.get('scholar_url')
            new_url = CORRECTED_URLS[name]

            if new_url is None:
                # Remove the URL if we couldn't find one
                if old_url:
                    del presenter['scholar_url']
                    removed_urls += 1
                    print(f'✗ Removed broken URL for {name}')
            elif old_url != new_url:
                # Update the URL
                presenter['scholar_url'] = new_url
                updates_made += 1
                print(f'✓ Updated {name}')
                print(f'  Old: {old_url}')
                print(f'  New: {new_url}')

# Save the updated data
with open('nber_videos_transcripts.json', 'w') as f:
    json.dump(videos, f, indent=2)

print(f'\n=== SUMMARY ===')
print(f'URLs updated: {updates_made}')
print(f'URLs removed: {removed_urls}')
print(f'Total changes: {updates_made + removed_urls}')
print(f'\nData saved to nber_videos_transcripts.json')
