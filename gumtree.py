import requests
from bs4 import BeautifulSoup as soup 

import pandas as pd         # for creating data frame
import numpy as np          # used to support large, multi-dimensional arrays
from datetime import date   # for todays date
from datetime import datetime # for runtime of program
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.linear_model import LinearRegression

def convert_list_to_string(org_list, seperator=' '):
    # """ Convert list to string, by joining all item in list with given separator.
    #     Returns the concatenated string """
    return seperator.join(org_list)


startTime = datetime.now()

gumString = 'https://www.gumtree.com.au'
search_url = 'https://www.gumtree.com.au/s-tvs/c21115' # gumtree page sorting by most recent

# opening up connection, grabbing the page
curr_page = requests.get(search_url)
search_html = curr_page.content
curr_page.close()

search_soup = soup(search_html, "html.parser")

data = []
used_urls = []

# opens up dataframe to date
df = pd.read_csv('completeTV.csv')

# for cycling through pages
page_num = 1
print("Selecting page_panel... ")
page_panel = search_soup.select("#react-root > div > div.page > div > div.search-results-page__content > main > div.panel.search-results-page__paginator > div > div.page-number-navigation")
print("Done!")

for page_num in range(2, 50): # there are 50 pages
    # grabs each product
    print("Finding Products... ")
    products = search_soup.findAll("a", {"class":"user-ad-row-new-design"})
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
        for url in df['Url']: # was in used_urls:
            if url == product_url:
                indata = 1
                
        if indata == 1:
            # url has already been checked
            # dont open site
            print("FOUND A DUPLICATE")
        else:
            # url has not been checked (should put all this into a function)
            used_urls.append(product_url) # add url to array
            
            # adds the urls data
            curr_prod = requests.get(product_url)
            prod_html = curr_prod.content
            curr_prod.close()

            prod_soup = soup(prod_html, "html.parser")
            
            product_rep['Url'] = product_url
            price = prod_soup.select("#react-root > div > div.page > div > div.view-item-page__page-content > div.view-item-page__item-and-related > div.panel.vip-ad > div > div.vip-ad__container > div.vip-ad__row > div > div.user-ad-price.user-ad-price--vip.vip-ad-title__price > span.user-ad-price__price")
            bad_chars = [',', '$']
            if price:
                price = price[0].contents[0]
                for i in bad_chars : 
                    price = price.replace(i, '') 
                product_rep['Price'] = int(float(price))

            # location = prod_soup.select("#react-root > div > div.page > div > div.view-item-page__page-content > div.view-item-page__item-and-related > div.panel.vip-ad > div > div.vip-ad__container > div.vip-ad__row > div > div.vip-ad-title__location > button > span.vip-ad-title__location-address")
            # if location:
            #     location = location[0].contents[0]
            #     # location = [x.strip() for x in location.split(',')] # splits into city and state
            #     product_rep['Location'] = location
            
            suburb = prod_soup.select(".breadcrumbs__desktop > span:nth-child(3) > a:nth-child(1)")
            if suburb:
                suburb = suburb[0].contents[0]
                product_rep['Suburb'] = suburb

            # looks in title to find exact screen size

            # Looks in description to find exact screen size

            # if double digits in title - its probably the size

            cont_screen_size = prod_soup.select(".vip-ad-title__header")
            # if there is a header
            if cont_screen_size:
                cont_screen_size = cont_screen_size[0].renderContents()
                cont_screen_size = str(cont_screen_size).lower() # changes all to lower case
                print(cont_screen_size)

                # converting utf-8 for " and ' back to ASCII


                index_inch = cont_screen_size.find('"', 3, -3) # skips opening quotations
                if index_inch == -1:
                    index_inch = cont_screen_size.find(r"\xe2\x80\x9d") # unicode for "
                if index_inch == -1:
                    index_inch = cont_screen_size.find(r"\xe2\x80\x99") # unicode for "
                index_inch_word = cont_screen_size.find('inch')
                index_cm = cont_screen_size.find('cm')

                if index_inch != -1:
                    # Find the number associated with " in title
                    index = index_inch - 1

                    if cont_screen_size[index].isnumeric() == False: # space or - immediately before it - remove it
                        index = index - 1
                        index_inch = index_inch - 1

                    while (cont_screen_size[index].isnumeric()) | (cont_screen_size[index] == '.'): # cop out way to do this. need a better alternative than > 
                        index = index - 1
                    if index + 1 != index_inch:
                        product_rep['size_inch'] = int(float(cont_screen_size[index + 1:index_inch]))
                        print(cont_screen_size[index + 1:index_inch])
                elif index_inch_word != -1:
                    # Find the number associated with inch in description
                    index = index_inch_word - 1
                    if cont_screen_size[index] == ' ': # space immediately before it - remove it
                        index = index - 1
                        index_inch_word = index_inch_word - 1

                    while (cont_screen_size[index].isnumeric()) | (cont_screen_size[index] == '.'):
                        index = index - 1
                    
                    if index + 1 != index_inch_word:
                        product_rep['size_inch'] = int(float(cont_screen_size[index + 1:index_inch_word]))
                        print(cont_screen_size[index + 1:index_inch_word])
                elif index_cm != -1:
                    # Find the number associated with cm in description
                    index = index_cm - 1

                    if cont_screen_size[index] == ' ': # space immediately before it - remove it
                        index = index - 1
                        index_cm = index_cm - 1

                    while (cont_screen_size[index].isnumeric()) | (cont_screen_size[index] == '.'):
                        index = index - 1
                    if index + 1 != index_cm:
                        product_rep['size_inch'] = int(float(cont_screen_size[index + 1:index_cm])/2.54)
                        print(float(cont_screen_size[index + 1:index_cm])/2.54)

            
            # loops through all elements of a tv and dynamically adds them to the dictionary
             # if brand is not in box, check desription against a bank of brand's
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

    print(f"FINISHED PAGE {page_num}")

    # opening new page
    curr_page = requests.get(next_page)
    search_html = curr_page.content
    curr_page.close()

    search_soup = soup(search_html, "html.parser")

