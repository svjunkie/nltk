# Natural Language Toolkit: Corpus Access
#
# Copyright (C) 2001 University of Pennsylvania
# Author: Edward Loper <edloper@ldc.upenn.edu>
# URL: <http://nltk.sf.net>
# For license information, see LICENSE.TXT
#
# $Id$
#

# Goals for this module:
#
#  1. we want corpus access to be easy.  In particular, we don't want
#     people to need to think about file formats, or which tokenizers
#     etc to use.
#
#  2. we want corpus access to be consistant (each corpus is accessed
#     using the same basic system).
#
#  3. we want corpus access to be portable (eg not dependant on where
#     files are installed).
#
#  4. we want to make it easy to tell NLTK about new corpera
#
#     4a. it should be possible to tell NLTK about an existing corpus
#         without moving the corpus, or editing its contents in any way.
#
#  5. we want to be able to handle a wide variety of formats, including
#     formats where mutliple files are used to represent the same data
#     (eg standoff annotation). 

"""

Access to NLTK's standard distribution of corpora.  Each corpus is
accessed by an instance of a C{CorpusReader} class.  For information
about using these corpora, see the reference documentation for
L{CorpusReaderI}.  The following corpus readers are currently defined:

  - L{twenty_newsgroups}: A collection of approximately 20,000
     Usenet newsgroup documents, partitioned (nearly) evenly across 20
     different newsgroups.
     
  - L{brown}: Approximately 1,000,000 words of part-of-speech tagged
    text.  The text consists of exerpts from 500 English prose
    documents, all printed in the United States in 1961.  Each exerpt
    is approximately 2000 words long.  The experts are grouped into 15
    topical categories that cover a wide range of genres and styles.
  
  - L{gutenberg}: A collection fourteen public-domain English etexts
    from Project Gutenberg.  The texts are taken from seven different
    authors, and range from 7,500 words to 800,000 words.
  
  - L{roget}: The 11th edition of Roget's Thesaurus of English Words
    and Phrases, from Project Guttenberg.  Each entry in this corpus
    corresponds to a single thesaurus entries from Roget's thesaurus.
  
  - L{words}: A list of about 45,000 unique words and word forms.
    The word list contains mostly English words and names, but also
    contains some non-English words that occur frequently in English
    text.
  
  - L{ppattatch}: Information about approximately 30,000 instances
    of potentially ambigous prepositional phrase attatchments.  For
    each instance, the corpus specifies the verb and noun that the
    prepositional phrase might potentially attatch to; and the
    preposition and head noun of the prepositional phrase.  I{The
    interface to this corpus is not implemented yet.}

  - L{reuters}: A collection of approximately 21,500 documents that
    appeared on the Reuters newswire in 1987.  The documents were
    assembled and indexed with categories by Reuters.  I{The interface
    to this corpus is corpus is not implemented yet.}

  - L{treebank}: A collection of hand-annotated parse trees for
    Englsih text.  I{This corpus can only be distributed through
    LDC; it is therefore not included as part of the standard NLTK
    corpus set.  However, the C{treebank} object will provide access
    to this corpus, if it is installed.}
  
@group Corpus Readers: twenty_newsgroups, treebank, words, reuters
@var twenty_newsgroups: A collection of approximately 20,000
     Usenet newsgroup documents, partitioned (nearly) evenly across 20
     different newsgroups.
@var treebank: A collection of hand-annotated parse trees for
     english text.
@var words: A list of English words.
@var reuters: A collection of documents that appeared on Reuters
     newswire in 1987.
      
@todo: Add default basedir for OS-X?

@variable _BASEDIR: The base directory for NLTK's standard distribution
    of corpora.  This is read from the environment variable
    C{NLTK_CORPORA}, if it exists; otherwise, it is given a
    system-dependant default value.  C{_BASEDIR}'s value can be changed
    with the L{set_basedir()} function.
@type _BASEDIR: C{string}
"""

import sys, os.path, re
from nltk.tokenizer import WSTokenizer
from nltk.tree import TreebankTokenizer
from nltk.tagger import TaggedTokenizer
from nltk.parser.chunk import ChunkedTaggedTokenizer

#################################################################
# Base Directory for Corpora
#################################################################
def set_basedir(path):
    """
    Set the path to the directory where NLTK looks for corpora.
    
    @type path: C{string}
    @param path: The path to the directory where NLTK should look for
        corpora.
    """
    global _BASEDIR
    _BASEDIR = path

def get_basedir():
    """
    @return: The path of the directory where NLTK looks for corpora.
    @rtype: C{string}
    """
    return _BASEDIR

# Find a default base directory.
if os.environ.has_key('NLTK_CORPORA'):
    set_basedir(os.environ['NLTK_CORPORA'])
