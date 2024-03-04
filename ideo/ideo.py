import argparse
import contextlib
import json
import os
import time
from http.cookies import SimpleCookie

from curl_cffi import requests
from curl_cffi.requests import Cookies
from fake_useragent import UserAgent

ua = UserAgent(browsers=["edge"])

base_url = "https://ideogram.ai"
browser_version = "edge101"

HEADERS = {
    "Origin": base_url,
    "Referer": base_url + "/",
    "DNT": "1",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) \
        Gecko/20100101 Firefox/117.0",
}


class ImageGen:
    def __init__(self, cookie: str, user_id: str, auth_token: str) -> None:
        self.session: requests.Session = requests.Session()
        HEADERS["user-agent"] = ua.random
        self.cookie = cookie
        self.user_id = user_id
        self.auth_token = auth_token
        HEADERS["Authorization"] = f"Bearer {auth_token}"
        self.session.headers = HEADERS
        self.session.cookies = self.parse_cookie_string(self.cookie)

    @staticmethod
    def parse_cookie_string(cookie_string):
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        cookies_dict = {}
        for key, morsel in cookie.items():
            cookies_dict[key] = morsel.value
        return Cookies(cookies_dict)

    def get_limit_left(self) -> int:
        self.session.headers["user-agent"] = ua.random
        url = f"{base_url}/api/images/sampling_available_v2?model_version=V_0_3"
        r = self.session.get(url, impersonate=browser_version)
        if not r.ok:
            raise Exception("Can not get limit left.")
        data = r.json()

        return int(data["max_creations_per_day"]) - int(
            data["num_standard_generations_today"]
        )

    def _fetch_images_metadata(self, request_id):
        url = (
            f"https://ideogram.ai/api/images/retrieve_metadata_request_id/{request_id}"
        )
        response = self.session.get(url, impersonate=browser_version)
        data = response.json()
        # this is very interesting it use resolution to check if the image is ready
        if data.get("resolution") == 1024:
            return data
        else:
            return None

    def get_images(self, prompt: str, is_auto_prompt: str = "AUTO") -> list:
        url = f"{base_url}/api/images/sample"
        self.session.headers["user-agent"] = ua.random
        payload = {
            "aspect_ratio": "1:1",
            "model_version": "V_0_3",  # the latest version
            "prompt": prompt,
            "raw_or_fun": "raw",
            "speed": "slow",
            "style": "photo",
            "user_id": self.user_id,
            "variation_strength": 50,
            "use_autoprompt_option": is_auto_prompt,  # "AUTO" or "OFF"
        }
        response = self.session.post(
            url,
            data=json.dumps(payload),
            impersonate=browser_version,
        )
        if not response.ok:
            print(response.text)
            raise Exception(f"Error response {str(response)}")
        response_body = response.json()
        request_id = response_body["request_id"]
        start_wait = time.time()
        print("Waiting for results...")
        while True:
            if int(time.time() - start_wait) > 600:
                raise Exception("Request timeout")
            image_data = self._fetch_images_metadata(request_id)
            if not image_data:
                print(".", end="", flush=True)
            else:
                data = image_data.get("responses", [])
                return [
                    f"{base_url}/api/images/direct/{i['response_id']}" for i in data
                ]

    def save_images(
        self,
        prompt: str,
        output_dir: str,
    ) -> None:
        png_index = 0
        try:
            links = self.get_images(prompt)
        except Exception as e:
            print(e)
            raise
        with contextlib.suppress(FileExistsError):
            os.mkdir(output_dir)
        for link in links:
            while os.path.exists(os.path.join(output_dir, f"{png_index}.png")):
                png_index += 1
            print(link)
            response = self.session.get(link, impersonate=browser_version)
            if response.status_code != 200:
                raise Exception("Could not download image")
            # save response to file
            with open(
                os.path.join(output_dir, f"{png_index}.png"), "wb"
            ) as output_file:
                output_file.write(response.content)
            png_index += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", help="Auth cookie from browser", type=str, default="")
    parser.add_argument("-I", help="User id from browser", type=str, default="")
    parser.add_argument(
        "-A", help="Bearer auth token from browser(request)", type=str, default=""
    )
    parser.add_argument(
        "--prompt",
        help="Prompt to generate images for",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        help="Output directory",
        type=str,
        default="./output",
    )

    args = parser.parse_args()

    # Create image generator
    # follow old style
    image_generator = ImageGen(
        os.environ.get("IDEO_COOKIE") or args.U,
        os.environ.get("IDEO_USER_ID") or args.I,
        os.environ.get("IDEO_AUTH_TOKEN") or args.A,
    )
    print(f"{image_generator.get_limit_left()} images left")
    image_generator.save_images(
        prompt=args.prompt,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