print("There were " + str(len(used_urls)) + " products scraped")



##### MERGING #####

(pd.DataFrame(data)
    .to_csv('/home/charlie/Documents/myProjects/Gumtree-bargains/newGumtreeTV.csv', header=True, index = False))

# reads the file just created
new = pd.read_csv('newGumtreeTV.csv')

print("Read both files! :)")
# Need to make another column indicating wether a tv from the complete database is no longer in new list -> then it is sold

# adds url's to the complete list and updates any ones already in the list
merged = df.append(new)
merged.drop_duplicates(subset = "Url", keep = "last", inplace = True)

print("Merged both files! :)")

# write finished file
merged.to_csv('/home/charlie/Documents/myProjects/Gumtree-bargains/completeTV.csv', header=True, index = False)




#### REGRESSION ####

predictors = list(merged)[1:len(merged)]
predictors.remove('Price')
predictors.remove('Suburb')
predictors.remove('Date Listed')
predictors.remove('Last Edited')
predictors.remove('size_inch')
predictors.remove('yhat') # this column will already exist if this script has been run before

merged_dummies = pd.get_dummies(merged, dummy_na = True, drop_first = True, columns=predictors)

x = merged_dummies.drop(columns=['Url', 'Price', 'Suburb', 'Date Listed', 'Last Edited', 'yhat']) # skips url column
merged_dummies.to_csv('/home/charlie/Documents/myProjects/Gumtree-bargains/dummies.csv', header=True, index = False)
x['size_inch'] = merged['size_inch']
x['size_na'] = np.isnan(x['size_inch']) # this currently doesnt work
x['size_inch'] = np.nan_to_num(x['size_inch'])
# do a tv age * brand here

y = merged['Price']
y = np.nan_to_num(y)
print(y)


# check this link for multiple linear regression -
# https://realpython.com/linear-regression-in-python/
# https://towardsdatascience.com/a-beginners-guide-to-linear-regression-in-python-with-scikit-learn-83a8f7ae2b4f



model = LinearRegression().fit(x, y)

r_sq = model.score(x, y)
print('coefficient of determination:', r_sq)
# print('intercept:', model.intercept_)
# print('slope:', model.coef_)

merged['yhat'] = model.predict(x)


# write finished file
merged.to_csv('/home/charlie/Documents/myProjects/Gumtree-bargains/completeTV.csv', header=True, index = False)

print("\nTime taken to execute: ")
print(datetime.now() - startTime)


# things to add - 
# check for key words in description e.g.
# brand names against a txt file
# "damaged"