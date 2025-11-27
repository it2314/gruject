import os
import sys

# Ensure project root is on sys.path so `import app` works when pytest changes cwd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app


def test_index_get():
    client = app.test_client()
    r = client.get('/')
    assert r.status_code == 200
    assert b'Contact us' in r.data
