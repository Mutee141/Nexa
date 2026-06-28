import re
import requests
from bs4 import BeautifulSoup

BASE = 'http://127.0.0.1:8001'
LOGIN_URL = BASE + '/accounts/login/'
DASH_URL = BASE + '/dashboard/'

s = requests.Session()
resp = s.get(LOGIN_URL)
print('login status', resp.status_code)
if resp.status_code != 200:
    print(resp.text[:1000])
    raise SystemExit(1)

soup = BeautifulSoup(resp.text, 'html.parser')
csrf = soup.find('input', attrs={'name': 'csrfmiddlewaretoken'})
if not csrf:
    print('no csrf token')
    raise SystemExit(1)
token = csrf['value']

# Replace with credentials of a known user.
email = 'testuser@example.com'
password = 'TestPass123!'

login_data = {
    'csrfmiddlewaretoken': token,
    'login': email,
    'password': password,
    'remember': 'True',
}

headers = {'Referer': LOGIN_URL}
login_resp = s.post(LOGIN_URL, data=login_data, headers=headers)
print('post login status', login_resp.status_code)
print('redirects', login_resp.history)

resp2 = s.get(DASH_URL)
print('dashboard status', resp2.status_code)
print(resp2.text[:2000])
