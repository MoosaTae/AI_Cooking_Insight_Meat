# AI COOKING Season 1

## What I do

-   discord bot
    -   recording audio
-   prompt summarization of the text
    -   push to trello
    -   demo by using gradio

## Status

| Task           | Status |
| -------------- | ------ |
| discord bot    | ??     |
| Summarization  | Done   |

## how to run gradio summarization demo

1. get in the directory
```bash
cd prompt_summarization
```

2. Install dependencies
```bash
pip3 install -r requirements.txt
```    

3. Configure typhoon api, trello api key and token in [prompt_summarize/.env](prompt_summarize/.env)
    - get trello api key and token from [here](https://trello.com/power-ups/admin)

4. run the demo
```bash
python gradio_demo.py
```
