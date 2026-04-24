from transformers import pipeline
import torch
import math

MODEL = "Helsinki-NLP/opus-mt-zh-en"
_pipe = None

def _get_pipe():
    global _pipe
    if _pipe is None:
        device = 0 if torch.cuda.is_available() else -1
        _pipe = pipeline("translation_zh_to_en", model=MODEL, device=device)
    return _pipe

def chunk_text(text, max_tokens=400):
    for i in range(math.ceil(len(text) / max_tokens)):
        yield text[i * max_tokens:(i * max_tokens) + max_tokens]

def translate(text):
    pipe = _get_pipe()

    output = ""
    for chunk in pipe(chunk_text(text)):
        output += chunk[0]["translation_text"]
    return output


if __name__ == "__main__":
    translation = translate("")
    print(translation)