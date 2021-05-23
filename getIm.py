from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse

def get_soup(url,header):
    return BeautifulSoup(urllib.request.urlopen(
        urllib.request.Request(url,headers=header)),
        'html.parser')

def bing_image_search(query):
    query= query.split()
    query='+'.join(query)
    url="http://www.bing.com/images/search?q=" + query + "&FORM=HDRSC2"

    header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    soup = get_soup(url,header)
    image_result_raw = soup.find_all("a",{"class":"iusc"})
    image_list = []

    for image_data in image_result_raw:
      img_link = image_data.get('m').replace('"', "").split(",")
      image_list.append(img_link[2][5:])
    
    return image_list