elif sys.platform.startswith('win'):
    if os.path.isdir(os.path.join(sys.prefix, 'nltk')):
        set_basedir(os.path.join(sys.prefix, 'nltk'))
    elif os.path.isdir(os.path.join(sys.prefix, 'lib', 'nltk')):
        set_basedir(os.path.join(sys.prefix, 'lib', 'nltk'))
    else:
        set_basedir(os.path.join(sys.prefix, 'nltk'))
elif os.path.isdir('/usr/lib/nltk'):
    set_basedir('/usr/lib/nltk')
elif os.path.isdir('/usr/local/lib/nltk'):
    set_basedir('/usr/local/lib/nltk')
elif os.path.isdir('/usr/share/nltk'):
    set_basedir('/usr/share/nltk')
else:
    set_basedir('/usr/lib/nltk')

#################################################################
# Corpus Reader Interface
#################################################################
class CorpusReaderI:
    """
    An accessor for a collection of natural language data.  This
    collection is organized as a set of named X{entries}.  Typically,
    each entry corresponds to a single file, and contains a single
    coherent text; but some corpora are divided into entries along
    different lines.

    A corpus can optionally contain a set of X{groups}, or collections
    of related entries.  The entries within a single group all have
    the same format; but different groups may have different formats.
    The set of a corpus's groups are often (but not always) mutually
    exclusive.  For a description of the groups that are available for
    a specific corpus, use the L{description()} method.

    The L{groups} method returns a list of the groups that are defined
    for a C{CorpusReader}'s corpus.  The L{entries()} method returns a
    list of the names of the entries in a group or corpus.  The
    X{entry reader} methods (listed below) are used to read the
    contents of individual entries.  The following example
    demonstrates the use of a C{Corpus}:

        >>> for newsgroup in twenty_newsgroups.groups():
        ...    for entry in twenty_newsgroup.entries(newsgroup):
        ...        do_something(newsgroup.tokenize(entry), newsgroup)

    Some corpora do not implement all of the entry reader methods; if
    a corpus doesn't implement an entry reader method, then that
    method will raise a C{NotImplementedError}.  Some corpora define
    new entry reader methods, for reading their contents in specific
    formats; see the documentation for individual implementations of
    the C{CorpusReaderI} interface for information about new entry reader
    methods.

    @group Entry Access: open, read, readlines, tokenize
    @group Subcorpus Access: subcorpora
    @group Metadata: name, description, licence, copyright,
        __str__, __repr__
    @sort: open, read, readlines, tokenize,
           name, description, __str__, __repr__
    """

    #////////////////////////////////////////////////////////////
    #// Corpus Information/Metadata
    #////////////////////////////////////////////////////////////
    def name(self):
        """
        @return: The name of this C{CorpusReader}'s corpus.
        @rtype: C{string}
        """
        raise AssertionError, 'CorpusReaderI is an abstract class'

    def description(self):
        """
        @return: A description of the contents of this
            C{CorpusReader}'s corpus; or C{None} if no description is
            available.
        @rtype: C{string} or C{None}
        """
        return None

    def license(self):
        """
        @return: Information about the license governing the use of
            this C{CorpusReader}'s corpus.
        @rtype: C{string}
        """
        return 'Unknown'

    def copyright(self):
        """
        @return: A copyright notice for this C{CorpusReader}'s corpus.
        @rtype: C{string}
        """
        return 'Unknown'

    #////////////////////////////////////////////////////////////
    #// Data access (entries)
    #////////////////////////////////////////////////////////////
    def entries(self):
        """
        @return: A list containing the names of the entries contained in
            this C{CorpusReader}'s corpus.
        @rtype: C{list} of C{string}
        """
        raise AssertionError, 'CorpusReaderI is an abstract class'

    def path(self, entry):
        """
        @return: The path of a file containing the given entry.
        @param entry: The name of the requested entry
        @rtype: C{string}
        """
        raise NotImplementedError, 'This corpus does not implement path()'

    def open(self, entry):
        """
        @return: A read-mode C{file} object for the given entry.
        @param entry: The name of the entry to read.
        @rtype: C{file}
        """
        raise NotImplementedError, 'This corpus does not implement open()'

    def read(self, entry):
        """
        @return: A string containing the contents of the given entry.
        @param entry: The name of the entry to read.
        @rtype: C{string}
        """
        raise NotImplementedError, 'This corpus does not implement read()'

    def readlines(self, entry):
        """
        @return: A list of the contents of each line in the given
            entry.  Trailing newlines are included.
        @param entry: The name of the entry to read.
        @rtype: C{list} of C{string}
        """
        raise NotImplementedError, 'This corpus does not implement readlines()'

    def tokenize(self, entry, tokenizer=None):
        """
        @return: A list of the tokens in the given entry.
        @param entry: The name of the entry to read.
        @param tokenizer: The tokenizer that should be used to
            tokenize the entry.  If no tokenizer is specified, then the
            default tokenizer for this corpus is used.
        @rtype: C{list} of L{Token<nltk.token.Token>}
        """
        raise NotImplementedError, 'This corpus does not implement tokenize()'
                          
    #////////////////////////////////////////////////////////////
    #// Structure access (groups)
    #////////////////////////////////////////////////////////////
    def groups(self):
        """
        @return: A list of the names of the groups contained in this
            C{CorpusReader}'s corpus.
        @rtype: C{list} of L{string}
        """
        raise AssertionError, 'CorpusReaderI is an abstract class'

    #////////////////////////////////////////////////////////////
    #// Printing
    #////////////////////////////////////////////////////////////
    def __repr__(self):
        """
        @return: A single-line description of this corpus.
        """
        str = self._name
        try:
            entries = self.entries()
            groups = self.groups()
            if entries:
                if groups:
                    str += (' (contains %d entries; %d groups)' %
                            (len(entries), len(groups)))
                else:
                    str += ' (contains %d entries)' % len(entries)
            elif groups:
                str += ' (contains %d groups)' % len(groups)
        except IOError:
            str += ' (not installed)'

        return '<Corpus: %s>' % str

    def __str__(self):
        """
        @return: A multi-line description of this corpus.
        """
        str = repr(self)[9:-1]
        if self._description:
            str += ':\n'
            str += '\n'.join(['  '+line for line
                              in self._description.split('\n')])
        return str

