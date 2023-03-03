from bs4 import BeautifulSoup
from urllib.parse import urlparse
from http.client import HTTPConnection
from contextlib import closing
import sys
import timeit

def get_images_src_from_html(html_doc):    
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

def wget(uri):    
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

def download(uri):    
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
    
def get_images(page_uri):    
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
        download(image_uri) 

if __name__ == '__main__':    
    print('--- Starting standard download ---')    
    web_page_uri = 'http://jardinesrinconcillo.com/'    
    print("Tiempo de ejecución: ", timeit.timeit('get_images(web_page_uri)', number=1, setup="from __main__ import get_images, web_page_uri"))