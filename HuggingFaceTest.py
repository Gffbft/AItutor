
import requests.exceptions

try:
    r = requests.get('https://sharegpt.churchless.tech/share/v1/chat')
    r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
    print ("Down")
except requests.exceptions.HTTPError:
    print ("4xx, 5xx")
else:
    print ("All good!")  # Proceed to do stuff with `r`
