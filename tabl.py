from spire.xls import *
from spire.xls.common import *
import pandas as pd
import seaborn as sns


def kanban_tabl():
    pd.set_option('max_rows', 5)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.float_format', '{:.2f}'.format)

