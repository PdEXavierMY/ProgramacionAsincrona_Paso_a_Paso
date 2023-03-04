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