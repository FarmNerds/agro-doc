# LLM

If testing with other LLMs, create a generic wrapper for the LLM of the pipeline similar to how `../ocr` has a generic `HandwritingReader`.

If the deployment architecture has GPU acceleration, configure all CPU models to use the GPU.

Use context from the bounding boxes location to determine what row and column of a grid the text will be in. This informs the LLM of what context to use to correct that text. 

i.e: If it is supposed to be a quantity and the post-processed text comes as "20 lv", it can be corrected to "20 lbs"