# Update Pypi Package


```shell
python3 -m twine upload dist/*

# Instalar las herramientas necesarias
pip install build twine

# Construir el paquete
python3 -m build

# Subir a PyPI (necesitarás tu API token)
python3 -m twine upload dist/*
```