from app import app

with app.app_context():
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    r = client.post('/', data={'name':'Integration Test','email':'test@example.com','message':'Hello from test'}, follow_redirects=True)
    print('status', r.status_code)
