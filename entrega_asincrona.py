from functools import partial
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import sys


async def wget(session, uri):  
    async with session.get(uri) as response:  
        if response.status != 200:  
            return None  
        if response.content_type.startswith("text/"):  
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

async def get_images_src_from_html(html_doc):  
    soup = BeautifulSoup(html_doc, "html.parser")
    for img in soup.find_all('img'):
        yield img.get('src')
        await asyncio.sleep(0.001)

async def get_uri_from_images_src(base_uri, images_src):
    """Devuelve una a una cada URI de imagen a descargar"""
    parsed_base = urlparse(base_uri)
    async for src in images_src:
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
        await asyncio.sleep(0.001)

async def get_images(session, page_uri):  
    html = await wget(session, page_uri)  
    if not html:  
        print("Error: no se ha encontrado ninguna imagen", sys.stderr)  
        return None  
    images_src_gen = get_images_src_from_html(html)  
    images_uri_gen = get_uri_from_images_src(page_uri, images_src_gen)  
    async for image_uri in images_uri_gen:  
        print('Descarga de %s' % image_uri)  
        await download(session, image_uri)

async def main():  
    web_page_uri = 'http://jardinesrinconcillo.com/'
    async with aiohttp.ClientSession() as session:  
        await get_images(session, web_page_uri)




def write_in_file(filename, content):   
    with open(filename, "wb") as f:   
        f.write(content)

async def download(session, uri):  
    content = await wget(session, uri)  
    if content is None:  
        return None 
    sep="/" if "/" in uri else "\\"
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, partial(write_in_file, uri.split(sep)[-1], content))
    return uri

asyncio.run(main())
event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)
event_loop.run_until_complete(main())