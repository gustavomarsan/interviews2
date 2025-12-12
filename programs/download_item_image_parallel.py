from serpapi import GoogleSearch
import requests
from pathlib import Path
from multiprocessing import Pool, cpu_count
import pandas as pd
import os


def descargar_primera_imagen_parallel(item_api_data): 
    """This function runs in a separate worker, and acts as in original version of download, no changes needed.
       Each worker downloads ONE image, is called by run_parallel.
    """
    try:
        item, api_key = item_api_data

        params = {
            "q": item,
            "tbm": "isch",
            "api_key": api_key
        }

        resultados = GoogleSearch(params).get_dict()

        if "images_results" not in resultados:
            return (item, False, "No results")

        url_imagen = resultados["images_results"][0]["original"]

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url_imagen, headers=headers, timeout=10)

        if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
            image_path = Path("programs/static/photos_api") / f"{item}.jpg"
            with open(image_path, "wb") as f:
                f.write(response.content)

            return (item, True, "OK")

        else:
            return (item, False, "Invalid image type")

    except Exception as e:
        return (item, False, f"Error: {e}")


def run_parallel(items, api_key):       # This is the new function that runs the pool of workers 
    """High-level function to run pool of parallel workers.
       It prepares the work items and starts the workers.
       The multiprocessing Pool handles the parallelism and is done here.
    """
    
    # Prepare inputs for workers
    work_items = [(item, api_key) for item in items]

    # Create Pool
    workers = min(cpu_count(), 8)   # limit to 8
    print(f"Using {workers} parallel workers")

    with Pool(workers) as pool:
        results = pool.map(descargar_primera_imagen_parallel, work_items)

    return results


# Example usage:
if __name__ == "__main__":
    API_KEY = os.getenv("SERPAPI_API_KEY")

    # Example list (in your real code this comes from Excel)
    items = ["table", "mountain", "bridge", "bus"]

    results = run_parallel(items, API_KEY)

    print("\nFINAL RESULTS:")
    for item, ok, msg in results:
        print(f"{item:12}  => {ok}   ({msg})")
