import sys
import importlib.util
from pathlib import Path
import openpyxl
import pandas as pd
from urllib import error

def load_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "programs" / "url_pics.py"
    spec = importlib.util.spec_from_file_location("url_pics", str(module_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules["url_pics"] = module
    spec.loader.exec_module(module)
    return module

def make_workbook(path, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    wb.save(path)

def test_read_excel_success(tmp_path):
    excel_path = Path("programs/static/files_to_read/ligas_foto.xlsx")
    rows = [
        ["H1","H2","H3","H4","H5","H6","H7","H8","H9","H10","H11","H12","H13"],
        ["a0","b0","ref0","y","ITEM1","","","","","","","","https://images.icecat.biz/img/gallery/79522815_3254890999.jpg"],
        ["a1","b1","ref1","x","ITEM2","","","","","","","","http://img/2.jpg"],
    ]
    make_workbook(excel_path, rows)

    url_pics = load_module()
    result = []
    errors = []
    
    print(f"Before: result={result}, errors={errors}")
    url_pics.read_excel(result, errors)
    print(f"After: result={result}, errors={errors}")
    print(f"result length: {len(result)}")
    if result:
        print(f"result[0]: {result[0]}")
        print(f"result[0][5]: {result[0][5]}")

    assert len(result) == 2
    assert errors == []
    assert result[0][5] == "ITEM1"
    assert result[1][5] == "ITEM2"

def test_read_excel_missing_file(tmp_path):
    excel_path = Path("programs/static/files_to_read/ligas_foto.xlsx")
    if excel_path.exists():
        excel_path.unlink()

    url_pics = load_module()
    result = []
    errors = []
    url_pics.read_excel(result, errors)

    assert result == []
    assert len(errors) == 1
    assert "not found" in (errors[0][3].lower() or "")

def test_import_picts_success(monkeypatch):
    url_pics = load_module()
    item = "ITEMX"
    url = "http://example/test.jpg"
    rec = [0, None, "refX", None, None, item] + [None] * 7 + [url]
    result = [rec]
    errors = []

    class DummyResp:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
        def read(self): return b"IMAGEBYTES"

    def fake_urlopen(remote_url, context=None, timeout=None):
        assert remote_url == url
        return DummyResp()

    monkeypatch.setattr(url_pics.request, "urlopen", fake_urlopen)

    url_pics.import_picts(result, errors)

    out_file = Path("programs/static/url_images") / f"{item}.jpg"
    assert out_file.exists()
    assert out_file.read_bytes() == b"IMAGEBYTES"
    assert errors == []

def test_import_picts_http_error(monkeypatch):
    url_pics = load_module()
    item = "ITEM_ERR"
    url = "http://bad/url.jpg"
    rec = [0, None, "refErr", None, None, item] + [None] * 7 + [url]
    result = [rec]
    errors = []

    def raise_http(remote_url, context=None, timeout=None):
        raise error.HTTPError(url, 404, "Not Found", hdrs=None, fp=None)

    monkeypatch.setattr(url_pics.request, "urlopen", raise_http)

    url_pics.import_picts(result, errors)

    assert len(errors) == 1
    assert "download failed" in errors[0][3].lower()

def test_print_errors_creates_excel():
    url_pics = load_module()
    init = "testinit"
    errors = [
        [1, "ITEM1", "http://x", "download failed"],
        [2, "ITEM2", "http://y", "row too short"],
    ]

    url_pics.print_errors(init, errors)

    out_dir = Path("programs/static/errores_excel")
    files = list(out_dir.glob("errores_testinit.xlsx"))
    assert files, "excel error file not created"
    df = pd.read_excel(files[0])
    assert len(df) ==  2