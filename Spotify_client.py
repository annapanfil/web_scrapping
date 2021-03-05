#!/usr/bin/env python
# coding: utf-8

import requests
import base64
import datetime
from urllib.parse import urlencode

client_id = ""
client_secret = ""

class SpotifyAPI():
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None

    def __init__(self, client_id, client_secret, *args, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns base 64 encoded string
        """
        if self.client_id == None or self.client_secret == None:
            raise Exception("You have to set client_id and client_secret")

        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds = client_creds.encode() # it's in bytes
        client_creds_b64 = base64.b64encode(client_creds) # base64 encrypted
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self):
        return {"grant_type": "client_credentials"}

    def get_resource_headers(self):
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    def perform_auth(self):
        # look up for a token for future requests (log in)
        # https://developer.spotify.com/documentation/general/guides/authorization-guide/#client-credentials-flow

        token_url = "https://accounts.spotify.com/api/token"
        method = "POST"
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()

        r = requests.post(token_url, data=token_data, headers=token_headers)

        if r.status_code not in range(200, 299):
            raise Exception("Authentication failed")
        else:
            data = r.json()
            now = datetime.datetime.now()
            self.access_token = data["access_token"]
            expires_in = data["expires_in"]
            self.access_token_expires = now + datetime.timedelta(seconds=expires_in)
            self.access_token_did_expire = self.access_token_expires < now
            return True

    def get_access_token(self):
        # get a new token if the old one has expired
        now = datetime.datetime.now()
        if self.access_token_expires < now or self.access_token == None:
            self.perform_auth()
            return self.get_access_token()
        return self.access_token

    def get_resource(self, _id, resource_type="artists", version="v1"):
        # search for artist, album, etc.
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{_id}"
        headers = self.get_resource_headers()

        r = requests.get(endpoint, headers=headers)

        if r.status_code not in range(200, 299):
            return {}

        return r.json()

    def get_album(self, _id):
        # https://developer.spotify.com/documentation/web-api/reference/#category-albums
        return self.get_resource(_id, "albums")

    def get_artist(self, _id):
        return self.get_resource(_id, "artists")

    def base_search(self, query):
        # search for a well-prepaired query
        endpoint = "https://api.spotify.com/v1/search"
        headers = self.get_resource_headers()
        lookup_url = f"{endpoint}?{query}"

        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def search(self, query=None, operator=None, operator_query=None, search_type="track"):
        # prepair a query from a dictionary (and operator with string)
        # https://developer.spotify.com/documentation/web-api/reference/#endpoint-search
        if query == None:
            raise Exception("Query is required")
        elif isinstance(query,dict):
            query = "%20".join([f"{k}:{v}" for k,v in query.items()]) #%20 is a space
            print('q =', query)

        if operator and operator_query:
            operator = operator.upper()
            if operator == "OR" or operator == "NOT":
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"

        query_params = urlencode({"q": query, "type": search_type.lower()})

        return self.base_search(query_params)

spotify = SpotifyAPI(client_id, client_secret)
