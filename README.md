# ProgramacionAsincrona_Paso_a_Paso

Pincha [aquí](https://github.com/Xavitheforce/ProgramacionAsincrona_Paso_a_Paso) para dirigirte a mi repositorio.

En esta entrega programamos de diferentes maneras un recolector de imágenes html. La primera de estas es programacion asíncrona, que basa su utilidad en poder ejecutar varios procesos necesarios para el algoritmo sin estancarse en la recogida de datos. Para comprobar la funcionalidad del código, hemos pedido a nuestro algoritmo que extrayese las imágenes de la siguiente url: http://jardinesrinconcillo.com/

El código ejecutado (asíncrono) es el siguiente:

```python
from functools import partial
import aiohttp
import asyncio # librería para la ejecución asíncrona
from bs4 import BeautifulSoup # librería para el análisis de documentos HTML
from urllib.parse import urlparse # librería para el análisis de URIs
import sys
import timeit
# importamos las librerías necesarias


async def wget(session, uri):  # Devuelve el contenido indicado por una URI (asincrona)
    async with session.get(uri) as response:  # Abrimos la sesión con la URI y la guardamos en response
        if response.status != 200:  # Si el estado de la respuesta no es 200 (OK) devolvemos None
            return None  
        if response.content_type.startswith("text/"):  # Si el tipo de contenido es texto lo devolvemos como texto
            return await response.text()
        else:
            return await response.read()

'''async def download(session, uri):  
    content = await wget(session, uri)  
    if content is None:  
        return None
    sep="/" if "/" in uri else "\\"
    with open(uri.split(sep)[-1], "wb") as f:
        f.write(content)  
        return uri'''

async def get_images_src_from_html(html_doc):  # Función para obtener las imágenes (html) de una página web
    soup = BeautifulSoup(html_doc, "html.parser") # Creamos un objeto BeautifulSoup a partir del documento HTML
    for img in soup.find_all('img'): # Recorremos todas las etiquetas img del documento HTML
        yield img.get('src') # Devolvemos el src de cada imagen
        await asyncio.sleep(0.001) # Esperamos 0.001 segundos

async def get_uri_from_images_src(base_uri, images_src):  # Función para obtener las uris de las imagenes dado el src
    """Devuelve una a una cada URI de imagen a descargar"""
    parsed_base = urlparse(base_uri) # Parseamos la URI base
    async for src in images_src: # Recorremos el generador de imágenes (asincrono)
        parsed = urlparse(src)
        if parsed.netloc == '': # Si no tiene netloc, es una URI relativa
            path = parsed.path # Obtenemos el path de la URI relativa
            if parsed.query: # Si tiene query, la añadimos al path
                path += '?' + parsed.query
            if path[0] != '/': # Si el path no empieza por /, lo añadimos
                if parsed_base.path == '/':
                    path = '/' + path
                else: # Si el path de la URI base no es /, lo eliminamos
                    path = '/' + '/'.join(parsed_base.path.split('/')[:-1]) + '/' + path
            yield parsed_base.scheme + '://' + parsed_base.netloc + path # Devolvemos la URI absoluta
        else: # Si tiene netloc, es una URI absoluta
            yield parsed.geturl() # Devolvemos la URI absoluta
        await asyncio.sleep(0.001) # Esperamos 0.001 segundos

async def get_images(session, page_uri):  # Función para obtener y empezar a descargar las imágenes de una página web
    html = await wget(session, page_uri)  # Obtenemos el contenido de la página web
    if not html:  # Si no se ha obtenido nada, devolvemos None
        print("Error: no se ha encontrado ninguna imagen", sys.stderr)  
        return None  
    images_src_gen = get_images_src_from_html(html)  
    images_uri_gen = get_uri_from_images_src(page_uri, images_src_gen)  
    async for image_uri in images_uri_gen:  # Recorremos el generador de imágenes (asincrono)
        print('Descarga de %s' % image_uri)  
        await download(session, image_uri) # Descargamos la imagen

async def main():  # Función principal ejecutadora
    web_page_uri = 'http://jardinesrinconcillo.com/'
    async with aiohttp.ClientSession() as session:
        await get_images(session, web_page_uri)




def write_in_file(filename, content):   # Función para escribir el contenido de una URI en un fichero
    with open(filename, "wb") as f:   
        f.write(content)

async def download(session, uri):  # Función para descargar el contenido de una URI
    content = await wget(session, uri)
    if content is None:  
        return None 
    sep="/" if "/" in uri else "\\"
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, partial(write_in_file, uri.split(sep)[-1], content))
    return uri

event_loop = asyncio.new_event_loop() # Creamos un nuevo bucle de eventos
asyncio.set_event_loop(event_loop) # Establecemos el nuevo bucle de eventos como el bucle de eventos por defecto

if __name__ == '__main__':
    web_page_uri = 'http://jardinesrinconcillo.com/'
    print("Tiempo de ejecución: ", timeit.timeit('event_loop.run_until_complete(main())', number=1, setup="from __main__ import event_loop, main"))     
```

Las imágenes obtenidas son las siguientes:

![loading](https://user-images.githubusercontent.com/91721699/222955998-5054c54f-c056-4de9-92ab-02d57eef17d4.gif)

![logo](https://user-images.githubusercontent.com/91721699/222956015-e87cb1b7-3915-460e-80ee-e0f1fcaa7b90.png)

![logo_arbol_verde_v2](https://user-images.githubusercontent.com/91721699/222956024-632b5f28-4321-45e8-8163-c62065757ae3.png)

![plano](https://user-images.githubusercontent.com/91721699/222956031-9c32f44b-1ad6-48bc-a3e8-36312d1a22e5.png)


Si nos fijamos al final del código, en el apartado del main, pedimos a nuestro algoritmo que mida el tiempo de ejecución con la libreria timeit para poder a posteriori comparárlo con nuestro segundo algoritmo para este problema. El output de este main, además de la descarga de las imágenes anteriores, es:

![tiempo-asincrono](https://user-images.githubusercontent.com/91721699/222956081-0653764f-8401-4024-a134-4ca177c600e5.png)

Para finalizar con esta entrega, se ha comparado la programación asíncrona desarrollada con una programación funcional normal a base de generadores en python. El código de este último algoritmo es el siguiente:

```python
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from http.client import HTTPConnection
from contextlib import closing
import sys
import timeit

def get_images_src_from_html(html_doc):  # Función para obtener las imágenes (html) de una página web
    """Recupera todo el contenido de los atributos src de las etiquetas 
img"""   
    soup = BeautifulSoup(html_doc, "html.parser")    
    return (img.get('src') for img in soup.find_all('img'))

def get_uri_from_images_src(base_uri, images_src):   
    """Devuelve una a una cada URI de la imagen a descargar"""
    parsed_base = urlparse(base_uri)
    for src in images_src:    
        parsed = urlparse(src)
        if parsed.netloc == '':    
            path = parsed.path    
            if parsed.query:    
                path += '?' + parsed.query    
            if path[0] != '/':    
                if parsed_base.path == '/':    
                    path = '/' + path    
                else:    
                    path = '/' + '/'.join(parsed_base.path.split('/')[:-1]) + '/' + path 
            yield parsed_base.scheme + '://' + parsed_base.netloc + path  
        else:    
            yield parsed.geturl()

def wget(uri):  # Función para descargar una página web
    """    
    Devuelve el contenido indicado por una URI    
   
    Argumento:    
    > uri (str, por ejemplo 'http://inspyration.org')    
   
    Retorno:    
    > contenido de un archivo (bytes, archivo textual o binario)    
    """    
    # Análisis de la URI    
    parsed = urlparse(uri)    
    # Apertura de la conexión    
    with closing(HTTPConnection(parsed.netloc)) as conn:   
        # Ruta en el servidor    
        path = parsed.path    
        if parsed.query:    
            path += '?' + parsed.query    
        # Envío de la consulta al servidor    
        conn.request('GET', path)    
        # Recuperación de la respuesta    
        response = conn.getresponse()    
        # Análisis de la respuesta    
        if response.status != 200:    
            # 200 = Ok, 3xx = redirection, 4xx = error client,   5xx = error servidor    
            print(response.reason, file=sys.stderr)
            return None
        # Devuelve la respuesta si todo está OK.    
        print('Respuesta OK')
        return response.read()

def download(uri):  # Función para descargar una imagen
    """    
    Guarda en el disco duro un archivo designado por una URI   
    """    
    content = wget(uri)    
    if content is None:    
        return None
    sep = '/' if '/' in uri else '\\'
    with open(uri.split(sep)[-1], 'wb') as f:    
        f.write(content)    
        return uri 
    
def get_images(page_uri):  # Función para obtener las imágenes de una página web
    #    
    # Recuperación de las URI de todas las imágenes de una página    
    #    
    html = wget(page_uri)    
    if not html:    
        print("Error: no se ha encontrado ninguna imagen ", sys.stderr) 
        return None    
    images_src_gen = get_images_src_from_html(html)    
    images_uri_gen = get_uri_from_images_src(page_uri, images_src_gen)   
    #    
    # Recuperación de las imágenes    
    #    
    for image_uri in images_uri_gen:    
        print('Descarga de %s' % image_uri)    
        download(image_uri) # Descarga de la imagen

if __name__ == '__main__':    
    print('--- Starting standard download ---')    
    web_page_uri = 'http://jardinesrinconcillo.com/'    
    print("Tiempo de ejecución: ", timeit.timeit('get_images(web_page_uri)', number=1, setup="from __main__ import get_images, web_page_uri"))
```

Al igual que con el primer código, se ha usado de referencia la página http://jardinesrinconcillo.com/ , de la que se han extraido las mismas imágenes:

![loading](https://user-images.githubusercontent.com/91721699/222955998-5054c54f-c056-4de9-92ab-02d57eef17d4.gif)

![logo](https://user-images.githubusercontent.com/91721699/222956015-e87cb1b7-3915-460e-80ee-e0f1fcaa7b90.png)

![logo_arbol_verde_v2](https://user-images.githubusercontent.com/91721699/222956024-632b5f28-4321-45e8-8163-c62065757ae3.png)

![plano](https://user-images.githubusercontent.com/91721699/222956031-9c32f44b-1ad6-48bc-a3e8-36312d1a22e5.png)

El output, también medido con timeit, es:

![tiempo-generadores](https://user-images.githubusercontent.com/91721699/222956096-280d14b8-9c85-47d2-ba0d-7a8ddc77655a.png)

Como conclusión, la programación asíncrona proporciona grandes beneficios cuando se quiere agilizar el tiempo de ejecución de un programa diseñado para compartir recursos, y esta afirmación queda respaldada por la diferencia, pequeña pero importante, de tiempos finales entre ambos programas.
