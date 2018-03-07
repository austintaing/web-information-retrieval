# Austin Taing
# CS 585-002
# HW2: Scrape

import urllib.request

def main():
    
    urlBase='http://www.kbb.com/'
    
    # List of cars to use
    carList = [['honda',
                ['accord', 'vp-sedan-4d'], #mid
                ['civic', 'hybrid-sedan-4d']], #compact
               ['toyota',
                ['camry', 'sedan-4d'], #mid
                ['corolla', 'l-sedan-4d']], #compact
               ['nissan',
                ['maxima', 's-sedan-4d'], #full
                ['altima','25-sedan-4d']], #mid
               ['ford',
                ['fusion', 's-sedan-4d'], #mid
                ['focus', 's-sedan-4d']], #compact
               ['chevrolet',
                ['malibu','ls-sedan-4d']], #full
               ['dodge',
                ['charger','se-sedan-4d']], #full
               ['volkswagen',
                ['passat', '18t-s-sedan-4d'], #mid
                ['jetta', '14t-s-sedan-4d']] #compact
               ]
    # Prices listed for Excellent, Very Good, Good, and Fair condition cars
    conditionList = ['\"excellentCondition\":', '\"veryGoodCondition\":', 
                     '\"goodCondition\":', '\"fairCondition\":']
    
    # Dump file
    outFile = open('Scrape raw output.txt', 'w')
    
    # Attempt to reach page for each model listed for every year from 2006-2016
    for make in range(len(carList)):
        for model in range(1,len(carList[make])):
            for year in range(2006,2017):
                # Build URL with each data combination
                # Hardcoded parameters for price type/domain, and mileage
                url = urlBase + carList[make][0] + '/' + carList[make][model][0]\
                    + '/' + str(year) + '/' + carList[make][model][1] + \
                    '/?intent=trade-in-sell&pricetype=privateparty&mileage=100000'
                
                req = urllib.request.Request(url)
                try:
                    #http ping from Python documentation
                    with urllib.request.urlopen(req) as response:
                        html = response.read()
                        
                    html = str(html)
                    
                    # Output each model year on one line
                    outFile.write(str(year) + '\t' + carList[make][0] + '\t' + carList[make][model][0])
                    for condition in conditionList:
                        # Parse for each of the four condition levels
                        # Output value for each condition level on line, separated by tabs
                        if(html.find(condition) != -1):
                            value = html[html.find(condition)+len(condition):]
                            value = value[:value.find(',')]
                            outFile.write('\t' + value)
                    outFile.write('\n')
                
                #error handling from Python documentation           
                except urllib.error.HTTPError as e:
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
                except urllib.error.URLError as e:
                    print('Failed to connect to server.')
                    print('Reason: ', e.reason)
                    
    outFile.close()
          
main()