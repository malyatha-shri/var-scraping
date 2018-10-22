# coding: utf-8

import requests
from bs4 import BeautifulSoup


class Crawler:

    def __init__(self):
        self.hello = "10-Q/10-K Crawler!"

    def filing_10q(self, cik, priorto, count):

        # generate the url to crawl
        base_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="+str(cik)+"&type=10-Q&dateb="+\
                   str(priorto)+"&owner=exclude&output=xml&count="+str(count)
        r = requests.get(base_url)
        data = r.text

        # get doc list data
        doc_list = self.create_document_list(data)

        return doc_list

    def create_document_list(self, data):
        # parse fetched data using beautifulsoup
        soup = BeautifulSoup(data)
        # store the link in the list
        link_list = list()

        # If the link is .htm convert it to .html
        for link in soup.find_all('filinghref'):
            url = link.string
            if link.string.split(".")[len(link.string.split("."))-1] == "htm":
                url += "l"
            link_list.append(url)
        link_list_final = link_list

        # List of url to the html documents
        doc_list = list()

        # Get all the doc
        for k in range(len(link_list_final)):
            required_url = link_list_final[k].replace('-index.html', '')
            txtdoc = required_url + ".txt"
            doc_list.append(txtdoc)

        return doc_list

