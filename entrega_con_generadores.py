from bs4 import BeautifulSoup
import urllib.parse

def get_images_src_from_html(html_doc):    
    """Recupera todo el contenido de los atributos src de las etiquetas 
img"""   
    soup = BeautifulSoup(html_doc, "html.parser")    
    return (img.get('src') for img in soup.find_all('img'))

def get_uri_from_images_src(base_uri, images_src):   
    """Devuelve una a una cada URI de la imagen a descargar"""
    parsed_base = urllib.parse.urlparse(base_uri)
    for src in images_src:    
        parsed = urllib.parse.urlparse(src)
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