# NickyGPT

NickyGPT es una aplicación desarrollada en Python que integra una interfaz gráfica para gestionar usuarios en una base de datos SQLite y interactuar con el modelo GPT de OpenAI. Esta aplicación permite realizar diversas operaciones como añadir, eliminar, y modificar usuarios, así como realizar consultas específicas a través de comandos en lenguaje natural procesados por GPT.

## Características

- Gestión de usuarios en base de datos SQLite.
- Interfaz gráfica con `customtkinter`.
- Integración con la API de OpenAI para procesamiento de lenguaje natural.
- Operaciones CRUD completas a través de comandos en texto.

## Instalación

Para ejecutar NickyGPT, necesitarás Python y algunas bibliotecas externas. Aquí están los pasos para configurar tu entorno:

### Prerrequisitos

Asegúrate de tener Python instalado en tu sistema. Puedes descargarlo desde [python.org](https://www.python.org/downloads/).

### Clonar el repositorio

Primero, clona este repositorio en tu máquina local usando Git:

```bash
git clone https://github.com/tu-usuario/nickygpt.git
cd NickyGPT
#Haz doble click sobre el ejecutable

```
### Problemas al ejecutar
Si al ejecutar con docble click no se ha ejecutado escribe esto en el terminal:
```
#Windows
NickyGPT_Windows.exe

#Linux
./NickyGPT_Linux

```
Si asi tampoco se ejecuta instala las siguientes bibliotecas:
```
pip install requests
pip install customtkinter
