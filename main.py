import firebase_admin as fa
from firebase_admin import db
from scrape import scrape
import json

credObject = fa.credentials.Certificate("privateKey.json")
defaultApp = fa.initialize_app(
    credObject, {
        "databaseURL": "https://rightmove-property-scraper-default-rtdb.europe-west1.firebasedatabase.app",
	}
)

while True:
    ref = db.reference("/link")
    database = ref.get()
    
    notScraped = []
    
    for id in database:
        if database[id]["scraped"] == False:
            notScraped.append({"id": id, "URL": database[id]["URL"]})
    
    if len(notScraped) == 0:
        print("nothing to scrape")
        
    for d in notScraped:
        print(f"scraping... {d['id']}")
        scrape(d["id"], d["URL"])
        
        with open(f"{d['id']}.json", "r") as file:
            data = json.load(file)
            database[d["id"]]["data"] = data["data"]
            database[d["id"]]["overview"] = data["overview"]
            database[d["id"]]["scraped"] = True
            database[d["id"]]["title"] = data["title"]
        print(f"scraped {d['id']}")
        ref.update(database)