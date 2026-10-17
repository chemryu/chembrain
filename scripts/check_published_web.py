"""Check actual Pages responses against the recorded code/data build identity."""
import json, sys, time, urllib.request
from urllib.parse import urlsplit
from web_provenance import validate_identity, verify_payload

def main():
    url = sys.argv[1].rstrip('/')+'/'
    expected = validate_identity(json.loads(sys.argv[2]))
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or not parsed.hostname.endswith('.github.io'):
        raise SystemExit('Expected a GitHub Pages HTTPS URL')
    for attempt in range(12):
        try:
            def get(path):
                request = urllib.request.Request(url+path+'?build='+expected['built_commit'], headers={'Cache-Control':'no-cache'})
                with urllib.request.urlopen(request, timeout=10) as response:
                    return response.read(5_000_001)
            verify_payload(expected, json.loads(get('version.json')), get('library.json'), get(''))
            print('PAGES_HTTP_PASS: workflow source, actual built commit and exact library SHA-256 match over public HTTPS')
            return
        except Exception as error:
            if attempt == 11:
                raise SystemExit('Pages HTTP verification unavailable or stale: '+type(error).__name__)
            time.sleep(4)

if __name__ == '__main__':
    main()
