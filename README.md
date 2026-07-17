# Domain copilot

Finds available and appealing domain names using Azure OpenAI, Azure Speech and the GoDaddy API.

## Setup

```bash
cp example.env .env          # then fill in your API info
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Authentication to Azure OpenAI uses `AZURE_OPENAI_API_KEY` if set, otherwise
falls back to Azure AD (`DefaultAzureCredential` — managed identity or `az login`).

## Configure

Adapt the brief in `user.md` to your needs. The system prompts live in `llm.py`.

## Generate domain names

```bash
python3.12 main.py generate                 # loop forever (Ctrl-C to stop)
python3.12 main.py generate --rounds 5      # run 5 rounds then exit
python3.12 main.py generate --brief user.md --delay 2
```

Available domains under `MAX_USD_PRICE` are appended to `domains.txt`.

## Evaluate domain names

```bash
python3.12 main.py evaluate --file domains.txt
```

Prints a ranked, categorized critique of the domains.

## Architecture

| Module | Responsibility |
|--------|----------------|
| `config.py`  | Load & validate settings from `.env` |
| `models.py`  | Pydantic schema for LLM output |
| `llm.py`     | Azure OpenAI calls (find / evaluate) |
| `godaddy.py` | Domain-availability lookups |
| `speech.py`  | Optional text-to-speech |
| `storage.py` | Persist discovered domains |
| `main.py`    | CLI entry point |

## Caveats

Use the **production** GoDaddy endpoint (`https://api.godaddy.com`). The OTE
sandbox (`https://api.ote-godaddy.com`) returns **fake data** — canned prices
and unreliable availability — so domains it reports as free may in fact be
taken. OTE and production use different key/secret pairs. Note that access to
`/v1/domains/available` in production may require an account holding a minimum
number of domains.

Even in production, the code ignores non-definitive availability results (fast
heuristic guesses) to avoid false positives. The GoDaddy API may still not
return the final price or whether hiring their broker is required, so verify on
their website once you find a domain of interest.
