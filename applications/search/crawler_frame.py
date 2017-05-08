import logging
from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager, Link
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time
from collections import Counter
import string
import StringIO

try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs


logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
url_count = (set() 
    if not os.path.exists("successful_urls2.txt") else 
    set([line.strip() for line in open("successful_urls2.txt").readlines() if line.strip() != ""]))
MAX_LINKS_TO_DOWNLOAD = 3000

@Producer(ProducedLink, Link)
@GetterSetter(OneUnProcessedGroup)
class CrawlerFrame(IApplication):

    def __init__(self, frame):
        self.starttime = time()
        # Set app_id <student_id1>_<student_id2>...
        self.app_id = "84232577_21647556_17882060"
        # Set user agent string to IR W17 UnderGrad <student_id1>, <student_id2> ...
        # If Graduate studetn, change the UnderGrad part to Grad.
        self.UserAgentString = "IR S17 UnderGrad 84232577, 21647556, 17882060"
		
        self.frame = frame
        assert(self.UserAgentString != None)
        assert(self.app_id != "")
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def initialize(self):
        self.count = 0
        l = ProducedLink("http://www.ics.uci.edu", self.UserAgentString)
        print l.full_url
        self.frame.add(l)

    def update(self):
        for g in self.frame.get_new(OneUnProcessedGroup):
            print "Got a Group"
            outputLinks, urlResps = process_url_group(g, self.UserAgentString)
            for urlResp in urlResps:
                if urlResp.bad_url and self.UserAgentString not in set(urlResp.dataframe_obj.bad_url):
                    urlResp.dataframe_obj.bad_url += [self.UserAgentString]
            for l in outputLinks:
                if is_valid(l) and robot_manager.Allowed(l, self.UserAgentString):
                    lObj = ProducedLink(l, self.UserAgentString)
                    self.frame.add(lObj)
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def shutdown(self):
        print "downloaded ", len(url_count), " in ", time() - self.starttime, " seconds."
        pass

def save_count(urls):
    global url_count
    urls = set(urls).difference(url_count)
    url_count.update(urls)
    if len(urls):
        with open("successful_urls.txt", "a") as surls:
            surls.write(("\n".join(urls) + "\n").encode("utf-8"))

def process_url_group(group, useragentstr):
    rawDatas, successfull_urls = group.download(useragentstr, is_valid)
    save_count(successfull_urls)
    return extract_next_links(rawDatas), rawDatas
    
#######################################################################################
'''
STUB FUNCTIONS TO BE FILLED OUT BY THE STUDENT.

1. Keep track of all the subdomains that it visited, and count how many different URLs it has
processed from each of those subdomains
CHeck 2. Count how many invalid links it received from the frontier, if any
check 3. Find the page with the most out links (of all pages given to your crawler)
check 4. Any additional things you may find interesting to keep track

'''

links = list()
subdomains = Counter()
invalidLinkCount = 0
highestLinkCount = 0
highestLinkCountUrl = ""
linksMarkedBad = 0
filename = "CrawlerAnalytics.txt"
domain = ".ics.uci.edu"

def addSubdomain(dom, url):
    index = 0
    index = string.find(url, dom)
    subdomain = url[0:index+len(dom)]
    subdomains[subdomain] += 1

def extract_next_links(rawDatas):
    outputLinks = list()
    global links
    global subdomains
    global invalidLinkCount
    global highestLinkCount
    global highestLinkCountUrl
    global linksMarkedBad
    global filename
    global domain

    for link in rawDatas:
        '''
        rawDatas is a list of objs -> [raw_content_obj1, raw_content_obj2, ....]
        Each obj is of type UrlResponse  declared at L28-42 datamodel/search/datamodel.py
        the return of this function should be a list of urls in their absolute form
        Validation of link via is_valid function is done later (see line 42).
        It is not required to remove duplicates that have already been downloaded. 
        The frontier takes care of that.

        Suggested library: lxml

        rawDatas have url, content, error_message, http_code, is_redirected, final_url
        print ("error_message: ")
        print (link.error_message)
        print ("http_code: ")
        print (link.http_code)
        print ("is_redirected: ")
        print (link.is_redirected)
        print ("final_url: ")
        print (link.final_url)
        '''
        links.append(link.url)
        if (link.http_code == 200 or link.error_message == "") and link.content != "": # If everything is successful then HTTP code 200 or error_message ""
            url = ""
            if(link.is_redirected): #If link is redirected then absolutes use the final_url?
                url = link.final_url
            else:
                url = link.url
            addSubdomain(domain, url)
            tmpStr = html.make_links_absolute(link.content, url, False) # Makes all links absolute
            tree = etree.HTML(tmpStr) # Separates html into a tree based on tags
            for href in tree.xpath('//a/@href'): # takes out all the hrefs from the tree //xpath syntax
                if not href in links:
                    #outputLinks.append(href)
                    print(href)
            if len(outputLinks) > highestLinkCount:
                highestLinkCountUrl = url
                highestLinkCount = len(outputLinks)
        else:
            link.bad_url = True
            ++linksMarkedBad

        #Write to file here
        target = open(filename, 'w')
        target.truncate()
        target.write("Number of Invalid Links: " + str(invalidLinkCount))
        target.write("\n")
        target.write("Link with most links: " + highestLinkCountUrl + "at " + str(highestLinkCount) + " links.")
        target.write("\n")
        target.write("Number of Links Marked Bad: " + str(linksMarkedBad))
        target.write("\n")
        target.write("Subdomains visited (sorted by most common)")
        target.write("\n")
        for s, c in subdomains.most_common():
            target.write(s + " visited " + str(c) + " times.")
            target.write("\n")
        target.close()
        
    return outputLinks

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be downloaded or not.
    Robot rules and duplication rules are checked separately.

    This is a great place to filter out crawler traps.
    '''
    global invalidLinkCount
    global links
    print ("Checking url validity: " + url)
    
    print ("Checking if visited url before")
    if len(url) > 2083 or url in links:
        ++invalidLinkCount
        return False
    print ("Checking if url is absolute") #This is simple. Just check if url has http or https, it was done for us.
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        print ("Not Valid due to not http or https")
        ++invalidLinkCount
        return False
    try:
        
        print ("Checking if url is dynamic") #### Not good to just check if dynamic.
        #You need to make sure the dynamicness doesn't cause a trap. Some dynamic pages are okay.
        #Bst way to check if it's a trap is to check the key-value parameters. Such as item=123
        '''
        if '?' in url:
            return False
        
        for c in url:
            if c == '?':
                ++invalidLinkCount
                return False
        '''
        if '../' in url: # These 2 ifs check if there's some sort of weird URL concatenation happening
        	++invalidLinkCount
        	return False
        if '.php' in url[:-4] and '.ph' in url [-4:-1]: #Obviously there shouldn't be 2 .phps in a single URL
        	++invalidLinkCount
        	return False
        if url.count("/") >= 10
        	++invalidLinkCount
        	return False

    #### Asked in Discussion if it was okay to not check for infinite loop traps. Waiting on Response
        print ("Checking if .ics.uci.edu and not media")
        if ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return True
        else:
            ++invalidLinkCount
            return False

    except TypeError:
        print ("TypeError for ", parsed)
