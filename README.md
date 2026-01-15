# Flask WTForms example

This small project demonstrates a Flask app with a WTForms contact form, a script to create a virtual environment, a Dockerfile suitable for Kubernetes, and a minimal test.

How to run locally (venv):

```bash
./scripts/setup_venv.sh
# Flask WTForms example

Krátký návod jak spustit projekt lokálně, v Dockeru a v Kubernetes — včetně příkazů.

Požadavky
- nainstalovaný `python3`, `docker` (pro Docker/Postgres), `kubectl` pokud chcete použít Kubernetes

1) Lokální vývoj (virtuální prostředí + sqlite)

```bash
# vytvoření virtuálního prostředí (poprvé)
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
# pro lokální vývoj používáme requirements-dev (vynechává mysqlclient)
pip install -r requirements-dev.txt

# spustit aplikaci (použije SQLite data.db pokud není DATABASE_URL)
export SECRET_KEY='muj_secret'
python app.py

# v prohlížeči otevřít http://localhost:5000
```

2) Spuštění lokálního Postgres (Docker) a připojení aplikace

```bash
# spustit Postgres kontejner
docker rm -f mypg || true
docker run -d --name mypg \
  -e POSTGRES_USER=pguser -e POSTGRES_PASSWORD=pgpass -e POSTGRES_DB=mydb \
  -p 5432:5432 postgres:15

# nastavit proměnné a spustit aplikaci (pouze pokud chcete běžet lokálně, ne v Dockeru)
source venv/bin/activate
export DATABASE_URL='postgresql://pguser:pgpass@localhost:5432/mydb'
export SECRET_KEY='muj_secret'
python app.py

# ověření tabulek / dat
docker exec -it mypg psql -U pguser -d mydb -c "\dt"
docker exec -it mypg psql -U pguser -d mydb -c "SELECT id,name,email,message FROM message ORDER BY id DESC LIMIT 10;"
```

3) Spuštění aplikace v Dockeru (vývojová image)

```bash
# použít dev image která používá requirements-dev.txt (nevyžaduje mysqlclient systémové knihovny)
docker build -f Dockerfile.dev -t gruject:dev .

# pokud běží lokální Postgres, spusťte kontejner připojený k němu
docker rm -f gruject || true
docker run -d --name gruject --link mypg:postgres \
  -e DATABASE_URL='postgresql://pguser:pgpass@postgres:5432/mydb' \
  -e SECRET_KEY='muj_secret' -p 5000:5000 gruject:dev

# přistupte na http://localhost:5000
```

Poznámka: Pokud chcete postavit produkční image použijte `Dockerfile` (obsahuje `requirements.txt`), ale může být nutné nainstalovat systémové závislosti pokud tam máte `mysqlclient`.

4) Spuštění testů

```bash
source venv/bin/activate
pytest -q
```

5) Kubernetes (rychlé nasazení ukázky)

```bash
# vytvořte secret (obsahuje POSTGRES_* a SECRET_KEY)
kubectl apply -f k8s/secret.yaml
# nasadit Postgres (pouze pro testy; v produkci použijte PVC)
kubectl apply -f k8s/postgres-deployment.yaml
# nasadit web aplikaci
kubectl apply -f k8s/app-deployment.yaml

# zkontrolujte logy a služby
kubectl get pods
kubectl logs deployment/web
```

6) Kde jsou data uložena
- výchozí: `data.db` (SQLite) v kořenovém adresáři projektu, pokud není nastavena proměnná `DATABASE_URL`
- při použití Postgres: tabulka `message` v DB (v našem příkladu databáze `mydb`)

7) Rychlé debug / tipy
- Pokud během instalace `pip install -r requirements.txt` narazíte na chybu při sestavování `mysqlclient`, použijte `requirements-dev.txt` nebo nainstalujte systémové balíčky (`libmysqlclient-dev`, `default-libmysqlclient-dev` apod.).
- Aplikace loguje použité `SQLALCHEMY_DATABASE_URI` při startu — dávejte pozor na publikování citlivých údajů v produkci.

Máte-li zájem, můžu upravit `Dockerfile` tak, aby používal `requirements-dev.txt` nebo přidat krok pro `Flask-Migrate` do projektu.