#################################################################
# General-purpose Corpus Implementation
#################################################################
class SimpleCorpusReader(CorpusReaderI):
    """
    A general-purpose implementation of the C{CorpusReader} interface
    that defines the set of entries and the contents of groups with
    regular expressions over filenames.  The C{SimpleCorpusReader}
    implementation is suitable for defining corpus readers for corpora
    where:
    
        - Each entry consists of the text in a single file.
        - Every entry has the same format.
        - The filenames of entries can be distinguished from the
          filenames of metadata files with a regular expression.
        - The set entries in each group can be distinguished with
          a single regular expression.

    For the purposes of defining regular expressions over path names,
    use the forward-slash character (C{'/'}) to delimit directories.
    C{SimpleCorpusReader} will automatically convert this to the
    appropriate path delimiter for the operating system.
    """
    def __init__(self,
                 # Basic Information
                 name, rootdir, entries_regexp,
                 # Grouping
                 groups=None,
                 # Meta-data
                 description=None, description_file=None, 
                 license_file=None,
                 copyright_file=None,
                 # Formatting meta-data
                 default_tokenizer=WSTokenizer()):
        """
        Construct a new corpus reader.  The parameters C{description},
        C{description_file}, C{license_file}, and C{copyright_file}
        specify optional metadata.  For the corpus reader's
        description, you should use C{description} or
        C{description_file}, but not both.

        @group Basic Information: name, rootdir, entries_regexp
        @group Grouping: groups
        @group Meta-data: description, license, copyright,
            description_file, license_file, copyright_file
        @group Formatting Meta-data: default_tokenizer

        @type name: C{string}
        @param name: The name of the corpus.  This name is used for
            printing the corpus reader, and for constructing
            locations.  It should usually be identical to the name of
            the variable that holds the corpus reader.
        @type rootdir: C{string}
        @param rootdir: The path to the root directory for the
            corpus.  If C{rootdir} is a relative path, then it is
            interpreted relative to the C{nltk.corpus} base directory
            (as returned by L{nltk.corpus.basedir()}).
        @type entries_regexp: C{regexp} or C{string}
        @param entries_regexp: A regular expression over paths that
            defines the set of files that should be listed as
            entities for the corpus.  The paths that this is tested
            against are all relative to the corpus's root directory.
            Use the forward-slash character (C{'/'} to delimit
            subdirectories; C{SimpleCorpusReader} will automatically convert
            this to the appropriate path delimiter for the operating
            system.
        @type groups: C{list} of C{(string, regexp)} tuples
        @param groups: A list specifying the groups for the corpus.
            Each element in this list should be a pair
            C{(M{groupname}, M{regexp})}, where C{M{groupname}} is the
            name of a group; and C{M{regexp}} is a regular expression
            over paths that defines the set of files that should be
            listed as entities for that group.  The paths that these
            regular expressions are tested against are all relative
            to the corpus's root directory.  Use the forward-slash
            character (C{'/'} to delimit subdirectories;
            C{SimpleCorpusReader} will automatically convert this to the
            appropriate path delimiter for the operating system.
        @type description: C{string}
        @param description: A description of the corpus.
        @type description_file: C{string}
        @param description_file: The path to a file containing a
            description of the corpus.  If this is a relative path,
            then it is interpreted relative to the corpus's root
            directory.
        @type license_file: C{string}
        @param license_file: The path to a file containing licensing
            information about the corpus.  If this is a relative
            path, then it is interpreted relative to the corpus's root
            directory.
        @type copyright_file: C{string}
        @param copyright_file: The path to a file containing a
            copyright notice for the corpus.  If this is a relative
            path, then it is interpreted relative to the corpus's root
            directory.
        @type default_tokenizer: L{TokenizerI}
        @param default_tokenizer: The default tokenizer that should be
            used for the corpus reader's L{tokenize} method.
        """
        # Compile regular expressions.
        if isinstance(entries_regexp, type('')):
            entries_regexp = re.compile(entries_regexp)
        if groups is None: groups = []
        else: groups = groups[:]
        for i in range(len(groups)):
            if isinstance(groups[i][1], type('')):
                groups[i] = (groups[i][0], re.compile(groups[i][1]))

        # Save parameters
        self._name = name
        self._original_rootdir = rootdir
        self._entries_regexp = entries_regexp
        self._grouplists = groups
        self._description = description
        self._description_file = description_file
        self._license = None
        self._license_file = license_file
        self._copyright = None
        self._copyright_file = copyright_file
        self._default_tokenizer = default_tokenizer

        # Postpone actual initialization until the corpus is accessed;
        # this gives the user a chance to call set_basedir(), and
        # prevents "import nltk.corpus" from raising an exception.
        # We'll also want to re-initialize the corpus if basedir
        # ever changes.
        self._basedir = None
        self._rootdir = None
        self._entries = None
        self._groups = None

    #////////////////////////////////////////////////////////////
    #// Initialization
    #////////////////////////////////////////////////////////////
    def _initialize(self):
        "Make sure that we're initialized."
        # If we're already initialized, then do nothing.
        if self._basedir == get_basedir(): return

        # Make sure the corpus is installed.
        self._basedir = get_basedir()
        self._rootdir = os.path.join(get_basedir(), self._original_rootdir)
        if not os.path.isdir(self._rootdir):
            raise IOError('%s is not installed' % self._name)

        # Build a filelist for the corpus
        filelist = self._find_files(self._rootdir)
        filelist = [os.path.join(*(file.split('/')))
                    for file in filelist]

        # Find the files that are entries
        self._entries = [f for f in filelist
                         if self._entries_regexp.match(f)]

        # Find the files for each group.
        self._groups = {}
        for (groupname, regexp) in self._grouplists:
            self._groups[groupname] = [f for f in filelist
                                       if regexp.match(f)]

        # Read metadata from files
        if self._description is None and self._description_file is not None:
            path = os.path.join(self._rootdir, self._description_file)
            self._description = open(path).read()
        if self._license is None and self._license_file is not None:
            path = os.path.join(self._rootdir, self._license_file)
            self._license = open(path).read()
        if self._copyright is None and self._copyright_file is not None:
            path = os.path.join(self._rootdir, self._copyright_file)
            self._copyright = open(path).read()

    def _find_files(self, path, prefix=''):
        filelist = []
        for name in os.listdir(path):
            filepath = os.path.join(path, name)
            if os.path.isfile(filepath):
                filelist.append('%s%s' % (prefix, name))
            elif os.path.isdir(filepath):
                filelist += self._find_files(filepath,
                                             '%s%s/' % (prefix, name))
        return filelist

    #////////////////////////////////////////////////////////////
    #// Corpus Information/Metadata
    #////////////////////////////////////////////////////////////
    def name(self):
        return self._name

    def description(self):
        self._initialize()
        return self._description

    def license(self):
        self._initialize()
        return self._license

    def copyright(self):
        self._initialize()
        return self._copyright

    #////////////////////////////////////////////////////////////
    #// Data access (entries)
    #////////////////////////////////////////////////////////////
    def entries(self, group=None):
        self._initialize()
        if group is None: return self._entries
        else: return self._groups.get(group) or []

    def path(self, entry):
        self._initialize()
        return os.path.join(self._rootdir, entry)

    def open(self, entry):
        return open(self.path(entry))

    def read(self, entry):
        return self.open(entry).read()

    def readlines(self, entry):
        return self.open(entry).readlines()

    def tokenize(self, entry, tokenizer=None):
        if tokenizer is None: tokenizer = self._default_tokenizer
        source = '%s/%s' % (self._name, entry)
        return tokenizer.tokenize(self.read(entry), source=source)

    #////////////////////////////////////////////////////////////
    #// Structure access (groups)
    #////////////////////////////////////////////////////////////

    def groups(self):
        self._initialize()
        return self._groups.keys()

