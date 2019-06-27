import requests 
from bs4 import BeautifulSoup 

global_dir = 'D:\\KGP\\'

def get_links(archive_url): 
      
    # create response object 
    r = requests.get(archive_url) 
      
    # create beautiful-soup object 
    soup = BeautifulSoup(r.content,'html5lib') 
      
    # find all links on web-page 
    links = soup.findAll('a') 
  
    # filter the link sending with .mp4 
    all_links = [archive_url + link['href'] for link in links if link['href'].endswith('html')] 
  
    return all_links 
  
  
def download_series(all_links, directory): 
    not_downloaded = []
    for link in all_links: 
  
        '''iterate through all links and download them one by one'''
          
        # obtain filename by splitting url and getting  
        # last string 
        file_name = link.split('/')[-1]  
        file_name = file_name.replace(':','_COLON_')
       
        try:
            print("Downloading file:%s"%file_name) 

            # create response object 
            r = requests.get(link, stream = True) 

            # download started 
            with open(directory + file_name, 'wb') as f: 
                f.write(r.content) 

            print("%s downloaded!\n"%file_name) 
        except:
            not_downloaded.append(link)

    print("All videos downloaded!")
    return not_downloaded
     
# Check the value of variable not_downloaded in the end to see which files were not downloaded

not_downloaded = []
for index in range(1, 10):
    archive_url = "https://manpages.ubuntu.com/manpages/bionic/en/man" + str(index) + "/"
    directory = global_dir + 'man' + str(index) + '\\'
    all_links = get_links(archive_url)
    not_downloaded += download_series(all_links, directory)
