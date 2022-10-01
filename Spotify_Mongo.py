# -*- coding: utf-8 -*-
"""
@author: jcuesta
"""

import requests
from urllib.parse import urlencode
import base64
import pymongo
import time

"""
##############################    LIBRERIA DE CLASES

"""

class SpotifyAPI(object):
    
    token = None
    client_id = None
    client_secret = None
    
    def __init__(self,client_id,client_secret):
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.getToken()
        
    def getToken(self):
        
        endpoint = "https://accounts.spotify.com/api/token"
        credentials = f"{client_id}:{client_secret}"
        credentials = base64.b64encode(credentials.encode())
        token_data = {
                
                      "grant_type" : "client_credentials"
            
                     }
        header = {
                    'Authorization':f'Basic {credentials.decode()}'
            
                  }
        
        req = requests.post(endpoint,data=token_data,headers = header)
        if req.status_code in range(200,299):
            return req.json()['access_token']
        else:
            raise Exception("No se pudo procesar la conexion correctamente")
        
       
class Request():
        
   url = None
   endpoint = None
   header = None
   
   def __init__(self,token):
        
        self.url = "https://api.spotify.com"
        self.header = {
                      'Authorization' : f'Bearer  {token}'           
                      }
       
   
   def Search(self,name_song):
       
       endpoint = "/v1/search"
       url_search = self.url + endpoint   
       data = urlencode({
              "q": f'{name_song}',
              "type":"track"
              })
       
       req_url = f"{url_search}?{data}"
       r = requests.get(req_url, headers= self.header,verify=False)
       if r.status_code in range(200,299):
           return r.json()
       
       else:
           Exception("No se ha conseguido realizar la busqueda correctamente en la API")
           
   def getLists(self,account):
        
       endpoint = "/v1/users/{}/playlists".format(account)
       url_search = self.url + endpoint
       r = requests.get(url_search, headers= self.header)
       
       if r.status_code in range(200,299):
           return r.json()
       else:
           Exception("No se ha podido obtener la lista del usuario")
       
      
   def getTracks(self,playlist_id):
       
       endpoint= "/v1/playlists/{}/tracks".format(playlist_id)
       url_search = self.url + endpoint
       r = requests.get(url_search, headers= self.header)
       return r.json()
       
     
   def analyzeSong(self,id_song):
       
       #id_song = "id_test"
       endpoint = "/v1/audio-features/{}".format(id_song)
       url_search = self.url + endpoint
       r = requests.get(url_search, headers= self.header)
       return r.json()
   
    
   def audioanalysis(self,id_song):
   
       endpoint = "/v1/audio-analysis/{}".format(id_song)
       url_search = self.url + endpoint
       r = requests.get(url_search,headers = self.header)
       return r.json()
   
class bbdd:
    
    dbStringConnection = "mongodb+srv://string"
    dbName = None
    dbCollectionSP = 'Songs_Spotify'
    songs = None
    
    def __init__(self,dbName):
        
        client = pymongo.MongoClient(self.dbStringConnection)
        db = client[dbName]
        self.songs = db[self.dbCollectionSP]
        #db[self.dbCollectionSP].create_index([('Spotify_handle', pymongo.ASCENDING)], unique=True)
        
    def insertSongs(self,dict_song):
        
        self.songs.insert_one(dict_song)
  
"""

################ LIBRERIA DE FUNCIONES

"""

def createDictSong(pl,dateAt,pop,ns,info):
    
    entry = {}
    entry['playlist'] = pl
    entry['added_at'] = dateAt
    entry['popularity'] = popularity
    entry['name_song'] = ns
    entry['features'] = info
    
    return entry



"""

###############  WORKFLOW
        
"""
    

if __name__ == "__main__":
    
    ## VARIABLES
	
    client_id = "id_string"
    client_secret  = "id_string"
    account_id = "id_string"
    
    ### CONEXION CON API-USER Y CREACION DE BBDD MONGO
    api = SpotifyAPI(client_id, client_secret)
    req = Request(api.token)
    bd = bbdd('NombreBBDD_MONGO') #Creación bbdd en MongoDB
    
	### RECOGIDA DE INFORMACIÓN
    
    allPlaylists = req.getLists(account_id)['items']
    for playlist in allPlaylists: #Recorremos todas las playlist: En este ejemplo solo analizamos la playlist 'Proyecto'
        if playlist['name'] == 'Proyecto':
            nameplaylist = playlist['name']
            print("Analizando playlist - " + str(nameplaylist))
            id_playlist = playlist['id']
            songs = req.getTracks(id_playlist)
            songs = songs['items']
            for song in songs:
                track = song['track']
                id_song = track['id']
                try:
                    infosong = req.analyzeSong(id_song)
                    #entry_song = createDictSong(nameplaylist,added_at,popularity,name_song,infosong)
                    song['features'] = infosong
                    time.sleep(3)  
					
                    try:
                        bd.insertSongs(song) #Insertamos diccionario
						
                    except pymongo.errors.DuplicateKeyError as e:
					
                        print (e, '\n')
                
                except:
                
                    continue
