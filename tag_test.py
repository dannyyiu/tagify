#!/usr/bin/env python
from Tagify import Tagify
from TopixTitles import TopixTitles


if __name__ == '__main__':
    ## run to test Tagify with realtime topix title batches

    # download new topix titles
    downloader = TopixTitles()
    titles = downloader.get_titles() # contains a list of titles

    # test titles with tagging script
    tagger = Tagify()
    for title in titles:
        print "\nTitle: %s" % title
        print "Tags:", tagger.convert(title)