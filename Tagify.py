#!/usr/bin/env python
import nltk
import time
import wget
import os


class Tagify(object):

    """
    Tools for generating SEO relevant tags with given text.
    NNDB entries used for human names,
    NLTK library used for normal words.
    """

    def __init__(self):
        # nltk library globals
        self.exclude_tags = [
            "CC",
            "DT",
            "EX",
            "IN",
            "LS",
            "MD",
            "PRP",
            "PRP$",
            "SYM",
            "TO",
            "WDT",
            "WP",
            "WP$",
            "WRB",
            "''",
            "VB",
            "VBP",
            "VBZ",
            "RB",
            "RBR"
        ]  # nltk tags to exclude
        self.tagger = nltk.data.load(nltk.tag._POS_TAGGER)  # default tagger

        # human name globals
        self.nndb_file = "fullnames.dat"  # filename for nndb full names
        self.nndb_names = None  # container for names found

    def nl_tag(self, text):
        """
        Return a list of tuples with NL tags assigned [(word, nl_tag),...].
        NL tags classify words as nouns, verbs etc.

        Use for normal words only.
        """

        # tokenize and NL tag
        tokenized = text.strip().split()
        lower_tagged = self.tagger.tag(tokenized)

        return lower_tagged

    def relevant_tags(self, nl_tagged, allow_long=False):
        """
        Return a list of tag words given an NL tagged sentence,
        append current date.

        Use for normal words only.
        """

        # remove all words with exclude_tags present
        taglist = " ".join(
            [[word, ""][tag in self.exclude_tags] for (word, tag) in nl_tagged]
        ).split()

        # add today's date
        taglist.append(time.strftime("%B %d %Y"))

        return taglist

    def train_names_nndb(self):
        """
        Save names from nndb file to memory, in lowercase.
        """
        if not os.path.isfile(self.nndb_file):
            print "[DEBUG] NNDB file not found. Downloading all 26 pages..."
            self.download_nndb()

        print "[DEBUG] Training names..."
        with open(self.nndb_file, 'r') as raw:
            # remove /n from all lines in readlines
            full = map(lambda s: s.strip().lower(), raw.readlines())
        self.nndb_names = set(full)
        print "[DEBUG] Names Trained."

    def download_nndb(self):
        """
        Download fullnames from NNDB website, save into fullnames.dat.
        """

        for i in xrange(26):
            print "\n[DEBUG] %d pages left..." % (26 - i)
            # url pattern for all NNDB pages based on last names
            url = "http://www.nndb.com/lists/%d/000063%d" % (493 + i, 304 + i)

            # download page, get raw data.
            fn = wget.filename_from_url(url)
            with open(wget.download(url)) as raw:
                content = raw.readlines()
            os.remove(fn)

            for line in content:
                if "nndb.com/people" in line:
                    name = self.rmtags(line).replace("\n", "")
                    with open(self.nndb_file, 'a') as w:
                        w.write(name + "\n")
        print "[DEBUG] NNDB Download complete!"

    def rmtags(self, str):
        """
        Return str with all items in tags removed, including the tags.
        """

        # helper function for download_nndb
        if "<" in str:
            str = str.replace(str[str.find("<"):str.find(">") + 1], "")
            return self.rmtags(str)
        else:
            return str

    def text_cleanup(self, text):
        """
        Return a string of given text cleaned up for tagging.

        Changes:
        Lowercase, removed various items such as quotations,.
        """
        # items to remove completely
        remove = [
            "...",
            "'s",
            ":",
            ",",
            "?",
            "!",
            "lsquo;",
            "rsquo;",
            "&#x26;",
            ";",
            "~",
        ]
        # items to replace with whitespace
        space = [
            "' ",
            " '",
            "\" ",
            " \"",
            " (",
            ") ",
            " [",
            "] ",
            " - ",
            " -- "
        ]

        # pad space to detect quotations at beginning and ending
        text = " %s " % (text.strip())

        # remove and replace
        for rm in remove:
            if rm in text:
                text = text.replace(rm, "")
        for sp in space:
            if sp in text:
                text = text.replace(sp, " ")

        # unify lowercase, except abbreviations
        text = [
            [word,word.lower()][len(word)==1 or word[1].islower()] for \
            word in text.split()
        ]

        # format cleanup, output.
        text = " ".join(text).strip()
        return text

    def convert(self, text):
        """
        Return a list of tag words using NNDB entries for human names and nltk
        library for normal words.
        NNDB file nust be one fullname per line.
        """

        # print "[DEBUG] Sentence:", text
        # clean sentence, lowercase to unify casing.

        sentence = self.text_cleanup(text).split()

        # return text if text only has one word
        if len(sentence) == 1:
            return sentence

        # train names if not already trained.
        if not self.nndb_names:
            self.train_names_nndb()

        # exhaustive list of all possible 2-6 word consecutive combinations
        # in the given text
        possible_names = set()
        for namelen in range(2, [len(sentence) + 1, 7][len(sentence) >= 6]):
            for wordindex in range(len(sentence) - namelen + 1):
                possible_names.add(
                    " ".join(sentence[wordindex:wordindex + namelen]))

        # find names
        # print "[DEBUG] Finding names..."
        names_found = list(possible_names.intersection(self.nndb_names))

        # print "[DEBUG] Names found: "
        # print map(lambda x: x.title(), names_found)

        # find other tag words
        sentence = " ".join(sentence)
        for name in names_found:
            sentence = sentence.replace(name, "")
        sentence = " ".join(sentence.strip().split())  # cleanup
        other_tags = self.relevant_tags(self.nl_tag(sentence))

        # format output capitalize, ignore abbreviations
        names_found = map(lambda x: x.title(), names_found)
        other_tags = [
            [word, word.title()][len(word)==1 or word[1].islower()] for \
            word in other_tags
        ]
        output_tags = names_found + other_tags
        # print "[DEBUG] Output Tags:"
        # print output_tags
        return output_tags


if __name__ == '__main__':
    # simple test
    a = Tagify()
    print a.convert("jeff koons' whimsy takes over NYC wayne gretzky museum")
