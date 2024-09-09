# IdeoImageCreator
About High quality image generation by ideogram. Reverse engineered API.

## How to
- Login to https://ideogram.ai and generate some images.
- Use `Chrome` or other browsers to inspect the network requests (F12 -> XHR).
- Clone this REPO -> `git clone https://github.com/yihong0618/IdeoImageCreator.git`
- Copy the cookie.
- Copy the Bearer token.
- Copy your user name.
- Export IDEO_COOKIE='xxxxx'.
- Export IDEO_AUTH_TOKEN='xxxxx' (found after `Bearer` in the HEADERS of the requests).
- Export IDEO_USER_ID='xxxxx'.

## Usage

```
python -m ideo --prompt 'a big red cat'
```

or
```
pip install -U ideo
```

```python
from ideo import ImageGen
i = ImageGen('cookie', 'user_id', 'auth_token') # Replace 'cookie', 'user_id', and 'auth_token' with your own values
print(i.get_limit_left())
i.save_images("a blue cyber dream", './output')
```

## Customization

Customization params: 
- aspect_ratio - default "1:1"
- model_version - default "V_0_3" ("V_1_0" and lower take 1 credit)
- style - default "AUTO"
- is_auto_prompt - default "AUTO"

Example:

```python
i.save_images(prompt = "woman with son turned away walking in a park",
              aspect_ratio="16:10",
              model_version="V_1_5",
              style="PHOTO",
              output_dir='./output',)
```


## Thanks

- [chatgpt-telegram-bot](https://github.com/brainboost/chatgpt-telegram-bot)
