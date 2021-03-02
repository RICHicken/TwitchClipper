import json
import sys
import ffmpeg
from urllib.request import Request, urlopen


class TwitchClipper:
    def __init__(self):
        self.clientId = 'x7e6kwztgt5lqz2jvnhyhp8h66cyee'
        self.secret = '35ew7v9n86wab84pm657kctf4m2lgb'
        request = Request(
            url=(
                f"https://id.twitch.tv/oauth2/token"
                f"?client_id={self.clientId}"
                f"&client_secret={self.secret}"
                f"&grant_type=client_credentials"
            ),

            method="POST"
        )
        with urlopen(request) as response:
            result = json.load(response)
            self.accesstoken = result["access_token"]
        self.auth = {
            'Client-Id': self.clientId,
            'Authorization': f"Bearer {self.accesstoken}"
        }

    def get_user(self, user: str) -> json:
        request = Request(
            url=(
                f"https://api.twitch.tv/helix/users"
                f"?login={user}"
            ),
            headers=self.auth,
            method="GET"
        )
        with urlopen(request) as response:
            result = json.load(response)
            return result

    def get_clip(self, id: str) -> (str, str):
        request = Request(
            url=(
                f"https://api.twitch.tv/helix/clips"
                f"?id={id}"
            ),
            headers=self.auth,
            method="GET"
        )
        with urlopen(request) as response:
            result = json.load(response)
            clip_meta = result["data"][0]
            clip_url = f"{clip_meta['thumbnail_url'].split('-preview-')[0]}.mp4"
            return clip_url, clip_meta["title"]


if __name__ == "__main__":
    # Parse Arguments
    args = sys.argv
    if len(args) < 2:
        print("Must include a twitch clip id or clip url")
        exit(1)
    id = sys.argv[1].split("/clip/")[-1].split("?")[0]
    print(id)

    # Get Twitch Information
    clipper = TwitchClipper()
    vid_url, title = clipper.get_clip(id)
    print(vid_url)

    # FFMPEG - download and encode video
    process = (
        ffmpeg.input(vid_url)
              .output(f"{title}.mp4")
              .run_async()
    )
    process.wait()