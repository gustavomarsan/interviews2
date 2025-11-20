"""
Programa para bajar imagenes de internet con numero de ITEM sin ligas
descraga la primera imagen de internet y genera un archivo de excel con 100 ligas por item

"""

import requests
from serpapi import GoogleSearch
import openpyxl
import pandas as pd
from urllib import request
from time import time
from datetime import datetime
import ssl
import os
ssl._create_default_https_context = ssl._create_unverified_context


# https://serpapi.com/    to put in line 42  "api_key"  = 

def count_elapsed_time(f):
    """
    Decorator.
    Execute the function and calculate the elapsed time.
    Print the result to the standard output.
    """
    def wrapper(*args, **kwargs):
        # Start counting.
        start_time = time()
        # Take the original function's return value.
        ret = f(*args, **kwargs)
        # Calculate the elapsed time.
        elapsed_time = time() - start_time
        print("Elapsed time: %0.10f seconds." % elapsed_time)
        return ret
    return wrapper

def descargar_primera_imagen(item, urls_search, errors, i, api_key):        # SerpApi
    item_urls = [item]      # set all the urls of the search
    params = {
        "q": item,
        "tbm": "isch",      # Modo imágenes
        "api_key": api_key   # key from SerpApi 
    }
    print(i, params)

    search = GoogleSearch(params)
    resultados = search.get_dict()
    #print(len(resultados["images_results"]))
    #print(type(resultados))
    if "images_results" in resultados:
        try :
            url_imagen = resultados["images_results"][0]["original"]
            img_data = requests.get(url_imagen).content
       
            with open("Documents/Cotizaciones 2025 Provicional/Catalogo 2025/imaganes_serpapi/" + item+".jpg", "wb") as handler:
                handler.write(img_data)
                
       
            # ser all the urls found in a excel list
            for j in range(len(resultados["images_results"])) :
                item_urls.append(resultados["images_results"][j]["original"])
            urls_search.append(list(item_urls))
        except :
            errors.append(item)
        return True
    else:
        return False

#@count_elapsed_time
def read_excel(result) -> None :
    # Define variable to load the dataframe
    dataframe = openpyxl.load_workbook("Documents/Cotizaciones 2025 Provicional/Catalogo 2025/Registros Ingram/item_sin_liga.xlsx")

    # Define variable to read sheet
    dataframe1 = dataframe.active

    # Iterate the loop to read the cell values
    index = 0
    for row in range(1, dataframe1.max_row):
        for col in dataframe1.iter_cols(1, dataframe1.max_column):
            result.append(str(col[row].value))
        index += 1
    print("Archivo Excel leido")
    return

@count_elapsed_time
def descargar_imgenes_lista(result, errors, urls_search, init) -> None :
    API_KEY = os.getenv("SERPAPI_API_KEY")
    if not API_KEY:
        raise RuntimeError("SERPAPI_API_KEY not set in environment")

    for i in range(len(result)) :
        descargar_primera_imagen(result[i], urls_search, errors, i, API_KEY) 
        #    errors.append(item)




    print("Imagenes descargadas")
    print(len(errors), "items no encontrados")
    datos = pd.DataFrame(urls_search)
    excel_writer = pd.ExcelWriter("Documents/Cotizaciones 2025 Provicional/Catalogo 2025/api_urls_excel/"+init+".xlsx")
    datos.to_excel(excel_writer, sheet_name=init)
    excel_writer._save()


@count_elapsed_time
def print_errors(errors, init)-> None :
    datos = pd.DataFrame(errors)
    excel_writer = pd.ExcelWriter("errores_excel/errores_api_"+init+".xlsx")
    datos.to_excel(excel_writer, sheet_name=init)
    excel_writer._save()
    print("Reporte de errores generado")

now = datetime.now()
print("prueba", now)
init = str(now.strftime('day_%d_%m_%Y_time_%H_%M'))
result = []
errors = []
urls_search = []
read_excel(result)
print(result)

descargar_imgenes_lista(result, errors, urls_search, init)
if len(errors) > 0 :
    print_errors(errors, init)