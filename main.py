from utils import check_domains_availability, find_domain, extract_domain_names, text_to_speech
import logging
import json
import time

# Configure logging  
logging.basicConfig(level=logging.INFO) 

if __name__ == "__main__":

    # from promptflow.tracing import start_trace
    # start_trace()

    with open("user.md", "r", encoding="utf-8") as file:  
        content = file.read()

    while True:
        try:
            suggested_domains = find_domain(content)
            # logging.info(suggested_domains)
            listed_domains = extract_domain_names(suggested_domains)

            if len(listed_domains) > 0:
                try:
                    availability = check_domains_availability(listed_domains)
                    for domain, price in availability.items():
                        logging.info(f"{domain} available at: {price}")
                        
                        # text to speech
                        text_to_speech(domain)

                        # save available domains in file
                        with open("domains.txt", "a+") as domain_file:
                            file_contents = domain_file.read()
                            if domain not in file_contents:
                                domain_file.write(domain+", ")
                except TypeError as e:
                    logging.error(f"Type error while checking domain availability: {e}")

            else:
                logging.info(f"Empty domain list")

        except (json.decoder.JSONDecodeError, KeyError) as e:
            logging.error(f"Error parsing JSON: {e}")
        
        # Wait x seconds before looping to avoid rate limit errors with Azure OpenAI
        time.sleep(1)