FROM nvidia/cuda:11.0.3-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/conda/bin:$PATH"

RUN apt-get update && apt-get install -y \
    ffmpeg wget curl git unzip \
    build-essential cmake libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /miniconda.sh \
    && bash /miniconda.sh -b -p /opt/conda \
    && rm /miniconda.sh

RUN /opt/conda/bin/conda create -n LSP python=3.6 pip -y

SHELL ["/bin/bash", "-c"]

WORKDIR /

COPY . .

RUN conda run -n LSP conda install --yes --file requirements.txt || \
    conda run -n LSP pip install --no-cache-dir -r requirements.txt

RUN conda run -n LSP conda install --yes opencv || \
conda run -n LSP pip install --no-cache-dir opencv-python-headless==4.5.5.64 || \
conda run -n LSP pip install --no-cache-dir opencv-python==4.5.5.64

RUN conda run -n LSP pip check || conda run -n LSP pip install --no-cache-dir --upgrade --ignore-installed -r requirements.txt

RUN conda run -n LSP pip install --no-cache-dir gdown

RUN mkdir -p /data && \
    gdown --folder https://drive.google.com/drive/folders/1fsHA0KZTWWh1dwOkwLOb9n2qAM_BCQpx?usp=sharing -O /data

EXPOSE 8000

CMD ["conda", "run", "--no-capture-output", "-n", "LSP", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