#################################################################
# Corpus Implementation for Roget's Thesaurus
#################################################################

class RogetCorpusReader(CorpusReaderI):
    """
    A C{CorpusReader} implementation for Roget's Thesaurus.  Each
    corpus entry corresponds to a single thesaurus entry.  These
    entries are all read from a single thesaurus file.
    """
    def __init__(self, name, rootdir, data_file):
        self._name = name
        self._original_rootdir = rootdir
        self._data_file = data_file

        # Postpone actual initialization until the corpus is accessed;
        # this gives the user a chance to call set_basedir(), and
        # prevents "import nltk.corpus" from raising an exception.
        # We'll also want to re-initialize the corpus if basedir
        # ever changes.
        self._basedir = None
        self._entries = None
        self._rootdir = None
        self._groups = None
        self._description = None
        self._licence = None
        self._copyright = None

    #////////////////////////////////////////////////////////////
    #// Initialization
    #////////////////////////////////////////////////////////////
    LICENSE_RE = re.compile(r'\*+START\*+THE SMALL PRINT[^\n]' +
                            r'(.*?)' +
                            r'\*+END\*+THE SMALL PRINT', re.DOTALL)
    
    DESCRIPTION_RE = re.compile('(' + r'\*'*60 + r'.*?' +
                                r'='*60+'\s+-->)', re.DOTALL)

    ENTRY_RE = re.compile(r'^     #(\w+)\.\s+(' + #r'(([^-]*)\s--' +
                          r'.*?\n)',
                          re.DOTALL | re.MULTILINE)
    
    def _initialize(self):
        # If we're already initialized, then do nothing.
        if self._basedir == get_basedir(): return

        # Make sure the corpus is installed.
        self._basedir = get_basedir()
        self._rootdir = os.path.join(get_basedir(), self._original_rootdir)
        if not os.path.isdir(self._rootdir):
            raise IOError('%s is not installed' % self._name)

        # Read in the data file.
        datapath = os.path.join(self._rootdir, self._data_file)
        data = open(datapath).read()

        # Extract the license
        self._license = self.LICENSE_RE.search(data).group(1)

        # Extract the description
        self._description = self.DESCRIPTION_RE.search(data).group(1)

        # Remove line number markings and other comments
        data = re.sub(r'<--\s+.*?-->', '', data)
        #p\.\s+\d+\s+-->', '', data)
        #data = re.sub(r'<--\s+p\.\s+\d+\s+-->', '', data)

        # Divide the thesaurus into entries.
        entries = re.split('\n     #', data)

        self._entrylist = []
        self._entries = {}
        for entry in entries[1:]:
            (key, contents) = entry.split('--', 1)
            key = ' '.join(key.split()) # Normalize the key.
            self._entrylist.append(key)
            self._entries[key] = contents.strip()

    #////////////////////////////////////////////////////////////
    #// Corpus Information/Metadata
    #////////////////////////////////////////////////////////////

    def name(self):
        return self._name

    def description(self):
        self._initialize()
        return self._description

    def license(self):
        self._initialize()
        return self._license

    def copyright(self):
        self._initialize()
        return self._copyright

    #////////////////////////////////////////////////////////////
    #// Data access (entries)
    #////////////////////////////////////////////////////////////
    def entries(self, group=None):
        self._initialize()
        return self._entrylist

    def path(self, entry):
        raise NotImplementedError, 'roget does not implement path()'
    
    def open(self, entry):
        raise NotImplementedError, 'roget does not implement open()'

    def read(self, entry):
        return self._entries[entry]

    def readlines(self, entry):
        return self._entries[entry].splitlines()

    def tokenize(self, entry, tokenizer=WSTokenizer()):
        source = '%s/%s' % (self._name, entry)
        return tokenizer.tokenize(self.read(entry), source=source)

    #////////////////////////////////////////////////////////////
    #// Structure access (groups)
    #////////////////////////////////////////////////////////////

    def groups(self):
        return []

