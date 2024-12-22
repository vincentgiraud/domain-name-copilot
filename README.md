# Domain copilot

Finds available domain names using Azure OpenAI and GoDaddy APIs.

## Configuration
Create a `.env` file from `example.env` and fill out your API information.

## Generate domain names
`.conda/bin/python main.py`

## Evaluate domain names
Run `evaluate_domain.prompty` using the [Prompty Visual Studio Code plugin](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.prompty)

## Caveats

The GoDaddy API doesn't return the actual price of a domain or if hiring their broker is required.  
So check on their website as soon as you found a domain of interest.
