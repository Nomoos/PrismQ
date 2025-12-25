"""Interactive CLI for downloading YouTube video inspiration from user-provided links."""

import sys
from pathlib import Path

# Add parent directories to path for imports
repo_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from T.Idea.Inspiration.From.User.YouTube.Video.src.downloader import download_video_inspiration


def main():
    """Interactive CLI for downloading YouTube video inspiration."""
    print("=" * 70)
    print("YouTube Video Inspiration Downloader (User-Provided Links)")
    print("=" * 70)
    print()
    print("This tool downloads YouTube video metadata and text content")
    print("from a URL that you provide.")
    print()
    
    while True:
        # Get URL from user
        url = input("Enter YouTube video URL (or 'quit' to exit): ").strip()
        
        if url.lower() in ['quit', 'q', 'exit']:
            print("Goodbye!")
            break
        
        if not url:
            print("Please enter a valid URL.")
            continue
        
        try:
            print(f"\nDownloading video from: {url}")
            print("Please wait...")
            
            # Download the video inspiration
            inspiration = download_video_inspiration(url)
            
            print("\n" + "=" * 70)
            print("✓ Successfully downloaded video inspiration!")
            print("=" * 70)
            print(f"\nTitle: {inspiration['title']}")
            print(f"Source: {inspiration['source']}")
            print(f"URL: {inspiration['source_url']}")
            
            metadata = inspiration['metadata']
            print(f"\nChannel: {metadata['channel']}")
            print(f"Duration: {metadata['duration']} seconds")
            print(f"Views: {metadata['view_count']:,}")
            print(f"Likes: {metadata['like_count']:,}")
            
            if metadata.get('tags'):
                print(f"\nTags: {', '.join(metadata['tags'][:5])}")
                if len(metadata['tags']) > 5:
                    print(f"  ... and {len(metadata['tags']) - 5} more")
            
            content_preview = inspiration['content'][:200]
            if len(inspiration['content']) > 200:
                content_preview += "..."
            print(f"\nContent preview:\n{content_preview}")
            
            print("\n" + "=" * 70)
            print()
            
            # Ask if user wants to download another
            another = input("Download another video? (y/n): ").strip().lower()
            if another not in ['y', 'yes']:
                print("Goodbye!")
                break
            print()
            
        except ValueError as e:
            print(f"\n✗ Error: {e}")
            print("Please check the URL and try again.\n")
        except RuntimeError as e:
            print(f"\n✗ Error: {e}")
            print("Please make sure yt-dlp is installed: pip install yt-dlp\n")
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