#################################################################
# Corpus Implementation for Treebank Data
#################################################################

class TreebankCorpusReader(CorpusReaderI):
    """
    A corpus reader implementation for the Treebank.
    """
    def __init__(self, name, rootdir, description_file=None,
                 license_file=None, copyright_file=None):
        self._name = name
        self._original_rootdir = rootdir
        self._description_file = description_file
        self._license_file = license_file
        self._copyright_file = copyright_file

        # 4 groups:
        self._groups = ('raw', 'tagged', 'parsed', 'merged')

        # Are the merged entries "virtual" (i.e., constructed on the
        # fly from the parsed & tagged entries)?  This is true iff the
        # treebank corpus doesn't contain a "merged" subdirectory.
        self._virtual_merged = 0
        
        # Postpone actual initialization until the corpus is accessed;
        # this gives the user a chance to call set_basedir(), and
        # prevents "import nltk.corpus" from raising an exception.
        # We'll also want to re-initialize the corpus if basedir
        # ever changes.
        self._basedir = None
        self._description = None
        self._license = None
        self._copyright = None
        self._entries = None
        self._group_entries = None

    #////////////////////////////////////////////////////////////
    #// Initialization
    #////////////////////////////////////////////////////////////
    def _initialize(self):
        "Make sure that we're initialized."
        # If we're already initialized, then do nothing.
        if self._basedir == get_basedir(): return

        # Make sure the corpus is installed.
        self._basedir = get_basedir()
        self._rootdir = os.path.join(get_basedir(), self._original_rootdir)
        if not os.path.isdir(self._rootdir):
            raise IOError('%s is not installed' % self._name)

        # Get the list of entries in each group.
        self._group_entries = {}
        for group in self._groups:
            self._find_entries(group)
        if not self._group_entries.has_key('merged'):
            self._virtual_merged = 1
            self._find_virtual_merged_entries()

        # Get the overall list of entries
        self._entries = []
        for entries in self._group_entries.values():
            self._entries += entries

        # Read metadata from files
        if self._description is None and self._description_file is not None:
            path = os.path.join(self._rootdir, self._description_file)
            self._description = open(path).read()
        if self._license is None and self._license_file is not None:
            path = os.path.join(self._rootdir, self._license_file)
            self._license = open(path).read()
        if self._copyright is None and self._copyright_file is not None:
            path = os.path.join(self._rootdir, self._copyright_file)
            self._copyright = open(path).read()

    def _find_entries(self, group):
        path = os.path.join(self._rootdir, group)
        if os.path.isdir(path):
            self._group_entries[group] = [os.path.join(group, f)
                                          for f in os.listdir(path)]

    def _find_virtual_merged_entries(self):
        # Check to make sure we have both the .tagged and the .parsed files.
        self._group_entries['merged'] = merged = []
        is_tagged = {}
        for entry in self._group_entries.get('tagged', []):
            basename = os.path.basename(entry).split('.')[0]
            is_tagged[basename] = 1
        for entry in self._group_entries.get('parsed', []):
            basename = os.path.basename(entry).split('.')[0]
            if is_tagged.get(basename):
                merged.append(os.path.join('merged', '%s.mrg' % basename))

    #////////////////////////////////////////////////////////////
    #// Corpus Information/Metadata
    #////////////////////////////////////////////////////////////
    def name(self):
        return self._name

    def description(self):
        self._initialize()
        return self._description

    def license(self):
        self._initialize()
        return self._license

    def copyright(self):
        self._initialize()
        return self._copyright

    def rootdir(self):
        """
        @return: The path to the root directory for this corpus.
        @rtype: C{string}
        """
        self._initialize()
        return self._rootdir

    #////////////////////////////////////////////////////////////
    #// Data access (entries)
    #////////////////////////////////////////////////////////////
    def entries(self, group=None):
        self._initialize()
        if group is None: return self._entries
        else: return self._group_entries.get(group) or []

    def path(self, entry):
        self._initialize()
        if self._virtual_merged and entry.startswith('merged'):
            estr = 'The given entry is virtual; it has no path'
            raise NotImplementedError, estr
        else:
            return os.path.join(self._rootdir, entry)

    def open(self, entry):
        return open(self.path(entry))

    def read(self, entry):
        if self._virtual_merged and entry.startswith('merged'):
            basename = os.path.basename(entry).split('.')[0]
            tagged_entry = os.path.join('tagged', '%s.pos' % basename)
            parsed_entry = os.path.join('parsed', '%s.prd' % basename)
            tagged = self.read(tagged_entry)
            parsed = self.read(parsed_entry)
            return self.merge(tagged, parsed)
        else:
            return self.open(entry).read()

    def readlines(self, entry):
        if self._virtual_merged and entry.startswith('merged'):
            contents = self.read(entry)
            return [line+'\n' for line in contents.split('\n')]
        else:
            return self.open(entry).readlines()

    # Default tokenizers.
    _ws_tokenizer = WSTokenizer()
    _tb_tokenizer = TreebankTokenizer()
    _tag_tokenizer = TaggedTokenizer()
    
    def tokenize(self, entry, tokenizer=None):
        if tokenizer is None:
            if entry.startswith('merged'):
                tokenizer = self._tb_tokenizer
            elif entry.startswith('tagged'):
                tokenizer = self._tag_tokenizer
            elif entry.startswith('parsed'):
                tokenizer = self._tb_tokenizer
            elif entry.startswith('raw'):
                tokenizer = self._ws_tokenizer

        # Read in the contents of the file.
        return tokenizer.tokenize(self.read(entry))

    #////////////////////////////////////////////////////////////
    #// Parsed/Tagged Merging
    #////////////////////////////////////////////////////////////
    def merge(self, tagged, parsed):
        """
        Create a merged treebank file (containing both parse and
        part-of-speech tagging information), given the parsed contents
        and the part-of-speech tagged contents for that file.

        This merge procedure is somewhat robust.  In particular:
          - It handles brace conversions (eg C{'('} -> C{'-LRB-'}).  It
            also accepts the (incorrect?) variants C{'*LRB*'} etc., and
            automatically convers the to the standard C{'-LRB-'} forms.
          - It complains but does not fail if the parse file drops
            the last word or the last quote mark.
          - It handles traces & other null elements in the parse.
          - It handles extra elements in the parse that are not present
            in the tagged text.  (E.g. in C{'(WHP-1 0)'}.

        This is enough robustness to handle wsj_0001 through wsj_0099;
        It hasn't yet been tested on the rest of the treebank.

        @param tagged: The part-of-speech tagged contents of the file
            to merge.
        @type tagged: C{string}
        @param parsed: The parse contents of the file to merge.
        @type parsed: C{string}
        @return: The merged contents of the treebank file.
        @rtype: C{string}

        @todo: Increase the robustness of this method.
        """
        # Clean up the tagged contents of the file.
        tagged = tagged.replace('[', ' ').replace(']', ' ')
        tagged = re.sub('={10,}', '', tagged) # >=10 equals signs
        tagged = tagged.replace('{', '-LCB-')
        tagged = tagged.replace('}', '-RCB-')
        tagged = tagged.replace('(', '-LRB-')
        tagged = tagged.replace(')', '-RRB-')

        # Divide the tagged contents into a list of words.  Reverse
        # it, so we can use pop() to remove one word at a time.
        self._tagged_words = tagged.split()

        # Use re.sub to replace words with tagged words.  The regexp
        # we're using will only match words, not part-of-speech tags.
        # Use a helper method (_merge_tag) to find the replacement for
        # each match.
        try:
            self._mismatches = 0
            self._first_mismatch = None
            self._tagged_index = 0
            merged = re.sub(r'\s([^\s\(\)]+)', self._merge_tag, parsed)
        except IndexError:
            raise ValueError('Merge failed: more words in the parsed '+
                             'contents than in the tagged contents')

        # Check that we used all tagged words.
        if self._tagged_index != len(self._tagged_words):
            if (self._tagged_index == (len(self._tagged_words)-1) and
                self._tagged_words[-1] == "''/''"):
                print 'Warning: dropped close quote'
            elif self._tagged_index == (len(self._tagged_words)-1):
                print ('Warning: dropped last word (%r)' %
                       self._tagged_words[-1])
            else:
                print self._tagged_index, len(self._tagged_words)
                print self._tagged_words[-5:]
                raise ValueError('Merge failed: more words in the tagged '+
                                 'contents than in the parsed contents')
        
        return merged

    def _merge_tag(self, match):
        """
        A helper function for L{merge}, that is used as the C{repl}
        argument for a regular expression substitution.  Given the
        regexp match for a word in the treebank, return the
        corresponding tagged word.
        """
        # Get the next parsed word
        parseword = match.group(1)

        # Annoying clean-up
        if parseword[:1] == '*' and parseword[-1:] == '*':
            if re.match(r'\*[LR][CRS]B\*', parseword):
                parseword = '-' + parseword[1:-1] + '-'

        # Get the next tagged word.
        taggedword = self._tagged_words[self._tagged_index]
        split = taggedword.rfind('/')
        if split == -1:
            raise ValueError('Merge failed: untagged word %s' % taggedword)
        word = taggedword[:split].replace('\\', '')
        tag = taggedword[split+1:]

        # If they don't match, then try returning the parse word, and
        # continuing.
        if word != parseword:
            if not parseword.startswith('*'):
                self._mismatches += 1
                if self._mismatches == 1:
                    self._first_mismatch = '%r vs. %r' % (word, parseword)
                if self._mismatches > 5:
                    print self._tagged_words[self._tagged_index:
                                             self._tagged_index+5]
                    raise ValueError("Merge failed: tagged & parsed files "+
                                     "don't match:\n  "+ self._first_mismatch)
            return word
            
        # If they match, then return the tagged word, expressed as a
        # tree constituant.
        self._mismatches = 0
        self._tagged_index += 1
        return ' (%s %s)' % (tag, word)
        
    #////////////////////////////////////////////////////////////
    #// Structure access (groups)
    #////////////////////////////////////////////////////////////

    def groups(self):
        return self._groups


