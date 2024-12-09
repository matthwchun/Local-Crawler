# IMPORTS
import re
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from urllib.parse import urlparse

# VARIABLES
visited = set() # every visited url
subdomains = dict() #subdomain: # of unique domains found
word_number = dict() #word: # of times appeared
blacklist = set() # hard coding bad sites, typically last resort
long = ["", -1] #url, number of words
backupcycle = 0 #NEW


uci_domains = [".ics.uci.edu/", ".cs.uci.edu/",".informatics.uci.edu/", ".stat.uci.edu/", "today.uci.edu/department/information_computer_sciences/"]

stop_words = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren", "t", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "not", "cannot", "could",
    "couldn", "did", "didn", "do", "does", "doesn", "doing", "don", "down", "during", "each", "few", "for", "from",
    "further", "had", "hadn", "has", "hasn", "have", "haven", "having", "he", "d", "ll", "s", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn", "it", "its", "itself", "let", "me",
    "more", "most", "mustn", "my", "myself", "no", "nor", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan", "she", "should", "shouldn", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn", "we", "what", "when", "where", "which",
    "while", "who", "whom", "why", "with", "won", "would", "wouldn", "you", "your", "yours", "yourself", "yourselves"
]

# HELPER FUNCTIONS
def normalize_url(url):
    parsed_url = urlparse(url)
    query_params = sorted(parse_qsl(parsed_url.query))
    normalized_query = urlencode(query_params, doseq=True)
    normalized_url = urlunparse(parsed_url._replace(query=normalized_query, fragment="")) 
    return normalized_url

def extract_text(resp): #returns string
    html = bs(str(resp.raw_response.content), "html.parser")
    text = (html.get_text()).replace("\\t"," ").replace("\\n"," ").replace("\\x"," ").replace("\\d"," ").replace("\\r"," ")
    return text

def extract_subdomain_and_update(url): #NEW2
    parsed_url = urlparse(url)
    '''
    subdomain_parts = parsed_url.hostname.split('.')
    if len(subdomain_parts) > 2:
        sub_domain = subdomain_parts[-3]
    if sub_domain not in subdomains:
        subdomains[sub_domain] = 0
    else:
        subdomains[sub_domain] += 1
    '''

    hostname = parsed_url.hostname

    if hostname not in subdomains:
        subdomains[hostname] = 0
    else:
        subdomains[hostname] += 1


def check_uci_in_domain(url):
    domain = urlparse(url).netloc
    return "uci.edu" in domain

def alphanumeric_check(char: str) -> bool:
    an = "abcdefghijklmnopqrstuvwxyz1234567890"
    if char.lower() not in an:
        return False
    return True

def tokenize_and_update(text: str) -> None:
    global num_tokens
    num_tokens = 0
    token_string = ""
    prev_char = ""
    for char in text:
        if alphanumeric_check(char):
            token_string += char
        elif alphanumeric_check(prev_char) == False and alphanumeric_check(char) == False:
            continue
        else:
            token_string = token_string.lower()
            if (token_string in stop_words) or (len(token_string) < 3): #NEW 2
                token_string = ""
                prev_char = char
                continue
            elif token_string in word_number:
                word_number[token_string] += 1
                num_tokens += 1 
            else:
                word_number[token_string] = 1
                num_tokens += 1 
            token_string = ""
        prev_char = char

def update_longest(url):
    if num_tokens > long[1]:
        long[0] = url
        long[1] = num_tokens


