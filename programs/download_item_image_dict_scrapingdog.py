"""
ScrapingDog - Download Item Images from Excel List
This script reads an Excel file containing a list dicts, gettting the 'VendorParNumber' as item, 
searches for the first image of each item using the SerpApi, and downloads it to a specified directory.
Also generates a excel file with all the urls found for each item, and a separate excel file with 
the items that had errors during the process.
"""

from functools import wraps
from serpapi import GoogleSearch
import openpyxl
import pandas as pd
from urllib import request, response
from time import time
from datetime import datetime
import json
import ssl
import os
import aiohttp
import asyncio
from pathlib import Path
import ssl
import certifi
from dotenv import load_dotenv


load_dotenv()

ssl._create_default_https_context = ssl._create_unverified_context


def count_elapsed_time(f):
    @wraps(f)
    async def async_wrapper(*args, **kwargs):
        start_time = time()
        ret = await f(*args, **kwargs)
        elapsed_time = time() - start_time
        print(f"Task: {f.__name__}. Elapsed time: %0.4f seconds." % elapsed_time)
        return ret

    @wraps(f)   
    def sync_wrapper(*args, **kwargs):
        start_time = time()
        ret = f(*args, **kwargs)
        elapsed_time = time() - start_time
        print(f"Task: {f.__name__}. Elapsed time: %0.4f seconds." % elapsed_time)
        return ret
    return async_wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper

@count_elapsed_time
async def download_first_image(item, urls_search, errors, i, api_key, session, semaphore: asyncio.Semaphore):        # SerpApi
    item_urls = [item]

    url = "https://api.scrapingdog.com/google_images"

    params = {
        "api_key": api_key,
        "query": item,
        "results": 10,
        "type": "photo"
    }

    print(i, params)

    try:
        async with semaphore:

            # ---- Call Scrapingdog (Fully Async) ----
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    print(f"❌ {item}: Scrapingdog error {response.status}")
                    errors.append(item)
                    return False

                data = await response.json()

            image_results = data.get("images_results", [])

            if not image_results:
                print(f"❌ {item}: No images found.")
                errors.append(item)
                return False

            url_imagen = image_results[0].get("image")

            if not url_imagen:
                print(f"❌ {item}: No valid image URL found.")
                errors.append(item)
                return False

            print("Image URL:", url_imagen)

            # ---- Download image ----
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }

            async with session.get(url_imagen, headers=headers, ssl=False) as img_response:
                data = await img_response.read()
                content_type = img_response.headers.get("Content-Type", "")

                print("Status:", img_response.status)
                print("Content-Type:", content_type)

            is_jpeg = data[:3] == b'\xff\xd8\xff'
            is_png  = data[:8] == b'\x89PNG\r\n\x1a\n'
            is_gif  = data[:3] == b'GIF'

            is_image = ("image" in content_type or is_jpeg or is_png or is_gif)

            if img_response.status == 200 and is_image:
                image_path = Path("programs/static/photos_api") / f"{item}.jpg"
                image_path.parent.mkdir(parents=True, exist_ok=True)

                with open(image_path, "wb") as handler:
                    handler.write(data)
            else:
                print(f"❌ {item}: Invalid image content.")
                errors.append(item)
                return False

        # ---- Store all URLs found ----
        for img in image_results:
            img_url = img.get("image")
            if img_url:
                item_urls.append(img_url)

        urls_search.append(list(item_urls))

        return True

    except Exception as e:
        print(f"❌ ERROR {item}: {e}")
        errors.append(item)
        return False
        

@count_elapsed_time
def read_excel(result) -> None :
    # Define variable to load the dataframe
    excel_path = Path("programs/static/files_to_read/lista_dicts.xlsx")
    dataframe = openpyxl.load_workbook(excel_path)
    sheet = dataframe.active

    for row in sheet.iter_rows(min_row=2, values_only=True):
        item = row[9]   # VendorPartNumber
        if isinstance(item, str) and item.strip().startswith("{"):
            parsed = json.loads(item.strip())
            result.append(parsed["vendorPartNumber"])

    print("Archivo Excel leido")
    return

@count_elapsed_time
async def dowmnload_images_list(result, errors, urls_search, init) -> None :
    API_KEY = os.getenv("SCRAPINGDOG_API_KEY")
    if not API_KEY:
        raise RuntimeError("SCRAPINGDOG_API_KEY not set in environment")

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:

        semaphore = asyncio.Semaphore(10)  # limit to 10 concurrent tasks

        tasks = []
        for i in range(len(result)):
            item = result[i]
            tasks.append(download_first_image(item, urls_search, errors, i, API_KEY, session, semaphore))

        await asyncio.gather(*tasks)


    print((len(result)-len(errors)),"Imagenes descargadas")
    print(len(errors), "items no encontrados")
    
    # Save all the urls found to an excel file
    results_path = Path("programs/static/results_excel/")
    datos = pd.DataFrame(urls_search)

    with pd.ExcelWriter(results_path / f"urls_sdog_{init}.xlsx") as writer:
        datos.to_excel(writer, sheet_name=init)


@count_elapsed_time
def print_errors(errors, init)-> None :
    datos = pd.DataFrame(errors)
    results_path = Path("programs/static/errores_excel/")
    results_path.mkdir(parents=True, exist_ok=True)
    
    file_path = results_path / f"errores_api_sdog_{init}.xlsx"

    with pd.ExcelWriter(file_path) as writer:
        datos.to_excel(writer, sheet_name=init)

    print("Reporte de errores generado")



@count_elapsed_time
async def main():
    now = datetime.now()
    init = str(now.strftime('day_%d_%m_%Y_time_%H_%M'))
    result = []
    errors = []
    urls_search = []        #create a list of urls found for each item for future use
    read_excel(result)

    if result:
        await dowmnload_images_list(result, errors, urls_search, init)

    if errors:
        print_errors(errors, init)
    else :
        print("No errors found")


if __name__ == "__main__":
    asyncio.run(main())