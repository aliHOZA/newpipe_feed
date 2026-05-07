#!/usr/bin/env python3
"""
Convert NewPipe subscriptions into a combined YouTube RSS feed.
"""
import time
from datetime import datetime, timezone

import feedparser
from feedgen.feed import FeedGenerator

from channels import CHANNELS


def main():
    """Generate combined RSS feed from channel list."""
    # Initialize combined feed with your correct raw URL
    fg = FeedGenerator()
    fg.title('My Combined YouTube Subscriptions')
    fg.link(href='https://raw.githubusercontent.com/aliHOZA/newpipe_feed/main/combined.xml', rel='self')
    fg.atomlink(href='https://raw.githubusercontent.com/aliHOZA/newpipe_feed/main/combined.xml', rel='self')
    fg.description('Latest videos from all channels I follow on YouTube')
    fg.language('en')
    
    entries = []
    
    # Loop through each channel from channels.py
    for name, channel_id in CHANNELS:
        rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
        print(f'Fetching {name} ...')
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                published = entry.get('published_parsed')
                if published:
                    dt = datetime.fromtimestamp(time.mktime(published), tz=timezone.utc)
                else:
                    dt = datetime.now(timezone.utc)
                entries.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': dt,
                    'summary': f'From {name}: {entry.get("description", "")[:500]}',
                    'author': name
                })
            time.sleep(0.5)  # Respect YouTube's servers
        except Exception as e:
            print(f'Error with {name}: {e}')
    
    # Sort entries, latest first
    entries.sort(key=lambda x: x['published'], reverse=True)
    
    # Add the top 100 videos to the feed
    for entry in entries[:100]:
        fe = fg.add_entry()
        fe.title(entry['title'])
        fe.link(href=entry['link'])
        fe.pubDate(entry['published'])
        fe.description(entry['summary'])
        fe.author(name=entry['author'])
    
    # Save the combined feed as combined.xml
    fg.rss_file('combined.xml')
    print(f'✅ Generated combined.xml with {len(entries[:100])} videos.')


if __name__ == '__main__':
    main()
