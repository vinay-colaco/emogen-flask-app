import json

with open("./credentials.json", "rb") as file:
    credentials = json.load(file)

server_email = credentials['server']['email']
server_pass = credentials['server']['password']
admin_email = credentials['admin']['email']
admin_pass = credentials['admin']['password']
