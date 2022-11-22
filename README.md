
# Chatting bot

Chat with bot in Chinese(Mandarin). Including ASR(or STT), NLU(or NLP) and TTS.

## Features

### Asking for Weather

### Asking for Datetime

### Chatting

### Bot Command Management

## Bot Specs

* Microphone
* Speaker

## Requirements

### OS

Linux x86_64 or WSL2 (GNU Compilers(gcc, g++) are required for installing NeMo)

### Packages

* STT: NVIDIA **NeMo** -- [GitHub](https://github.com/NVIDIA/NeMo)
* TTS: **Mandarin-TTS** with PyTorch backend -- [GitHub](https://github.com/ranchlai/mandarin-tts)

## Setup

```sh
git clone --recurse-submodules $URL_OF_THIS_REPO

# Create environment for machine having CUDA device.
conda create -n $NAME_OF_NEW_ENV --file package-list-cuda.txt
```

## Usage

```sh
python BotService/wsgi.py
```

## Known Issues

* pretrained stt_zh_citrinet_1024_gamma_0_25 weights may be the best STT model in NeMo,
  however, it still mistranscribe some chars in a sentence.
* MTTS API cannot proccess sentence containing `:` and whitespace.
* Try to speak a little slower.

## Abbreviations

* ASR: Automatic Speech Recognition
* STT: Speech to Text
* NLU: Natural Language Understanding
* NLP: Natural Language Processing
* TTS: Text to Speech
