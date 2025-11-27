# Flask WTForms example

This small project demonstrates a Flask app with a WTForms contact form, a script to create a virtual environment, a Dockerfile suitable for Kubernetes, and a minimal test.

How to run locally (venv):

```bash
./scripts/setup_venv.sh
source .venv/bin/activate
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

Build Docker image:

```bash
docker build -t flask-wtforms-example:latest .
```

Kubernetes (simple Deployment):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-wtforms
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask-wtforms
  template:
    metadata:
      labels:
        app: flask-wtforms
    spec:
      containers:
      - name: app
        image: flask-wtforms-example:latest
        ports:
        - containerPort: 5000
```
