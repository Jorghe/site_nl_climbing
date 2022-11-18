from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from deta import Deta, Drive
import pandas
import numpy
import os, io
import json

from settings import Settings
"""
nl-climbing.deta.dev
Web function to provide info about routes and categorize by grade and by area
"""
grados = numpy.array(Settings.DEPORTIVA)

app = FastAPI()
root = os.path.dirname(os.path.abspath(__file__))
try:
  app.mount(
    "/static",
    StaticFiles(directory=root + "/static"),
    name = "static",
)
except :
  print("Exception type")

deta = Deta()
drive = deta.Drive("rutas")

templates = Jinja2Templates(directory="templates")
style = Jinja2Templates(directory="static")

structure : str = "Not implemented"

def load_json(file:str):
    # print(file, Settings.Zonas)
    if file in Settings.Zonas.all:
        stream = io.BytesIO(drive.get(f"{file}.json").read())
        json_file = json.loads(stream.getvalue().decode('utf-8'))
        print(json_file)
        return json_file
    else: return {}

@app.get("/style.css")
def style():
    """ with open(os.path.join(root, 'static/style.css')) as sty:
        print(len(sty.read())) """

    return style.TemplateResponse("style.css")

""" @app.get('/favicon.ico')
def fav():
    return style.TemplateResponse("favicon.ico") """

@app.get("/")# , response_class=HTMLResponse)
def render_home(request : Request ):
    """ index.html is rendered in root file """
    structure = "World Hello"
    with open(os.path.join(root, 'templates/index.html')) as fh:
        web_html = fh.read()
    print("Welcome to nl climbing")
    print(request.url)
    # print(request.body())
    # print(request.headers['content-type'])
    return templates.TemplateResponse("index.html", {"request": request.url, "grados": grados })
    # Response(content=web_html, media_type="text/html")
        

@app.get("/api/{zone}", response_class=JSONResponse)
def api_endpoint(zone:str, format:str="json"):
    
    """ Return a JSON response for a given zone """
    endpoint = "Not found"
    if zone in Settings.Zonas.all:
        # TODO: Use format
        #print(zone, format)
        # zona = pandas.read_json(load_json(zone))
        #print(zona.head())
        return drive.get(zone+".json").read()
    return endpoint

@app.get("/huaste/", response_class=HTMLResponse)
def render(rutas: str ="0", zonas:str = "0", sort :str = "0"):
    """ La Huasteca 
        Stream json file from deta.Drive and deploy it to html Response
    """
    print(f"Parametros: de rutas: {rutas}, zonas: {zonas}")
    stream = io.BytesIO(drive.get("huaste.json").read())
    cg= json.loads(stream.getvalue().decode('utf8'))
    crag = pandas.DataFrame(load_json('huaste'))
    print(f"File size is {crag.size}")
    if zonas == "0": 
        crag = crag.sort_values(by=["Area"])
    else:
        z = crag['Area'] == zonas
        crag = crag[z]

    if rutas == "0": return crag.to_html()
    q = crag["Grade"] == rutas

    return crag[q].to_html()

@app.get("/epc", response_class=HTMLResponse)
def epc():
    print("loading epc")
    crag = pandas.DataFrame(load_json('epc'))
    # crag = crag.sort_values(by=["Area"])
    return crag.to_html()

@app.get("/salto", response_class=HTMLResponse)
def render():
    crag = pandas.DataFrame(load_json('salto'))
    crag = crag.sort_values(by=["Area"])
    return crag.to_html()

""" def app(event):
    drive = Drive("rutas")
    crag = pandas.read_csv(drive.get("huaste_1.csv"))
    # nl_crag = nlCrag()
    # nl_crag.initialize()

    return crag.to_json()
 """
