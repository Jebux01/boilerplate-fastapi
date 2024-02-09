# Boilerplate FastAPI, SQLALCHEMY

## IMPORTANTE
Si en algun punto esto es complejo o falta informacion por mostrar
Con todo gusto podemos seguir dando manto al proyecto

## Presentacion

Hola, gracias por tomar mi repositorio ya sea para empezar con fastapi, para iniciar un proyecto nuevo, o simplemente para bardearlo.

En mis proyectos tenia que empezar a generar microservicios tenia que volver a "re-estructura" un proyecto que funcionaba para generar uno nuevo
Esta perdida de tiempo me dio la idea de crear este boilerplate, que en rasgos generales utilizo las siguientes 3 (Frameworks/Librerias)

- FastAPI
- SQLALCHEMY
- python-jose

Con los requerimientos anteriores se logra crear un boilerplate para empeza un proyecto en menos de 5 min, la idea de usar [FastAPI] es disminuir el tiempo de desarrollo que lleva un Desarrollador el empezar un proyecto completamente nuevo, simplificando mucho el tiempo de configuracion. [SQLALCHEMY] el conectarse a una instancia SQL en general no esta ligado a un solo motor, he dejado un Dockerfile.mssql que instala Microsoft SQL SERVER, realmente mariadb, mysql, etc. Pueden ser agregados con gran facilidad, la idea es no utilizar el ORM para no empezar a generar modelos, si no que trabajes simplemente con una instancia ya existente. [python-jose] una libreria en seguridad (JavaScript Object Signing and Encryption), implementando en este proyecto JWT.



### Technology
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)  
[![Build Status](https://img.shields.io/badge/build-develop-pass.svg)](https://shields.io/)
[![Coverage](https://img.shields.io/badge/coverage-process-blue.svg)](https://shields.io/)
[![Testing](https://img.shields.io/badge/testing-process-blue.svg)](https://shields.io/)


install dependencies
```
pyenv virtualenv template
pyenv activate template
pip3 install -r requirements.txt
pip3 install pre-commit
pre-commit install
```

Run pre-commit checks
```
pre-commit run --all-files
```

Run unit tests
```
pytest --cov -v
coverage html   (genera reporte html)
```

Run checks
```
flake8 .
black .    (formatea código)
```

---


## Uso Docker

### Iniciar proyecto
```sh
docker-compose up --build
```

### Terminar proyecto
```sh
docker-compose down
```

## Puntos importantes a mencionar
Si quieres cambiar el motor a cual te quieres conectar
Este archivo sera el siguiente 
``` Bash
/app/db/config.py
```