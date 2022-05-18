"""
Author: Gabriel Cenciati
LinkedIn: https://www.linkedin.com/in/cenciati/
GitHub: https://github.com/cenciati/
"""

# data manipulation
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

# data visualization
from matplotlib import pyplot as plt
import seaborn as sns

# machine learning
from sklearn import model_selection as ms
from sklearn import metrics as m

# other
import warnings

class MyToolBox(object):
    def __init__(self):
        pass
    
    
    def jupyter_settings(self, figsize=(24, 12), fontsize=12, filterwarnings=False):
        """Set jupyter settings.

        Parameters
        ----------
        figsize : tuple, default=(24, 12)
            Indicates the size of the plots.
        fontsize : int, default=12
            Indicates the font size of all plots labels.
        filterwarnings : boolean, default=False
            Defines whether warnings will be displayed during the project.
        
        Returns
        -------
        None
        """
        # settings
        ## pandas settings
        pd.options.display.max_columns = None
        pd.options.display.max_rows = 20
        pd.options.display.float_format = '{:.3f}'.format
        
        ## numpy settings
        np.random.seed(42)
        np.set_printoptions(precision=3)
        
        ## visualization settings
        plt.rc('figure', figsize=figsize)
        plt.rc('font', size=fontsize)
        
        ## warnings settings
        if filterwarnings:
            warnings.filterwarnings('ignore')
        
        # work message
        print('Done!')

        return None
    
    
    def cramers_v(self, x, y):
        """Calculates the Cramer's V correlation between two variables.

        Parameters
        ----------
        x : pandas series
            First variable.
        y : pandas series
            Second variable.
        
        Returns
        -------
        Cramer's V correlation
        """
        # confusion matrix
        cm = pd.crosstab(x,y).to_numpy()
        
        # formula
        n = cm.sum()
        r, k = cm.shape
        chi2 = chi2_contingency(cm)[0]
        
        # bias correction
        chi2corr = max(0, chi2 - (k-1)*(r-1) / (n-1))
        kcorr = k - (k-1)**2 / (n-1)
        rcorr = r - (r-1)**2 / (n-1)
        
        return np.sqrt((chi2corr / n) / (min(kcorr-1, rcorr-1)))
