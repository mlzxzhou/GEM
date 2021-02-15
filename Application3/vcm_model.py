import numpy as np
import pandas as pd
import statsmodels.api as sm      


def compute_Amat(D, Vi):
    index = D.index.get_level_values(1)
    return np.dot(D.T.values * Vi[index].values, D.values)


def compute_bvec(D, Vi, y):
    index = D.index.get_level_values(1)
    return np.dot(D.T.values * Vi[index].values, y.values)


def compute_Cmat(D, Vi, W):
    index = D.index.get_level_values(1)
    Vi_, W_ = Vi.loc[index], W.loc[index, index]
    left = (D.T.values * Vi_.values)
    return np.dot(np.dot(left, W_.values), left.T)


class VCM(object):
    def __init__(self, df, ycol, xcols, acol, 
                 interaction=False, two_sided=True, wild_bootstrap=False, copy=True,
                 center_x=True, scale_x=True, center_y=False, scale_y=False, # not used this time
                 keep_ratio=0.95, he=0.05, smooth_coef=False, hc=0.05): # extra args for future model update
        '''
        y_i(t) = alpha(t) + (x_i(t)-x_bar(t))^T beta(t) + a_i(t)[alpha'(t) + (x_i(t)-x_bar(t))^T beta'(t)]
                 + eta_i(t) + varepsilon_i(t) if interaction = True
               = alpha(t) + (x_i(t)-x_bar(t))^T beta(t) + a_i(t)gamma(t)
                 + eta_i(t) + varepsilon_i(t) if interaction = False
        
        df: pandas DataFrame, multiindex: ('date','time'), 
                              columns: [ycol='gmv', xcols=['demand','supply'], acol='A']
                              
        ycol: str, column name for response of interest
        xcols: list, can be None or [], column names for covariates
        acol: str, column name for treatment indicator
        
        interaction: boolean, whether to include treatment and covariates interactions
        two_sided:   boolean, one sided or two sided test
        wild_bootstrap: boolean, wild_bootstrap based statistical inference
        copy:        whether to copy df, df will be modified
        
        keep_ratio:  functional PCA of cov_eta, keep ratio
        he:          smoothing bandwidth of eta_i(t), relative to 1
        smooth_coef: boolean, whether to smooth varying coeffs
        hc:          smoothing bandwidth of varying coeffs, relative to 1
        '''
        self.df = df.copy() if copy else df
        self.df.sort_index(inplace=True, level=[0,1])
        self.df['const'] = 1
        
        if xcols is None: xcols = []
        
        # check inputs
        ### deal with NANs
        for col in xcols + [acol, ycol]:
            nan_dates = self.df[col].isnull().groupby('date').sum()
            if (nan_dates > 0.001).any():
                idices = nan_dates[nan_dates > 0.001].index.tolist()
                raise ValueError('{} has NANs on dates: {}'.format(col, idices))
                
        ### filter out rows with all zeros
        if len(xcols) > 0:
            times = (self.df.groupby('time')[xcols].sum().abs() > 1e-6).all(axis=1)
            times = times[times.values].index
            self.df = self.df.loc[(slice(None),times),:]
        
        # dates
        self.dates = self.df.index.get_level_values(0).unique()
        # times
        self.times = self.df.index.get_level_values(1).unique()
        # number of days
        self.N = len(self.dates)
        # number of obs for each day
        self.Ms = self.df[acol].groupby('date').count()
        # maximum number of obs for a given day
        self.M = self.Ms.max()
        # total number of obs
        self.NM = self.df.shape[0]
        # num of features
        self.px = len(xcols)
        
        ### check sample size
        if self.N < self.px + 3:
            raise ValueError('Number of days {} < number of features {} + 3,'.format(self.N, self.px) + \
                             'VCM fails to conduct statistical inference!')
        
        # Agnostic notes on Regression Adjustments to Experimental Data: Reexamining Freedman's Critique
        if len(xcols) != 0:
            self.mx = self.df[xcols].groupby('time').mean()
            self.df[xcols] -= self.mx
            self.sx = self.df[xcols].groupby('time').std() + 1e-6 # avoid zero division
            self.df[xcols] /= self.sx
        self.sy = self.df[ycol].std() + 1e-6 # avoid zero division
        self.df[ycol] /= self.sy
        
        # regression column names
        axcols = []
        if interaction and len(xcols) > 0:
            mapper = {col: acol+'_'+col for col in xcols}
            for col in xcols:
                self.df[mapper[col]] = self.df[acol] * self.df[col]
            axcols = list(mapper.values())
        self.regcols1 = ['const'] + xcols + [acol] + axcols
        self.regcols0 = ['const'] + xcols + axcols
        
        # extend feature columns, TODO: make it more efficient
        self.regcols1_ = [col + str(time) for time in self.times for col in self.regcols1]
        self.regcols0_ = [col + str(time) for time in self.times for col in self.regcols0]
        self.df_ = pd.DataFrame(0, index=self.df.index, columns=self.regcols1_)
        for time in self.times:
            regcols1_time = [col+str(time) for col in self.regcols1]
            self.df_.loc[(slice(None),time), regcols1_time] = self.df.loc[(slice(None),time), self.regcols1].values
        self.df_[ycol] = self.df[ycol].values
    
        # main args
        self.ycol = ycol
        self.xcols = xcols
        self.acol = acol
        self.axcols = axcols
        self.interaction = interaction
        self.two_sided = two_sided
        self.wild_bootstrap = wild_bootstrap
        self.copy = copy
        # not used args
        self.keep_ratio = keep_ratio
        self.he = he
        self.smooth_coef = smooth_coef
        self.hc = hc
        # number of regressors
        self.pr = len(self.regcols1)
        # estimation done under H0 or H1
        self.null, self.alternative = False, False 
        # result holder
        self.holder = {} 
        
    def estimate(self, ycol=None, null=False, suffix='', max_iter=20, eps=1e-3):
        if null: suffix = '0'
        if ycol is None: ycol = self.ycol
        xcols, acol = self.xcols, self.acol
        interaction, axcols = self.interaction, self.axcols
        # extended data frame
        df_ = self.df_
        # extended columns
        regcols_ = self.regcols0_ if null else self.regcols1_ 
        regcols  = self.regcols0  if null else self.regcols1
        # number of covariates (intercept not included) and 
        # number of regressors (intercept included)
        px, pr = self.px, self.pr
        N, M, K = self.N, self.M, len(regcols)
        # time points
        times = self.times
        holder = self.holder
        
        # estimate theta
        Amat = df_.groupby('date').apply(lambda dt: np.dot(dt[regcols_].T, dt[regcols_])).sum()
        bvec = df_.groupby('date').apply(lambda dt: np.dot(dt[regcols_].T, dt[ycol])).sum()
        # avoid degenerate covariance matrix
        eps_diag = np.eye(Amat.shape[0])*1e-3
        theta_hat = np.linalg.solve(Amat+eps_diag, bvec)
        for idx in range(max_iter):
            resid_hat = df_[ycol] - df_[regcols_].dot(theta_hat)
            V = resid_hat.unstack().var(axis=0) + 1e-3 # pandas series
            Vi = 1.0/V

            Amat = df_.groupby('date').apply(lambda dt: compute_Amat(dt[regcols_], Vi)).sum()
            bvec = df_.groupby('date').apply(lambda dt: compute_bvec(dt[regcols_], Vi, dt[ycol])).sum()
            
            theta_hat_ = np.linalg.solve(Amat+eps_diag, bvec) # possible place of exceptions
            if np.abs(theta_hat-theta_hat_).sum()/np.abs(theta_hat).sum() < eps:
                break
            theta_hat = theta_hat_
        if idx == max_iter-1:
            print('warning: max iteration reached!')
            
        df_['fittedvalues'+suffix] = df_[regcols_].dot(theta_hat)
        df_['resid'+suffix] = df_[ycol] - df_['fittedvalues'+suffix]
        
        if not null: # compute standard error
            W = df_['resid'+suffix].unstack().fillna(0).groupby('date').apply(lambda dt: np.outer(dt, dt)).sum()/(N-pr)
            W = pd.DataFrame(W, index=times, columns=times)
            
            Ai = np.linalg.pinv(Amat+eps_diag)
            Cmat = df_.groupby('date').apply(lambda dt: compute_Cmat(dt[regcols_], Vi, W)).sum()
            theta_cov_hat = np.dot(np.dot(Ai, Cmat), Ai)
            
            idx = px + 1 + pr * np.arange(M)
            gamma_hat = theta_hat[idx]
            gamma_cov_hat = theta_cov_hat[idx,:][:,idx]
            
            gamma = gamma_hat.sum()
            gamma_se = gamma_cov_hat.sum()**0.5 + 1e-6
            test_stats = gamma / gamma_se
            holder['gamma'+suffix] = gamma * self.sy
            holder['gamma_se'+suffix] = gamma_se * self.sy
            holder['test_stats'+suffix] = test_stats
            
        theta_hat = pd.DataFrame(theta_hat.reshape((M, K)), columns=regcols)
        if len(xcols) > 0:
            theta_hat[xcols] /= self.sx.values
            theta_hat['const'] -= (theta_hat[xcols]*self.mx.values).sum(axis=1)
            if interaction:
                theta_hat[axcols] /= self.sx.values
                theta_hat['const'] -= (theta_hat[axcols]*self.mx.values).sum(axis=1)
        theta_hat *= self.sy
        
        holder['thetas'+suffix] = theta_hat
        holder[ycol] = df_[ycol] * self.sy
        holder[ycol+'_hat'+suffix] = df_['fittedvalues'+suffix] * self.sy
        holder['resid'+suffix] = df_['resid'+suffix] * self.sy
        
        if null:
            self.null = True
        else:
            self.alternative = True
        
    def inference(self, nb=100, max_iter=20, eps=1e-3):
        # solve under alternative
        if not self.alternative:
            self.estimate(null=False)
        
        holder = self.holder
        df_ = self.df_
        N, M, Ms, NM = self.N, self.M, self.Ms, self.NM
        two_sided = self.two_sided
        wild_bootstrap = self.wild_bootstrap
        test_stats = holder['test_stats']
        
        if wild_bootstrap:
            # solve under null
            if not self.null:
                self.estimate(null=True)
            fittedvalues0 = df_['fittedvalues0']
            resid0 = df_['resid0']
            
            test_stats_wb = np.zeros(nb)
            for idx in range(nb):
                # generate data via params learned under null
                df_['Yb'] = fittedvalues0 + np.repeat(np.random.randn(N), Ms) * resid0
                # estimate under alternative
                self.estimate(ycol='Yb', null=False, suffix='_b', max_iter=max_iter, eps=eps)
                test_stats_wb[idx] = holder['test_stats_b']

            pvalue1 = (test_stats_wb > test_stats).mean()
            pvalue2 = min(1.0, 2.0 * (test_stats_wb > abs(test_stats)).mean())
            holder['test_stats_wb'] = test_stats_wb
        else:
            from scipy.stats import norm
            pvalue1 = 1 - norm.cdf(test_stats)
            pvalue2 = 2 - 2 * norm.cdf(abs(test_stats))

        pvalue = pvalue2 if two_sided else pvalue1
        holder['test_stats'] = test_stats
        holder['pvalue'] = pvalue
        holder['pvalue1'] = pvalue1
        holder['pvalue2'] = pvalue2