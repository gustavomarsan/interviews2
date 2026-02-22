"""
This script reads an Excel file containing a list dicts, gettting the 'VendorParNumber' as item, 
searches for the first image of each item using the SerpApi, and downloads it to a specified directory.
Also generates a excel file with all the urls found for each item, and a separate excel file with 
the items that had errors during the process.
https://serpapi.com/    to put in "api_key"  = 

"""
from functools import wraps
from serpapi import GoogleSearch
import openpyxl
import pandas as pd
from time import time
from datetime import datetime
import json
import ssl
import os
import aiohttp
import asyncio
from pathlib import Path
from file_manager import FileManager
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
async def download_first_image(item, urls_search, errors, i, api_key, session, semaphore: asyncio.Semaphore):
    item_urls = [item]      # set all the urls of the search
    params = {
        "q": item,
        "tbm": "isch",      # Modo imágenes
        "api_key": api_key  # key from SerpApi account
    }

    print(i, params)

    try:
        async with semaphore:
            
            resultados = await asyncio.to_thread(GoogleSearch(params).get_dict)

            if "images_results" not in resultados:
                errors.append(item)
                return False
            
            url_imagen = resultados["images_results"][0]["original"]

            if not url_imagen:
                print(f"❌ {item}: No image URL found in SerpAPI results.")
                errors.append(item)
                return False

            print(url_imagen)    


            headers = {
                "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
                )
            }

            async with session.get(url_imagen, headers=headers, ssl=False) as response:
                data = await response.read()
                content_type = response.headers.get("Content-Type", "")
                
                # Debug logs
                print("Status:", response.status)
                print("Content-Type:", content_type)

            is_jpeg = data[:3] == b'\xff\xd8\xff'
            is_png  = data[:8] == b'\x89PNG\r\n\x1a\n'
            is_gif  = data[:3] == b'GIF'            

            # Validate the content before writing the file
            is_image = ("image" in content_type or is_jpeg or is_png or is_gif)

            if response.status == 200 and is_image:
                image_path = Path("programs/static/photos_api") / f"{item}.jpg"
                image_path.parent.mkdir(parents=True, exist_ok=True)
                with open(image_path, "wb") as handler:
                    handler.write(data)
            else:
                print(f"❌ {item}: URL is not an image or request failed.")
                errors.append(item)
                return False

        # store all the urls found for future use
        for j in range(len(resultados["images_results"])) :
            item_urls.append(resultados["images_results"][j]["original"])
        
        urls_search.append(list(item_urls))
        return True
        
    except Exception as e:
        print(f"❌ ERROR {item}: {e}")
        errors.append(item)
        return False
        

@count_elapsed_time
def read_excel(result) -> None :
    excel_path = Path("programs/static/files_to_read/lista_dicts.xlsx")
    with FileManager(excel_path, "rb") as file:
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active

        for row in sheet.iter_rows(min_row=2, values_only=True):
            item = row[9]   # VendorPartNumber
            if isinstance(item, str) and item.strip().startswith("{"):
                parsed = json.loads(item.strip())
                result.append(parsed["vendorPartNumber"])

    return

@count_elapsed_time
async def dowmnload_images_list(result, errors, urls_search, init) -> None :
    API_KEY = os.getenv("SERPAPI_API_KEY")
    if not API_KEY:
        raise RuntimeError("SERPAPI_API_KEY not set in environment")

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(10)  # limit to 10 concurrent tasks

        tasks = []
        for i in range(len(result)):
            item = result[i]
            tasks.append(download_first_image(item, urls_search, errors, i, API_KEY, session, semaphore))

        await asyncio.gather(*tasks)


    print((len(result)-len(errors)),"Imagenes descargadas")
    print(len(errors), "items no encontrados")
    
    # Save all the urls found to an excel file
    datos = pd.DataFrame(urls_search)
    results_path = Path("programs/static/results_excel/")
    results_path.mkdir(parents=True, exist_ok=True)
    file_path = results_path / f"urls_{init}.xlsx"

    with FileManager(file_path, "wb") as file:
        with pd.ExcelWriter(file, engine='openpyxl') as writer:
            datos.to_excel(writer, sheet_name=init)


@count_elapsed_time
def print_errors(errors, init)-> None :
    datos = pd.DataFrame(errors)
    results_path = Path("programs/static/results_excel/")
    results_path.mkdir(parents=True, exist_ok=True)
    file_path = results_path / f"errores_api_{init}.xlsx"

    with FileManager(file_path, "wb") as file:
        with pd.ExcelWriter(file, engine='openpyxl') as writer:
            datos.to_excel(writer, sheet_name=init)



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