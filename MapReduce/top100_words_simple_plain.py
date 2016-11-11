#   2016 Fall tdi
#   RUN AS:
#   time python Q1.py -r local ../datums/simple/part-00026.xml.bz2
#   time python Q1.py -r local ../datums/simple/part-000*

#   Useful Documentation 
#   https://pythonhosted.org/mrjob/guides/writing-mrjobs.html#multi-step-jobs
#   https://pythonhosted.org/mrjob/guides/quickstart.html#writing-your-first-job
#   https://pythonhosted.org/mrjob/guides/writing-mrjobs.html#job-protocols

from mrjob.job import MRJob
from mrjob.step import MRStep
import mrjob.protocol as mrjp
import re

WORD_RE = re.compile(r"[\w']+")            		# split the words with regex

#   Each question written as a separate class

class MRMostUsedWord(MRJob):

    INPUT_PROTOCOL = mrjp.RawValueProtocol
    INTERNAL_PROTOCOL = mrjp.JSONProtocol
    OUTPUT_PROTOCOL = mrjp.JSONValueProtocol		# does not write out the key
    #OUTPUT_PROTOCOL = mrjob.protocol.JSONProtocol
    
    # wrapper for multi steps

    def steps(self):

        return [
            MRStep(mapper=self.mapper_get_words,
                   combiner=self.combiner_count_words,
                   reducer=self.reducer_count_words),
            MRStep(reducer=self.reducer_find_max_word)
        ]

    def mapper_get_words(self, _, line):		# yield each word of a line - yields (word, 1)
        for word in WORD_RE.findall(line):		# convert to lower case to make 'The' and the 'the' same
	    yield (word.lower(), 1)
        
            

    def combiner_count_words(self, word, counts):
        yield (word, sum(counts))			# optimization: sum the words we've seen so far

    def reducer_count_words(self, word, counts):
        yield None, (sum(counts), word)			# send all (num_occurrences, word) pairs to the same reducer.
        						# num_occurrences is so we can easily use Python's max() function.

    # Since the input protocol is RawValueProtocol, the key will always be None and the value will be the text of the line.
    # As all input to this step has the same key, a single task will get all rows. 

    def reducer_find_max_word(self, _, word_count_pairs):
        count_words = [i for i in word_count_pairs]
        top100 = sorted(count_words, reverse=True)[0:100]
        print [(item[1], item[0]) for item in top100]
        return 0					# each item of word_count_pairs is (count, word),
						        # so yielding one results in key=counts, value=word
        


if __name__ == '__main__':
    MRMostUsedWord.run()


# could prove useful in future
# http://arunxjacob.blogspot.com/2013/11/hadoop-streaming-with-mrjob.html
# https://pythonhosted.org/mrjob/job.html#mrjob.job.MRJob.add_passthrough_option
