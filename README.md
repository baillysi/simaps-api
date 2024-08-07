# simaps-api :gear:	

Python REST API with Flask, server-side of [Kavalé](https://kavaleapp.com) web application. See [client-side](https://github.com/baillysi/simaps-client) to get more information :v:.

## Description

simaps-api provides a REST API to handle CRUD operations on various data, like hikes. It uses sqlalchemy ORM.

## Development

### Requirements

- Conda >= 23.3.1
- Docker >= 24.0.7
- Google SA to access Firebase services [see more](https://firebase.google.com/docs/admin/setup?hl=fr#python)
  
### Environment
```
conda conda create --name simaps-api python=3.11
conda activate simaps-api
export ENV=dev
export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/service-account-file.json"
```

### Setup Database with docker-compose
```
docker-compose up --build
```
exposed on local port 5431

### Test
```
pytest
```

### Run 
```
python -m wsmain.app
```
served on http://localhost:5001

## Production & deployment

Continuous integration with Cloud Run by Google Cloud Platorm.
