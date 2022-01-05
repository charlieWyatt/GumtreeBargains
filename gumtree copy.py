from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup 

import pandas as pd         # for creating data frame
import numpy as np          # used to support large, multi-dimensional arrays
from datetime import date   # for todays date


def grabUrl(Url):
    print("Opening product url... ")
    prodClient = uReq(Url)
    print("Done!")

    print("Reading Page... ")
    prod_html = prodClient.read()
    print("Done!")

    print("Closing product url... ")
    prodClient.close()
    print("Done!\n")

    return prod_html



gumString = 'https://www.gumtree.com.au'
search_url = 'https://www.gumtree.com.au/s-tvs/c21115' # gumtree page sorting by most recent

# opening up connection, grabbing the page
search_html = grabUrl(search_url)

search_soup = soup(search_html, "html.parser")

data = []
used_urls = []

# for cycling through pages
page_num = 1
print("Selecting page_panel... ")
page_panel = search_soup.select("#react-root > div > div.page > div > div.search-results-page__content > main > div.panel.search-results-page__paginator > div > div.page-number-navigation")
print("Done!")

for page_num in range(2, 50): # there are 50 pages
    # grabs each product
    print("Finding Products... ")
    products = search_soup.findAll("a", {"class":"user-ad-row"})
    print("Done!")
    for (idx, product) in enumerate(products):

        product_rep = {}

        container = product
        details = container.find("div", "user-ad-row__details") # where the products details are located
        # go to link
        product_url = gumString + str(container.get('href'))

        print(product_url)
        # cycles through used_urls to check if it is already in database
        indata = 0
        for url in used_urls:
            if url == product_url:
                indata = 1
                
        if indata == 1:
            # url has already been checked
            # dont open site
            print("FOUND A DUPLICATE\n")
        else:
            # url has not been checked (should put all this into a function)
            used_urls.append(product_url) # add url to array
            
            # adds the urls data
            prod_html = grabUrl(product_url)

            prod_soup = soup(prod_html, "html.parser")
            
            product_rep['Url'] = product_url
            price = prod_soup.select("#react-root > div > div.page > div > div.view-item-page__page-content > div.view-item-page__item-and-related > div.panel.vip-ad > div > div.vip-ad__container > div.vip-ad__row > div > div.user-ad-price.user-ad-price--vip.vip-ad-title__price > span.user-ad-price__price")
            if price:
                product_rep['Price'] = price[0].contents[0]

            location = prod_soup.select("#react-root > div > div.page > div > div.view-item-page__page-content > div.view-item-page__item-and-related > div.panel.vip-ad > div > div.vip-ad__container > div.vip-ad__row > div > div.vip-ad-title__location > button > span.vip-ad-title__location-address")
            if location:
                location = location[0].contents[0]
                # location = [x.strip() for x in location.split(',')] # splits into city and state
                product_rep['Location'] = location

            # loops through all elements of a tv and dynamically adds them to the dictionary
            el = prod_soup.select("li.vip-ad-attributes__item")
            # Get the suburb from the url!!! It always has the surburb without the state
            i = 0
            while i < len(el):

                if str(el[i].contents[0].contents[0]) == "Date Listed" or str(el[i].contents[0].contents[0]) == "Last Edited":
                    product_date = str(el[i].contents[1].contents[0])
                    if product_date[len(product_date) - 1] == 'o':                                # if date is in the form "x minutes/hours ago"
                        product_rep[el[i].contents[0].contents[0]] = date.today() # set date to today
                    else:
                        product_rep[el[i].contents[0].contents[0]] = el[i].contents[1].contents[0]
                else:
                    product_rep[el[i].contents[0].contents[0]] = el[i].contents[1].contents[0] # puts a categories value into its respective item

                i = i + 1
            
            data.append(product_rep)    # puts the product_rep into an array of products

    # cycling through pages
    next_page = gumString + "/s-tvs/page-" + str(page_num) + "/c21115"

    # opening new page
    uClient = uReq(search_url)
    search_html = uClient.read()
    uClient.close()
    # html parsing
    search_soup = soup(search_html, "html.parser")



(pd.DataFrame(data)
    .to_csv('/mnt/c/Users/Charlie/Documents/MyProjects/scrapping/newGumtreeTV.csv', header=True))

print("There were " + str(len(used_urls)) + " products scraped")


df = pd.read_csv('gum-data.csv')



# open the complete data list
#   if(fail_to_open) {
#       exit
#   }
#
# merge datasets
#
# do a linear regression and add expected price as a new column
#
# do a lower 95% CI interval column
# do an upper 95% CI interval column
# 
# Do a loop which outputs the links of those which are cheaper than average in white
# Do a loop which ouputs the links of those which are cheaper than lower interval in red

# This was used when data was also a dictionary
# (pd.DataFrame.from_dict(data=data, orient='index', columns = data.keys)
#    .to_csv('/mnt/c/Users/Charlie/Documents/MyProjects/scrapping/gumtreeTV.csv', header=False))


    