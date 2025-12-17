# Use a reasonably recent version of Python (as of Sep 2024). The -bookworm
# variant ensures that this will run on both x86 and arm64 machines.
FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Install system dependencies required by OpenCV (used by PaddleOCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies
# Install PyTorch CPU version first (from PyTorch's CPU index for compatibility)
RUN pip3 install torch==2.5.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install PaddlePaddle CPU version from their custom index
RUN python3 -m pip install paddlepaddle==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/

# Install remaining dependencies (transformers, accelerate, flask, etc.)
RUN pip3 install -r requirements.txt

# Install PaddleOCR
RUN python3 -m pip install paddleocr
# # Install Google Cloud SDK
# RUN curl -sSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
#     echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list && \
#     apt-get update && apt-get install -y google-cloud-sdk


