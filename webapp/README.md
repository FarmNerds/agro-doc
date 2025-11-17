# Webapp Directory
[description place-holder]

## Trying Different OCRs

### 15 November 2025
I am going to use the CPU version of [PaddleOCR](https://www.paddlepaddle.org.cn/en/install/quick?docurl=/documentation/docs/en/develop/install/pip/linux-pip_en.html)--for now pivoting away from Google Cloud Vision. In the future, I can refactor to use the GPU verson (CUDA 13.0) instead:

```bash
python3 -m pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu130/
```

Also going to use (for now) the [Phi-3-mini-128k-instruct](https://huggingface.co/microsoft/Phi-3-mini-128k-instruct) model off of HuggingFace.

### 7 November 2025

I am exploring some new OCR frameworks to use to translate the raw handwritten text in images to not only (1) translate them directly but also (2) query an LLM to edit the text based on "expected" or "assumed" inputs.

For example, if I am uploading an image that has the word "cukes" but it's difficult for the OCR to pick up the letters, it my translate it as "cokes". However, with our understanding, we know that it's very unlikely to have the word "cokes" on a whiteboard, and much MORE likely to have so-called *farm-related* terms on the whiteboard. Therefore, we want to use an edit step using an LLM with the farm-context. Additionally, we could use an LLM to offer potential organizations of the text.


To summarize, a potential workflow is:

1. Upload an image of handwriting
2. Have an OCR model translate it
3. Pipe the text into an LLM that can use the farm-context
4. Pipe the 'corrected' text into JSON format or the Excel format


