<img src="images/logo-teal.png" style="float: left; margin-right: 10px;" />

FastAPI est un framework python qui permet de mettre en place des API robustes, performantes, faciles à maintenir.

Ce projet vise à montrer de façon simple la création d'une API sécurisée avec FastAPI. Dans notre exemple, nous allons construire une API qui fourit le numéro et le type d'une carte bancaire à partir de l'image.

**Déploiement du service**

```bash

mkdir demo-docker
cd demo-docker
git clone https://github.com/fayeab/fastapi-ocr-credit-card.git
cd fastapi-ocr-credit-card/

# Construire une nouvelle image docker
cd code
docker images
docker build -t demo-docker .
docker images

# Lancer le container
docker run -d --name demo-doc -p 8000:8000 -e USERNAME=username -e PWD=changeme demo-docker:latest
```

**Tests de l'API**

On a deux façons de tester l'API:

* Avec l'interface fournie par FastAPI (http://127.0.0.1:8000/docs)

<img src="images/test_fastapi.png" style="float: left; margin-right: 10px;" />

* En voyant une requête directement à l'API:

```python
import requests

# Créer un token
url_auth = 'http://127.0.0.1:8000/token'
data = dict(username='username', password='changeme')
response = requests.post(url_auth, json=data)
jsonData = response.json()
token = jsonData['access_token']

# Appeler l'API
image_path =  'carte_visa_1.jpg'
image_data = open(image_path, "rb").read()
data_str = image_data.decode('ISO-8859-1')
url_ocr = 'http://127.0.0.1:8000/ocr_image_string'
headers = {'Authorization' : 'Bearer ' + token}
response = requests.post(url_ocr, json={'image_str': data_str},  headers=headers)
response.json()
```

Le résultat de la requête est :

```
{'carte_num': '4970101234567890', 'carte_type': 'Visa'}
```