#!/usr/bin/env python
import wget
from os import remove
from pprint import pprint as pp

class TopixTitles:
    """
    Tool to grab news titles from Topix Newswire pages.
    """

    def __init__(self):
        ## vars that go here are globally accessible for all funcitons.
        # global variables
        self.topix_url = "http://www.topix.com/wire/entertainment"


    def get_titles(self):
        """
        Return a list of titles grabbed from a Topix Newswire page.
        """

        # grab topix content
        filename = wget.filename_from_url(self.topix_url) # get filename
        print "[DEBUG] Downloading from topix..."
        with open(wget.download(self.topix_url)) as raw: # download and open
            content = raw.readlines() # save content as list
            print "[DEBUG] Content saved."
        try:
        	remove(filename) # remove downloaded file, if exist
        except:
        	print "[DEBUG] Cannot download topix page."
        	return 0

        # filter results
        titles = [] # container for titles
        for line in content:
            if "<a t=\"artclick\"" in line:
            	# find and filter out title
                titles.append(self.rmtags(line[:line.find("<img")]).strip())
        pp(titles) # pretty print titles to console

        # return list of titles
        return titles


    def rmtags(self, str):
        """
        Return a string with all tag items removed.

        ie. 
        input: "<title><em>This</em>is a string</title>"
        output: "This is a string"
        """

        ## (this is a helper function)
        if "<" in str:
            str = str.replace(str[str.find("<"):str.find(">") + 1], "")
            return self.rmtags(str) # recursive call till removed all tags
        else:
            return str


if __name__ == '__main__':
    ## Code here will be run if this file is ran by itself.

    # create class
    topix = TopixTitles()
    topix.get_titles()
