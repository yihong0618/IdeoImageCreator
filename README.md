# IdeoImageCreator
About High quality image generation by ideogram. Reverse engineered API.

## How to
- Login to https://ideogram.ai and generate some images.
- Use `Chrome` or other browsers to inspect the network requests (F12 -> XHR).
- Clone this REPO -> `git clone https://github.com/flowese/IdeogramWrapper.git`
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

## Thanks

- [chatgpt-telegram-bot](https://github.com/brainboost/chatgpt-telegram-bot)