def is_new_url(url):
    """
    Checks if a URL follows the general pattern expected for events on either 'cecs.uci.edu' or 'wics.ics.uci.edu'.
    If it has been visited before based on the base structure, return False; if it is new, add it to the visited patterns and return True.
    """
    # Regular expression for the base URL patterns we want to track, regardless of specific date or parameters
    base_pattern_regex = (
        r"(https:\/\/(?:www\.cecs\.uci\.edu|wics\.ics\.uci\.edu)\/events\/category\/"
        r"(other-events|wics-meeting-dbh-5011|)\/"
        r"(day\/\d{4}-\d{2}-\d{2}|month|list)\/?)"
    )
    
    # Remove query parameters (anything after '?')
    normalized_url = re.sub(r"\?.*$", "", url)
    
    # Check if the URL matches one of the expected patterns
    match = re.match(base_pattern_regex, normalized_url)


    date_pattern_A = r'\d{4}-\d{2}-\d{2}'
    date_pattern_B = r'\d{4}-\d{2}'
    if("uci.edu/events" in url):
        standardnizedURL_A = re.sub(date_pattern_A, 'XXXX-XX-XX', url)
        standardnizedURL_B = re.sub(date_pattern_B, 'XXXX-XX', url)

        if(standardnizedURL_A in visited):
            return False
        elif(standardnizedURL_B in visited):
            return False
        else:
            visited.add(standardnizedURL_A)
            visited.add(standardnizedURL_B)
            return True

        


    if not match:
        return True  # URL does not match the expected patterns, treat as new
    
    # Extract the base pattern
    base_pattern = match.group(1)
    
    # Check if the normalized base pattern has been visited
    if base_pattern in visited_patterns:
        return False  # Pattern already visited
    else:
        visited_patterns.add(base_pattern)  # Mark this pattern as visited
        return True


def numFilters(Found_url):

    parts = Found_url.split('?')

    if len(parts) == 1:
        return True
    
    query_string = parts[1]
    num_filters = (query_string.lower()).count("filter") 

    #print(num_filters)
    return (num_filters <= 2)

def determine_quality():
    if num_tokens < 100:
        return False
    return True

def check_back_up():
    try:
        if(len(long)==0): #NEW
            with open("Z-long", "r") as file:
                first_char = file.read(1)
                if not first_char:
                    print("Z-long is empty.")
                else:
                    file.seek(0)
                    for line in file:
                        data = line.rstrip().split(",")
                        long[0] = data[0]
                        long[1] = int(data[1])
        if(len(subdomains)==0):  #NEW
            with open("Z-subdomains", "r") as file:
                first_char = file.read(1)
                if not first_char:
                    print("Z-subdomains is empty.")
                else:
                    file.seek(0)
                    for line in file:
                        data = line.rstrip().split(",")
                        subdomains[data[0]] = int(data[1])
        if(len(visited)==0):#NEW
            with open("Z-visited", "r") as file:
                first_char = file.read(1)
                if not first_char:
                    print("Z-visited is empty.")
                else:
                    file.seek(0)
                    for line in file:
                        data = line.rstrip()
                        visited.add(data)
        if(len(word_number)==0):#NEW
            with open("Z-word_number", "r") as file:
                first_char = file.read(1)
                if not first_char:
                    print("Z-word_number is empty.")
                else:
                    file.seek(0)
                    for line in file:
                        data = line.rstrip().split(",")
                        word_number[data[0]] = int(data[1])
    except FileNotFoundError:
        print("FileNotFoundError!")

def create_back_up():
    with open("Z-long", "w") as file:
        file.write(f"{long[0]},{str(long[1])}")
    with open("Z-subdomains", "w") as file:
        for k,v in subdomains.items():
            file.write(f"{k},{str(v)}\n")
    with open("Z-visited", "w") as file:
        for url in visited:
            file.write(f"{url}\n")
    with open("Z-word_number", "w") as file:
        for k,v in word_number.items():
            file.write(f"{k},{str(v)}\n")

# MAIN FUNCTIONS

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def ImportBlackList():
    with open("BLACKLIST.txt", "r") as file:
        first_char = file.read(1)
        if not first_char:
            print("BLACKLIST.txt is empty.")
        else:
            file.seek(0)
            for line in file:
                blacklist.add(line.strip())

