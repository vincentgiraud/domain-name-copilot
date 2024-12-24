# Domain copilot

Finds available and appealing domain names using Azure OpenAI, Azure Speech and GoDaddy APIs.

## Setup
Create a `.env` file from `example.env` and fill out your API information.  
Create a virtual Python environment: `python3.12 -m venv .venv`  
Install python modules: `pip install requirements.txt`

## Configure
Adapt system prompt in `find_domains.prompty` and `user.md` to your needs and test against an example.

## Generate domain names
`python3.12 main.py`

## Evaluate domain names
Run `evaluate_domain.prompty` using the [Prompty Visual Studio Code plugin](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.prompty)

## Caveats

The GoDaddy API doesn't return the actual price of a domain or if hiring their broker is required.  
So check on their website as soon as you found a domain of interest.
