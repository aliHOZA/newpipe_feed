#!/usr/bin/env python3
import json
import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import requests
import time

# Load subscriptions
with open('newpipe_subscriptions_202605080040.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Prepare combined feed
fg = FeedGenerator()
fg.title('My Combined YouTube Subscriptions')
fg.link(href='https://your-github-username.github.io/repo-name/combined.xml', rel='self')
fg.description('Latest videos from all channels I follow on YouTube')
fg.language('en')

entries = []

for sub in data['subscriptions']:
    channel_url = sub['url']
    # Extract channel ID from URL (supports /channel/ and /c/ formats)
    if '/channel/' in channel_url:
        channel_id = channel_url.split('/channel/')[-1].split('/')[0].split('?')[0]
    elif '/c/' in channel_url:
        # For custom URLs you may need an extra API call; but NewPipe usually gives /channel/
        continue
    else:
        continue

    rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    print(f'Fetching {sub["name"]} ...')
    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            # Convert published time to datetime object
            published = entry.get('published_parsed')
            if published:
                dt = datetime.fromtimestamp(time.mktime(published), tz=timezone.utc)
            else:
                dt = datetime.now(timezone.utc)
            entries.append({
                'title': entry.title,
                'link': entry.link,
                'published': dt,
                'summary': f'From {sub["name"]}: {entry.get("description", "")}',
                'author': sub['name']
            })
        time.sleep(0.5)  # be polite to YouTube
    except Exception as e:
        print(f'Error with {sub["name"]}: {e}')

# Sort by newest first
entries.sort(key=lambda x: x['published'], reverse=True)

# Add to RSS feed
for e in entries[:100]:  # limit to 100 latest videos to keep feed size reasonable
    fe = fg.add_entry()
    fe.title(e['title'])
    fe.link(href=e['link'])
    fe.pubDate(e['published'])
    fe.description(e['summary'])
    fe.author(name=e['author'])

fg.rss_file('combined.xml')
print(f'Generated combined.xml with {len(entries[:100])} videos.')
