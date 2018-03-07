# Austin Taing
# CS 585-002
# HW3 - Crawl

import requests
import queue
import hashlib
import re
import time
import urllib.parse
import socket
import sys

# Canonicalizes a given URL
#  String url - the URL to be canonicalized
#  String src - URL to use for converting from relative URL
def canonURL(url, src):
    url = urllib.parse.urljoin(src, url)
    return url

# Reads given string input and enqueues found hyperlinks into work queue
#  String text - the page text to be parsed
def parse(text):
    hrefs = re.findall('href="[^ #"][^ "]+"', text)
    for i in range(len(hrefs)):
        hrefs[i] = hrefs[i][6:-1]
    return hrefs#+srcs+urls

# Checks if a given URL has been processed previously by the crawler
#  String url - The URL to be checked
#  List<string> known - set of previously visited URLs' hashes
def urlIsKnown(url, known):
    hURL = hashlib.md5(url.encode())
    if(hURL.hexdigest() in known):
        ret = True
    else:
        known.add(hURL.hexdigest())
        ret = False
    return ret

def mayVisit(url):
    if('uky.edu/' in url):
        ret = True
    else:
        ret = False
    return ret

def lookup(url, cache):
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    if host in cache:
        ipaddress = cache[host]
    else:
        try:
            ipaddress = socket.gethostbyname(host)
            cache[host] = ipaddress
        except:
            dnslog = open('DNSLog.txt', 'a')
            if(host == None):
                dnslog.write('Ill-formed url: ' + url + '\n')
            else:
                dnslog.write('Lookup failed for host ' + host + '\n')
            dnslog.close()
            return url, None
    parsed = parsed._replace(netloc=ipaddress)
    new_url = parsed.geturl()    
    return new_url, host

# Primary crawling operation, controlled by work queue
def crawl():
    wq = queue.Queue()    # The work queue, containing URLs to be processed
    wq.put(("http://www.uky.edu/UKHome", 0))  # Seed queue with UK homepage
    contentCount = {}
    urlList = {hashlib.md5(b"http://www.uky.edu/UKHome").hexdigest()}
    log = open("DebugLog.txt", 'w')
    dnsCache = {}
    
    startTime = time.time()
    lastUpdate = 0
    contentCount['css'] = 0
    while(not wq.empty() and time.time() - startTime < 750000):
        try:
            rawURL, depth = wq.get()
            
            url, host = lookup(rawURL, dnsCache)
            if(url == rawURL):
                log.write(str(round(time.time() - startTime, 3)) + ': DNS lookup failed for ' + url + '\n')
                continue
            
            if('.css' in url):
                log.write(str(round(time.time() - startTime, 3)) + ': CSS link ' + url + '\n')
                contentCount['css'] +=1
                continue
            
            #log.write(str(round(time.time() - startTime, 3)) + ': Attempting to connect to ' + url + '\n')
            
            try:
                req = requests.head(url, headers = {'Host':host}, timeout = 2, allow_redirects = True)
            except ConnectionError:
                log.write(str(round(time.time() - startTime, 3)) + ':\tFailed to connect to ' + rawURL +'\n')
                continue
            except requests.exceptions.ReadTimeout:
                log.write(str(round(time.time() - startTime, 3)) + ':\tRequest to ' + rawURL +' timed out\n')
                continue
            except Exception as ex:
                log.write(str(round(time.time() - startTime, 3)) + ':\tUnspecified error when connecting to ' + rawURL +' - ' + str(sys.exc_info()[0]) + '\n')
                continue
            
            if(req.status_code == 200 and 'content-type' in req.headers):
                contentType = req.headers['content-type']
                contentType = contentType.split(';')[0]
                if(contentType not in contentCount):
                    contentCount[contentType] = 0
                contentCount[contentType] += 1
                
                links = []
                if('text/html' in contentType):
                    #log.write(str(round(time.time() - startTime, 3)) + ': Attempting to fetch payload from ' + url + '\n')
                    try:
                        req = requests.get(url, headers={'Host':host}, timeout = 2)
                        url = req.url
                        if(req.status_code == requests.codes.ok):
                            links = parse(req.text)
                            #log.write(str(round(time.time() - startTime, 3)) + ':\tPayload fetched and parsed\n')
                        else:
                            log.write(req.status_code + ' Bad request to ' + rawURL + '\n')
                    except ConnectionError:
                        log.write(str(round(time.time() - startTime, 3)) + ':\tFailed to connect to ' + rawURL +'\n')
                    except requests.exceptions.ReadTimeout:
                        log.write(str(round(time.time() - startTime, 3)) + ':\tRequest to ' + rawURL +' timed out\n')
                    except Exception as ex:
                        log.write(str(round(time.time() - startTime, 3)) + ':\tUnspecified error when connecting to ' + rawURL +' - ' + str(sys.exc_info()[0]) + '\n')
                        
                for newURL in links:
                    cURL = canonURL(newURL, url)
                    if(mayVisit(cURL) and not urlIsKnown(cURL, urlList) and depth < 4):
                        wq.put((cURL, depth+1))
                        
            else:
                log.write(str(round(time.time() - startTime, 3)) + ':\tError when connecting to ' + rawURL +' - HTTP code ' + str(req.status_code) +'\n')
                
            if(time.time() - startTime > lastUpdate + 600):
                lastUpdate = time.time() - startTime
                log.write(str(round(time.time() - startTime, 3)) + ':\t')
                for i in contentCount:
                    log.write(i + ':' + str(contentCount[i]) + ', ')
                log.write('\n')
            
        except:
            log.write('Unexpected error\n')
    
    log.close()
    
    result = open('Crawl Results 2.txt', 'w')
    result.write('Page types\n')
    for i in contentCount:
        result.write(i + '\t' + str(contentCount[i]) + '\n')
        
    result.write('\nSubdomains\n')
    for i in dnsCache:
        result.write(i + '\n')
    result.close()
    return

crawl()