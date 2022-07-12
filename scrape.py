import requests
from bs4 import BeautifulSoup
from decimal import Decimal
import json

def scrape(id, link):

    allPropertiesLinks = []
    allDescription = []
    allPrice = []
    title = ""

    index = 0
        
    for pages in range(41):

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
        }

        if index == 0:
            rightmove = link

        elif index != 0:
           rightmove = link + f"&index={str(index + 24)}"

        res = requests.get(rightmove, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # This gets the list of apartments
        apartments = soup.find_all("div", class_="l-searchResult is-list")

        # This gets the number of listings
        numListings = soup.find(
            "span", {"class": "searchHeader-resultCount"}
        )
        numListings = numListings.get_text()
        numListings = int(numListings.replace(",", ""))
        
        findTitle = soup.find(
            "div", {"class" : "searchTitle"} 
        )
        title = {
            findTitle.find("h1", class_="searchTitle-heading")
            .get_text()
            .strip()
        }
        for i in title:
            title = i

        for i in range(len(apartments)):

            # Tracks which apartment we are on in the page
            firstVar = apartments[i]

            # Append link
            propertyInfo = firstVar.find("a", class_="propertyCard-link")
            propertyLink = "https://www.rightmove.co.uk" + propertyInfo.attrs["href"]
            allPropertiesLinks.append(propertyLink)

            # Append description
            description = (
                propertyInfo.find("h2", class_="propertyCard-title")
                .get_text()
                .strip()
            )
            allDescription.append(description)

            # Append price
            price = (
                firstVar.find("div", class_="propertyCard-priceValue")
                .get_text()
                .strip()
            )
            allPrice.append(price)

        index = index + 24

        if index >= numListings:
            break

    allNumPrice = []
    unknownPrice = 0
    
    for price in allPrice:
        num = "".join([i for i in price if i not in ["£",","]])
        if num != "POA":
            allNumPrice.append(int(num))
        else:
            unknownPrice += 1
            
    average = sum(allNumPrice) / (len(allNumPrice)-unknownPrice)
    
    overview = {
        "length": len(allPropertiesLinks),
        "average": '£{:,.0f}'.format(average),
    }
    
    title = title.split("Properties For Sale in ")[1] 
    title = title.split(",")[0]
        
    data = {
        "data": {
            "Links": allPropertiesLinks,
            "Description": allDescription,
            "Price": allPrice,
        },
        "overview": overview,
        "title": title
    }
    
    with open(f"{id}.json", "w") as file:
        json.dump(data, file)
