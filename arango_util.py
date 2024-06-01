from bottle import request, response
from icecream import ic
import requests



##############################


def arango(query, type = "cursor"):
    try:
        url = f"http://arangodb:8529/_api/{type}"
        res = requests.post( url, json = query )
        ic(res)
        ic(res.text)
        return res.json()
    except Exception as ex:
        print("#"*50)
        print(ex)
    finally:
        pass