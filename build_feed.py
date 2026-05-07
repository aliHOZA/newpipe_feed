#!/usr/bin/env python3
# IMPORT channels from the separate file you created
from channels import CHANNELS
import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import time

# Initialize combined feed with your correct repository URL
fg = FeedGenerator()
fg.title('My Combined YouTube Subscriptions')
fg.link(href='https://raw.githubusercontent.com/aliHOZA/newpipe_feed/main/combined.xml', rel='self')
fg.atomlink(href='https://raw.githubusercontent.com/aliHOZA/newpipe_feed/main/combined.xml', rel='self')
fg.description('Latest videos from all channels I follow on YouTube')

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
                'summary': f'From {name}: {entry.get("description", "")}',
                'author': name
            })
        time.sleep(0.5)  # Respect YouTube's servers
    except Exception as e:
        print(f'Error with {name}: {e}')

# Sort entries, latest first
entries.sort(key=lambda x: x['published'], reverse=True)

# Add the top 100 videos to the feed
for e in entries[:100]:
    fe = fg.add_entry()
    fe.title(e['title'])
    fe.link(href=e['link'])
    fe.pubDate(e['published'])
    fe.description(e['summary'])
    fe.author(name=e['author'])

# Save the combined feed as combined.xml
fg.rss_file('combined.xml')
print(f'✅ Generated combined.xml with {len(entries[:100])} videos.')