#################################################################
# Corpus Implementation for the PP Attatchment Corpus
#################################################################

# Not implemented yet    

#################################################################
# Corpus Implementation for Reuters
#################################################################

# Not implemented yet    

#################################################################
# The standard corpora
#################################################################

###################################################
## 20 Newsgroups
groups = [(ng, ng+'/.*') for ng in '''
    alt.atheism rec.autos sci.space comp.graphics rec.motorcycles
    soc.religion.christian comp.os.ms-windows.misc rec.sport.baseball
    talk.politics.guns comp.sys.ibm.pc.hardware rec.sport.hockey
    talk.politics.mideast comp.sys.mac.hardware sci.crypt
    talk.politics.misc comp.windows.x sci.electronics
    talk.religion.misc misc.forsale sci.med'''.split()]
twenty_newsgroups = SimpleCorpusReader(
    '20_newsgroups', '20_newsgroups/', '.*/.*', groups,
    description_file='../20_newsgroups.readme')

###################################################
## Brown
groups = [('press: reportage', r'ca\d\d'), ('press: editorial', r'cb\d\d'),
          ('press: reviews', r'cc\d\d'), ('religion', r'cd\d\d'),
          ('skill and hobbies', r'ce\d\d'), ('popular lore', r'cf\d\d'),
          ('belles-lettres', r'cg\d\d'),
          ('miscellaneous: government & house organs', r'ch\d\d'),
          ('learned', r'cj\d\d'), ('fiction: general', r'ck\d\d'),
          ('fiction: mystery', r'cl\d\d'), ('fiction: science', r'cm\d\d'),
          ('fiction: adventure', r'cn\d\d'), ('fiction: romance', r'cp\d\d'),
          ('humor', r'cr\d\d')]
