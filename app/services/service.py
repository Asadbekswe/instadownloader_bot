import asyncio
import os
from urllib.parse import urlparse

import instaloader
import requests


async def download_instagram_video(url: str, file_path: str) -> bool:
    loop = asyncio.get_running_loop()

    def _download():
        try:
            loader = instaloader.Instaloader(download_videos=True, save_metadata=False, compress_json=False)

            path_parts = [p for p in urlparse(url).path.split("/") if p]
            if len(path_parts) < 2:
                return False
            shortcode = path_parts[-1]

            post = instaloader.Post.from_shortcode(loader.context, shortcode)

            video_urls = []
            if post.is_video:
                video_urls.append(post.video_url)
            elif post.typename == "GraphSidecar":
                for node in post.get_sidecar_nodes():
                    if node.is_video:
                        video_urls.append(node.video_url)

            if not video_urls:
                return False

            video_url = video_urls[0]

            r = requests.get(video_url, stream=True, timeout=20)
            if r.status_code == 200:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=16384):  # 16KB chunk
                        f.write(chunk)
                return True
            return False
        except Exception as e:
            print(f"Download error: {e}")
            return False

    return await loop.run_in_executor(None, _download)