def extract_next_links(url, resp):
    
    if(len(blacklist) < 1):
        print("IMPORTING BLACKLIST")
        ImportBlackList()
    


    global backupcycle
    check_back_up() #NEW
    found_urls = set()
    repeatCycle = 0
    links = list()
    
    if((url in visited) or ("uci.edu" not in url)):
        return links

    try:
        # CHECK for STATUS
        
        if resp.status == 204:
            (f"Webpage status returned <{resp.error}>. No Content")
            return links
        if resp.status != 200:
            print(f"Webpage: <" + str(url) + f"> status returned <{resp.error}>. Expected <200>. Reason: <{resp.raw_response}>")
            with open("ERRORCODES.txt", "a") as file:
                file.write("Webpage: <" + str(url) + "> status returned <"+ str(resp.error) + ">. Expected <200>. Reason: <" + str(resp.raw_response) + ">\n")
            return links


        # ACCEPTED, LOG
        with open("TheTraversed.txt", "a") as f:
            f.write(f"status {resp.status} : {str(resp.raw_response.url)} \n")
        

        # PARSE CURRENT URL CONTENT AND UPDATE STATS ACCORDINGLY
        web_text = extract_text(resp) #gets web_text
        extract_subdomain_and_update(url) #updates subdomain dict 
        tokenize_and_update(web_text) #updates word_number dict
        if not determine_quality(): 
            return links 
        update_longest(url)
        writeNumOfUniquePages()
        writeLongestPage()
        write50CommonWords()
        writeAllSubDomains()
        backupcycle += 1 # NEW
        if backupcycle >= 50:
            create_back_up()
            backupcycle = 0
        # START PARSING FOR LINKS

        html = bs(resp.raw_response.content, "html.parser")

        for link in html.find_all('a'):
            if(repeatCycle >= 5):
                return links



            l = link.get('href')

            if(l is None):
                continue

            if("http" not in l):
                l = urljoin(url, l)

            if(l in found_urls):
                repeatCycle+=1
            l = normalize_url(l) 

            if ((is_valid(l)) and (l not in visited) and (check_uci_in_domain(l)) and (numFilters(l)) and (is_new_url(url)) and (l not in blacklist) and (((l[:-1]) not in blacklist) and ((l+"/") not in blacklist))) :
                #print("ACCEPTED URL:") 
                #print(l)
                visited.add(l)
                links.append(l)
                found_urls.add(l)
            else:
                #print("NOT ACCEPTED URL:<" + l)
                l = ""
                #print("REASON:")
                #print(is_valid(l))
                #print((l not in visited))
                #print((check_uci_in_domain(l)))
                #print(is_new_url(url))
                #print(l)
        return links
    except Exception as e:

        print(f"An error occurred: {e}")
        return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|htm"
            + r"|eventDate=\d{4}-\d{2}-\d{2}"
            + ")$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

# FUNCTIONS TO RUN STATISTICS

def writeNumOfUniquePages():
    with open("TheNumberOfUniquePages", "w") as file:
        file.write("Number of unique pages: " + str(len(visited)))
    
def writeLongestPage():
    with open("TheLongestPage", "w") as file:
        file.write("Webpage with the most number of words: " + str(long[0]) + " : " + str(long[1]))


def write50CommonWords(): #ordered by freq
    top_50_words = sorted(word_number.items(), key=lambda x: x[1], reverse=True)[:50]
    with open("TheTop50CommonWords.txt", "w") as file:
        for word, freq in top_50_words:
            file.write(f"{word}: {freq}\n")
    
def writeAllSubDomains(): #ordered alphabetically + # of unique pages detected in subdomain: sub, #
    sorted_subdomains = sorted(subdomains.items())
    with open("TheSubDomains.txt", "w") as file:
        for subdomain, count in sorted_subdomains:
            file.write(f"{subdomain}, {count}\n")

if __name__ == "__main__":
    test_url = "https://ics.uci.edu/happening/news/?filter%5Baffiliation_posts%5D%5B0%5D=1989&filter%5Baffiliation_posts%5D%5B1%5D=1990"
    test_url2 = "http://www.ics.uci.edu#aaa"
    print("Before: "+ test_url2)
    x = normalize_url(test_url2)
    print("After : "+ x)

# NOTES

# Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content


# THINGS 2 LOOK OUT FOR
#Visited dict/list, Regex, Sim hash (dup detection), site maps, monitor crawl speed
#dead URLs, calendar trap, time trap, 
#robots.txt  ==> /robots.txt
#quality, multithreaded, fast, polite, doesn't get trapped