brown = SimpleCorpusReader(
    'brown', 'brown/', r'c\w\d\d', groups, description_file='README')
 
###################################################
## Gutenberg
groups = [('austen', 'austen-.*'), ('bible', 'bible-.*'),
          ('blake', 'blake-.*'), ('chesterton', 'chesterton-.*'),
          ('milton', 'milton-.*'), ('shakespeare', 'shakespeare-.*'),
          ('whitman', 'whitman-.*')]
gutenberg = SimpleCorpusReader(
    'gutenberg', 'gutenberg/', r'.*\.txt', groups, description_file='README')

###################################################
## PP Attatchment

# Not supported yet

###################################################
## Roget

roget = RogetCorpusReader('roget', 'roget/', 'roget15a.txt')

###################################################
## Words corpus (just English at this point)

words = SimpleCorpusReader(
    'words', 'words/', r'words') #, description_file='README')


###################################################
## Treebank (fragment distributed with NLTK)

treebank = TreebankCorpusReader('treebank', 'treebank/',
                                description_file='README')

###################################################
## Reuters corpus

# Not supported yet

#################################################################
# Testing/Example use
#################################################################

def _truncate_repr(obj, n):
    s = repr(obj)
    if len(s) < n: return s
    else: return s[:n-3] + '...'

def _test_corpus(corpus):
    print '='*70
    print corpus.name().center(70)
    print '-'*70
    print 'description() = ' + _truncate_repr(corpus.description(), 70-16)
    print 'license()     = ' + _truncate_repr(corpus.license(), 70-16)
    print 'copyright()   = ' + _truncate_repr(corpus.copyright(), 70-16)
    print 'entries()     = ' + _truncate_repr(corpus.entries(), 70-16)
    print 'groups()      = ' + _truncate_repr(corpus.groups(), 70-16)
    entry = corpus.entries()[0]
    contents = corpus.read(entry)
    print 'read(e0)      = ' + _truncate_repr(contents, 70-16)
    if len(contents) > 50000: return
    print 'tokenize(e0)  = ' + _truncate_repr(corpus.tokenize(entry), 70-16)

def _test_treebank():
    _test_corpus(treebank)
    print 'er, et, ep, em = raw, tagged, parsed, merged'
    er = treebank.entries('raw')[0]
    et = treebank.entries('tagged')[0]
    ep = treebank.entries('parsed')[0]
    em = treebank.entries('merged')[0]
    for (name, entry) in zip('er et ep em'.split(), (er, et, ep, em)):
        contents = treebank.read(entry)
        tokenized = treebank.tokenize(entry)
        print 'read(%s)      = %s' % (name, _truncate_repr(contents, 70-16))
        print 'tokenize(%s)  = %s' % (name, _truncate_repr(tokenized, 70-16))

def demo():
    _test_corpus(twenty_newsgroups)
    _test_corpus(brown)
    _test_corpus(gutenberg)
    _test_corpus(roget)
    _test_corpus(words)
    _test_treebank()
    print '='*70
    
if __name__ == '__main__':
    demo()
