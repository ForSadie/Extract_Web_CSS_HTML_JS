import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re

def sanitizar_nombre_archivo(nombre_archivo):
    """
    Sanitiza el nombre de un archivo para eliminar caracteres problemáticos
    """
    nombre_archivo = re.sub(r'[\\/*?:<>|"]', '', nombre_archivo)  # Eliminar caracteres problemáticos
    nombre_archivo = re.sub(r'\s+', '_', nombre_archivo)  # Normalizar espacios en blanco a guiones bajos
    if not nombre_archivo:  # Manejar el caso donde el nombre queda vacío
        return None
    return nombre_archivo

def descargar_recurso(url, directorio, extension):
    """
    Descarga un recurso y lo guarda en un archivo
    """
    try:
        respuesta = requests.get(url, stream=True)
        respuesta.raise_for_status()

        nombre_archivo = sanitizar_nombre_archivo(url.split("/")[-1])
        if not nombre_archivo:  # Manejar el caso donde el nombre queda vacío
            print(f"No se pudo obtener un nombre válido para el recurso {url}")
            return

        if not nombre_archivo.endswith(extension):  # Agregar la extensión si no la tiene
            nombre_archivo += extension

        ruta_archivo = os.path.join(directorio, nombre_archivo)

        with open(ruta_archivo, "wb") as archivo:
            for chunk in respuesta.iter_content(chunk_size=1024):
                archivo.write(chunk)

        print(f"Descargado {nombre_archivo}")

    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el recurso {url}: {e}")
    except OSError as e:
        print(f"Error al guardar el archivo {nombre_archivo}: {e}")

def extraer_recursos(url):
    """
    Extrae los recursos de una página web (JavaScript, CSS y HTML)
    """
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()

        soup = BeautifulSoup(respuesta.text, 'html.parser')

        scripts_js = []
        for script in soup.find_all('script'):
            src = script.get('src')
            if src:
                scripts_js.append(urljoin(url, src))  # Unir URLs relativas a la base

        archivos_css = []
        for link in soup.find_all('link', rel='stylesheet'): # Simplifica la búsqueda de CSS
            href = link.get('href')
            if href:
                archivos_css.append(urljoin(url, href)) # Unir URLs relativas a la base

        #  No es necesario prettify() si solo quieres el HTML.  Usa str(soup)
        contenido_html = str(soup)  # Obtener el HTML sin formato

        return scripts_js, archivos_css, contenido_html

    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return None, None, None
    except Exception as e: # Captura excepciones generales para debug
        print(f"Ocurrió un error inesperado: {e}")
        return None, None, None


def main():
    url = input("Ingrese la URL de la página web: ")
    scripts_js, archivos_css, contenido_html = extraer_recursos(url)

    if scripts_js is not None and archivos_css is not None and contenido_html is not None: # Mejor comprobación
        print("Recursos extraídos con éxito:")

        if scripts_js: # Evita imprimir si está vacío
            print("\nScripts de JavaScript:")
            for script in scripts_js:
                print(script)

        if archivos_css: # Evita imprimir si está vacío
            print("\nArchivos CSS:")
            for archivo in archivos_css:
                print(archivo)

        # Decide si quieres imprimir todo el HTML.  Puede ser *MUY* largo.
        # print("\nContenido HTML:")
        # print(contenido_html)  # Comentado por defecto.  Descomentar con precaución.

        directorio = "recursos"
        if not os.path.exists(directorio):
            os.makedirs(directorio)

        for script in scripts_js:
            descargar_recurso(script, directorio, ".js")

        for archivo in archivos_css:
            descargar_recurso(archivo, directorio, ".css")

        nombre_archivo = "index.html"
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(contenido_html)
        print(f"Guardado {nombre_archivo}")

    else:
        print("No se pudieron extraer los recursos.")

if __name__ == "__main__":
    main()
