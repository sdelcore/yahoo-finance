#!/usr/bin/python
"""
Created by: Spencer Delcore
Info:
    This script scrapes the table found in finance.yahoo.com/etf/lists
    and places all of the data in a CSV file.
"""
from lxml import html
import requests
import csv

#Return(mkt)
#url = "http://finance.yahoo.com/etf/lists?mod_id=mediaquotesetf&tab=tab1&scol=mkt3m&stype=desc&rcnt=100&page=1"
#Return(NAV)
#url = "http://finance.yahoo.com/etf/lists?mod_id=mediaquotesetf&tab=tab2&scol=nav3m&stype=desc&rcnt=100&page=1"
#Trading/Volume
#url = "http://finance.yahoo.com/etf/lists?mod_id=mediaquotesetf&tab=tab3&scol=volint&stype=desc&rcnt=100&page=1"
#Holdings
#url = "http://finance.yahoo.com/etf/lists?mod_id=mediaquotesetf&tab=tab4&scol=avgcap&stype=desc&rcnt=100&page=1"
#Risk
#url = "http://finance.yahoo.com/etf/lists?mod_id=mediaquotesetf&tab=tab5&scol=riskb&stype=desc&rcnt=100&page=1"
#operations
#url = "http://finance.yahoo.com/etf/lists?mod_id=mediaquotesetf&tab=tab6&scol=nasset&stype=desc&rcnt=100&page=1"

def get_num_of_etf():
    num_etf = ''
    url = "http://finance.yahoo.com/etf/lists?mod_id=mediaquotesetf&tab=tab1&scol=imkt&stype=desc&rcnt=20"
    page = requests.get(url)
    raw_page = html.fromstring(page.text)
    split_num = raw_page.xpath('//div[@class="ft"]/text()')[0][1:-7].split(',')
    for num in split_num:
        num_etf = num_etf + num
    return int(num_etf)
    
def get_url(tab_num, page_num):
    base_url = "http://finance.yahoo.com/etf/lists?mod_id=mediaquotesetf&tab=tab"
    return base_url + str(tab_num) + "&scol=tkr&stype=asc&rcnt=100&page=" + str(page_num)
    
def get_page(url):
    page = requests.get(url)
    raw_page = html.fromstring(page.text)
    table_col = raw_page.xpath('//th/descendant-or-self::*/text()')
    raw_table_data = raw_page.xpath('//td/descendant-or-self::*/text()')[5:]
    table_data = parse_data(raw_table_data, len(table_col))    
    return table_data, table_col
    
def parse_data(data, size):
    x = []
    for i in xrange(0, len(data), size):
         x.append(data[i:i+size])
    return x
    
def csv_writer(data, path):
    with open(path, "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        #writer.writerow([unicode(line).encode("utf-8") for line in data])
        #for line in data:
            #writer.writerow(line)
        for row in data:
            row = [c.encode('utf8') if isinstance(c, unicode) else c for c in row]
            writer.writerow(row)

if __name__ == "__main__":
    num_etf = get_num_of_etf()
    num_pages = ( num_etf / 100 ) + 1
    
    etf = [[]]
    
    for tab_num in range(1, 7):
        count = 1;
        for page_num in range(1, num_pages + 1):
            url = get_url(tab_num, page_num)
            print url
            table_data, table_col = get_page(url) 
                    
            if (tab_num == 1 and page_num == 1):
                etf[0] = table_col
                etf = etf + table_data
                
            elif (tab_num == 1 and page_num != 1):
                etf = etf + table_data
                
            elif (tab_num != 1):
                if (page_num == 1):
                    etf[0] = etf[0] + table_col[4:]
                    
                for ticker in table_data:
                    if (count < len(etf)):
                        if(ticker[1] != etf[count][1]):
                            na = ["N/A"] * len(ticker[4:])
                            etf[count] = etf[count] + na
                            if (count+1 < len(etf)):
                                if (ticker[1] == etf[count+1][1]):
                                    count = count + 1
                
                        etf[count] = etf[count] + ticker[4:]                
                    count = count + 1
                        
            else:
                print "something else"
                
    csv_writer(etf, 'yahoo.csv')
