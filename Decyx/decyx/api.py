# api.py
# @runtime Jython

# Note: Decyx doesn't use Anthropic's official python API as it is intended for Python 3+

import json
import os
import urllib2
from config import OLLAMA_API_URL

def send_request(url, headers, data):
    """Send a POST request to the specified URL with the given headers and data.

    Args:
        url (str): The URL to send the request to.
        headers (dict): A dictionary of HTTP headers to include in the request.
        data (dict): The data to send in the body of the request.

    Returns:
        urllib2.Response or urllib2.HTTPError: The response object returned by the server.
    """
    req = urllib2.Request(url, json.dumps(data), headers)
    try:
        response = urllib2.urlopen(req)
        return response
    except urllib2.HTTPError as e:
        return e
    except urllib2.URLError as e:
        print "Failed to reach server: {}".format(e.reason)
        return None

def read_response(response):
    """Read the response from the response object.

    Args:
        response (urllib2.Response or urllib2.HTTPError): The response object returned by send_request.

    Returns:
        str: The content of the response as a string, or None if an error occurred.
    """
    if response is None:
        return None
    elif isinstance(response, urllib2.HTTPError):
        error_content = response.read()
        print "Error: HTTP response code {}".format(response.code)
        print "Error message: {}".format(error_content) 
        return None
    else:
        content = response.read()
        return content

def parse_json_response(content):
    """Parse the JSON response from Claude API.

    Args:
        content (str): The response content as a string.

    Returns:
        dict: The parsed JSON object, or None if parsing failed.
    """

    def find_json_object(s):
        # Find first balanced JSON object in the string.
        start = s.find('{')
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(s)):
            ch = s[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return s[start:i + 1]

        return None

    json_str = find_json_object(content)
    if not json_str:
        print "No JSON object found in Claude's response"
        return None

    try:
        return json.loads(json_str)
    except ValueError as e:
        # Try to fix common JSON issues
        print "Initial JSON parse failed: {}".format(str(e))
        print "Attempting to fix common JSON issues..."

        # Replace invalid escape sequences with placeholders or remove them
        import re
        # Replace backslash followed by invalid escape characters
        json_str = re.sub(r'\\([^"\\\/bfnrtu])', r'\1', json_str)

        try:
            return json.loads(json_str)
        except ValueError as e2:
            print "Failed to parse JSON even after fixing escapes: {}".format(str(e2))
            print "=== JSON snippet ==="
            print json_str

    return None

def get_response_from_claude(prompt, model, monitor, is_explanation=False):
    """Get a response from the Claude API.

    Args:
        prompt (str): The prompt to send to the Claude API.
        api_key (str): The API key for authentication.
        model (str): The model name to use.
        monitor (object): An object with a setMessage method to display status messages.
        is_explanation (bool, optional): Flag indicating if the response is an explanation. Defaults to False.

    Returns:
        dict or str: The parsed JSON response, or the content string if is_explanation is True.
    """
    try:
        monitor.setMessage("Sending request to Ollama API...")
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.2,
        }

        print "Sending request to Ollama API..."
        response = send_request(OLLAMA_API_URL, headers, data)

        monitor.setMessage("Waiting for response from Ollama API...")
        content = read_response(response)

        if content:
            print "Received response from Ollama API."
            response_json = json.loads(content)
            content_text = response_json['choices'][0]['message']['content']

            # Debug: save the raw model response to a file for inspection
            debug_path = os.path.join(os.path.dirname(__file__), "llm_last_response.txt")
            try:
                with open(debug_path, "w") as f:
                    if isinstance(content_text, unicode):
                        f.write(content_text.encode('utf-8'))
                    else:
                        f.write(content_text)
                print "Saved raw LLM response to {}".format(debug_path)
            except Exception as e:
                print "Failed to write LLM response debug file: {}".format(e)

            if is_explanation:
                return content_text.strip()

            parsed = parse_json_response(content_text)
            if parsed is None:
                print "Failed to parse JSON response. See {} for raw output.".format(debug_path)
            return parsed

        return None

    except Exception as e:
        print "Exception in get_response_from_claude: {}".format(e)
        return None
    finally:
        monitor.setMessage("")
