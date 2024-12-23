import requests
import logging
# import http.client as http_client
import os
import azure.cognitiveservices.speech as speechsdk

from dotenv import load_dotenv
from pathlib import Path
# from promptflow.tracing import trace
from promptflow.core import Prompty, _errors

BASE_DIR = Path(__file__).absolute().parent

# @trace
def find_domain(question: str) -> str:
    """Flow entry function."""

    if "OPENAI_API_KEY" not in os.environ and "AZURE_OPENAI_API_KEY" not in os.environ:
        # load environment variables from .env file
        load_dotenv()

    prompty = Prompty.load(source=BASE_DIR / "find_domains.prompty")
    # trigger a llm call with the prompty obj
    try:
        output = prompty(question=question)
    except _errors.LLMError as e:
        output = {}
    return output

def extract_domain_names(domains):  
    """  
    Extracts a list of domain names from a JSON-like data structure.  
  
    Args:  
    - domains (dict): A dictionary containing a list of domain suggestions.  
  
    Returns:  
    - list: A list of domain names.  
    """  
    # Extract the "domain_suggestions" list and get all "domain" values
    try:
        return [item["domain"] for item in domains.get("domain_suggestions", [])]  
    except TypeError as e:
        logging.error(f"Type error: {e}")
        return []

def check_domains_availability(domains):
    """
    Check the availability of a list of domain names using the GoDaddy API.

    Args:
        domains (list): List of domain names to check.

    Returns:
        dict: A dictionary with domain names as keys and availability status as values.
    """

    load_dotenv()
    
    url = f"{os.environ['GODADDY_API_ENDPOINT']}/v1/domains/available?checkType=FULL"
    headers = {
        "Authorization": f"sso-key {os.environ['GODADDY_API_KEY']}:{os.environ['GODADDY_API_SECRET']}",
        "Content-Type": "application/json",
    }

    payload = domains

    try:

        # # These two lines enable debugging at httplib level (requests->urllib3->http.client)
        # # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
        # # The only thing missing will be the response.body which is not logged.
        # http_client.HTTPConnection.debuglevel = 1

        # # You must initialize logging, otherwise you'll not see debug output.
        # logging.basicConfig()
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        results = response.json()

        # Extract availability information
        availability = {}
        for domain_info in results.get("domains", []):
            if domain_info["available"] and (int(domain_info["price"]) < int(os.environ["MAX_USD_PRICE"])):
                logging.debug(f"{domain_info['domain']} available for {domain_info['currency']}{domain_info['price']}")
                availability[domain_info["domain"]] = domain_info["price"]
            elif domain_info["available"]:
                logging.debug(f"{domain_info['domain']} available but verify at " +
                    f"https://www.godaddy.com/fr/domainsearch/find?checkAvail=1&domainToCheck={domain_info['domain']}")
                availability[domain_info["domain"]] = f"Verify at " \
                    + f"https://www.godaddy.com/fr/domainsearch/find?checkAvail=1&domainToCheck={domain_info['domain']}"

        return availability
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while checking domain availability: {e}")
        return {}

def text_to_speech(text):
    """
    Convert text to speech using Azure Cognitive Services.

    Args:
        text (str): The text to be converted to speech.
    
    Returns:
        None

    Raises:
        Exception: If there is an error during speech synthesis.

    Logs:
        Info: When speech synthesis is completed successfully.
        Error: When speech synthesis is canceled or if there are error details.
    """
    
    subscription_key = os.environ.get("AZURE_SPEECH_TTS_KEY")
    region=os.environ.get("AZURE_SPEECH_TTS_REGION")
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        logging.info("Speech synthesized for text [{}]".format(text))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logging.error("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            logging.error("Error details: {}".format(cancellation_details.error_details))
