from stravalib.client import Client
import time
import os
import json
from stravalib import unithelper
import configparser


config = configparser.ConfigParser()
config.read('config.cfg')

tokens = {}
strava_client = Client()
authorize_url = strava_client.authorization_url(
    client_id=config['USER']['ClientID'], redirect_uri='http://localhost:8282/authorized')


if not os.path.isfile('tokens.json'):
    token_response = strava_client.exchange_code_for_token(
        client_id=config['USER']['ClientID'], client_secret=config['USER']['ClientSecret'], code=config['USER']['ClientCode'])
    tokens['access_token']=token_response['access_token']
    tokens['refresh_token']=token_response['refresh_token']
    tokens['expires_at']=token_response['expires_at']
    with open('tokens.json', 'w') as outfile:
        json.dump(tokens, outfile)
else: 
    with open('tokens.json', 'r') as json_file:
        tokens = json.load(json_file)

# Now store that short-lived access token somewhere (a database?)
strava_client.access_token = tokens['access_token']
strava_client.refresh_token = tokens['refresh_token']

# An access_token is only valid for 6 hours, store expires_at somewhere and
# check it before making an API call.
strava_client.token_expires_at = tokens['expires_at']

athlete = strava_client.get_athlete()
print("For {id}, I now have an access token {token}".format(
    id=athlete.id, token=tokens['access_token']))

if time.time() > strava_client.token_expires_at:
    refresh_response = strava_client.refresh_access_token(client_id=config['USER']['ClientID'], client_secret=config['USER']['ClientSecret'],
                                                   refresh_token=strava_client.refresh_token)
    tokens['access_token'] = refresh_response['access_token']
    tokens['refresh_token'] = refresh_response['refresh_token']
    tokens['expires_at'] = refresh_response['expires_at']
    with open('tokens.json', 'w') as outfile:
        json.dump(tokens, outfile)

curr_athlete = strava_client.get_athlete_stats()
print("All Runs in KM: {}".format(unithelper.kilometer(curr_athlete.all_run_totals.distance)))
print("All Rides in KM: {}".format(unithelper.kilometer(curr_athlete.all_ride_totals.distance)))
