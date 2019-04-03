from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS

# Constants for scaled f-score
DEFAULT_BETA = 2
DEFAULT_SCALER_ALGO = 'normcdf'

DEFAULT_PMI_THRESHOLD_COEFFICIENT = 8

DEFAULT_MINIMUM_TERM_FREQUENCY = 3

DEFAULT_DIV_ID = 'd3-div-1'

DEFAULT_HTML_VIZ_FILE_NAME = 'scattertext.html'
SEMIOTIC_SQUARE_HTML_PATH = 'data/viz/semiotic_new.html'
PAIR_PLOT_HTML_VIZ_FILE_NAME = 'pairplot.html'
PAIR_PLOT_WITHOUT_HALO_HTML_VIZ_FILE_NAME = 'pairplot_without_halo.html'

# Constants for background scaled f-score
DEFAULT_BACKGROUND_BETA = 1
DEFAULT_BACKGROUND_SCALER_ALGO = 'none'

# For sample corpus
POLITICAL_DATA_URL = 'https://gitcdn.xyz/repo/JasonKessler/scattertext/master/scattertext/data/political_data.json'
ROTTEN_TOMATOES_DATA_URL = 'https://gitcdn.xyz/repo/JasonKessler/scattertext/master/scattertext/data/rotten_tomatoes_corpus.csv.bz2'
ROTTEN_TOMATOES_DATA_FULL_URL = 'https://gitcdn.xyz/repo/JasonKessler/scattertext/master/scattertext/data/rotten_tomatoes_corpus_full.csv.bz2'

# General inquirer data
GENERAL_INQUIRER_URL = 'http://www.wjh.harvard.edu/~inquirer/inqtabs.txt'

# For sample corpus
DEFAULT_D3_URL = 'http://cdnjs.cloudflare.com/ajax/libs/d3/4.6.0/d3.min.js'
DEFAULT_D3_SCALE_CHROMATIC = 'http://d3js.org/d3-scale-chromatic.v1.min.js'
SPACY_ENTITY_TAGS = ['person', 'norp', 'facility', 'org', 'gpe',
                     'loc', 'product', 'event', 'work_of_art', 'language',
                     'type', 'date', 'time', 'percent', 'money', 'quantity',
                     'ordinal', 'cardinal']

# Adjust stopword set for spaCy tokenization
MY_ENGLISH_STOP_WORDS = set(ENGLISH_STOP_WORDS) | {'hasn', 'won', 'don', 'haven', 'shouldn', 'isn', 'couldn', 'wouldn',
                                                   'aren', 'didn', 'wasn', 'dosen', 'weren', 'doesn', 's', 't'}

# Qualitative Colors From Tableau

QUALITATIVE_COLORS = [[31, 119, 180], [174, 199, 232], [255, 127, 14], [255, 187, 120], [44, 160, 44], [152, 223, 138],
                      [214, 39, 40], [255, 152, 150], [148, 103, 189], [197, 176, 213], [140, 86, 75], [196, 156, 148],
                      [227, 119, 194], [247, 182, 210], [127, 127, 127], [199, 199, 199], [188, 189, 34],
                      [219, 219, 141], [23, 190, 207], [158, 218, 229],  # tableau 20
                      [177, 3, 24], [219, 161, 58], [48, 147, 67], [216, 37, 38], [255, 193, 86], [105, 183, 100],
                      [242, 108, 100], [255, 221, 113], [159, 205, 153]] # traffic light 9
