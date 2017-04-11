from __future__ import division
import  matplotlib.pyplot as plt
import pandas as pd
from random import randint
import numpy as np
import os
from scipy import stats
import sys
from random import shuffle
from math import isnan
from scipy.stats.kde import gaussian_kde
from numpy import empty

mydir = os.path.expanduser("~/GitHub/residence-time")
tools = os.path.expanduser(mydir + "/tools")

sys.path.append(tools + "/DiversityTools/macroecotools")
import macroecotools as mct
sys.path.append(tools + "/DiversityTools/macroeco_distributions")
from macroeco_distributions import pln, pln_solver
sys.path.append(tools + "/DiversityTools/mete")
import mete


def get_kdens_choose_kernel(_list,kernel):
    """ Finds the kernel density function across a sample of SADs """
    density = gaussian_kde(_list)
    n = len(_list)
    xs = np.linspace(min(_list),max(_list),n)
    #xs = np.linspace(0.0,1.0,n)
    density.covariance_factor = lambda : kernel
    density._compute_covariance()
    D = [xs,density(xs)]
    return D



def get_rad_pln(S, mu, sigma, lower_trunc = True):
    """Obtain the predicted RAD from a Poisson lognormal distribution"""
    abundance = list(empty([S]))
    rank = range(1, int(S) + 1)
    cdf_obs = [(rank[i]-0.5) / S for i in range(0, int(S))]
    j = 0
    cdf_cum = 0
    i = 1
    while j < S:
        cdf_cum += pln.pmf(i, mu, sigma, lower_trunc)
        while cdf_cum >= cdf_obs[j]:
            abundance[j] = i
            j += 1
            if j == S:
                abundance.reverse()
                return abundance
        i += 1



def get_rad_from_obs(ab, dist):
    mu, sigma = pln_solver(ab)
    pred_rad = get_rad_pln(len(ab), mu, sigma)
    return pred_rad



p = 1
fr = 0.2
_lw = 0.5
w = 1
sz = 5

df = pd.read_csv(mydir + '/results/simulated_data/SimData.csv')

df2 = pd.DataFrame({'width' : df['width'].groupby(df['ct']).mean()})
df2 = df2.replace([0], np.nan).dropna()

df2['sim'] = df['sim'].groupby(df['ct']).mean()
df2['flow'] = df['flow.rate'].groupby(df['ct']).mean()

df2['tau'] = np.log10(df2['width']**p/df2['flow'])

df2['N'] = np.log10(df['total.abundance'].groupby(df['ct']).mean())
df2['NS'] = np.log10(df['avg.pop.size'].groupby(df['ct']).mean())
df2['var'] = np.log10(df['pop.var'].groupby(df['ct']).mean())

state = 'all'
df2['G'] = df[state+'.avg.per.capita.growth'].groupby(df['ct']).mean()
df2['M'] = df[state+'.avg.per.capita.maint'].groupby(df['ct']).median()
df2['D'] = df[state+'.avg.per.capita.active.dispersal'].groupby(df['ct']).mean()
df2['E'] = df[state+'.avg.per.capita.efficiency'].groupby(df['ct']).mean()
df2['size'] = np.log10(df[state+'.size'].groupby(df['ct']).median())

df2['B'] = np.log10(df2['M'])
df2 = df2.replace([np.inf, -np.inf], np.nan).dropna()

#df2 = df2[df2['size'] > -10]
#### plot figure ###############################################################
fs = 8 # fontsize
fig = plt.figure()

#### N vs. Tau #################################################################
Blist = df2['B'].tolist()
Mlist = df2['size'].tolist()

fig.add_subplot(2, 2, 1)
plt.scatter(Mlist, Blist, lw=_lw, color='0.2', s = sz)
m, b, r, p, std_err = stats.linregress(Mlist, Blist)
print 'MTE:', m
Mlist = np.array(Mlist)
plt.plot(Mlist, m*Mlist + b, '-', color='k')
xlab = r"$log_{10}$"+'(body size)'
ylab = r"$log_{10}$"+'(basal metabolic rate)'
plt.xlabel(xlab, fontsize=fs+3)
plt.tick_params(axis='both', labelsize=fs)
plt.ylabel(ylab, fontsize=fs+3)
plt.text(1.2, -2.7, 'slope = '+str(round(m,2)), fontsize=fs+2)
plt.ylim(-3, -1)
plt.xlim(0, 2)



df2 = df2[df2['NS'] > 0.4]
Nlist = df2['NS'].tolist()
Vlist = df2['var'].tolist()

fig.add_subplot(2, 2, 2)
plt.scatter(Nlist, Vlist, lw=_lw, color='0.2', s = sz)
m, b, r, p, std_err = stats.linregress(Nlist, Vlist)
print 'Taylors Law:', m
Nlist = np.array(Nlist)
plt.plot(Nlist, m*Nlist + b, '-', color='k')
xlab = r"$log_{10}$"+'(mean)'
ylab = r"$log_{10}$"+'(variance)'
plt.xlabel(xlab, fontsize=fs+3)
plt.tick_params(axis='both', labelsize=fs)
plt.ylabel(ylab, fontsize=fs+3)
plt.text(0.7, 5, 'slope = '+str(round(m,2)), fontsize=fs+2)
#plt.ylim(0, 6)
#plt.xlim(0.5, 2.5)




data = mydir + '/results/simulated_data/SAR-Data.csv'

SARs = []

with open(data) as f:
    for d in f:
        d = list(eval(d))
        sim = d.pop(0)
        ct = d.pop(0)
        if max(d) <= 1: continue
        SARs.append(d)

print 'Number of SARs:', len(SARs)


z_vals = []
shuffle(SARs)
for sar in SARs:
    area_vector = (2**np.array(range(0, len(sar)))).tolist()
    m, b, r, p, std_err = stats.linregress(np.log10(area_vector), np.log10(sar))
    
    if isnan(m): continue
    z_vals.append(m)
    if len(z_vals) > 1000: break

fig.add_subplot(2, 2, 3)
kernel = 0.2

D = get_kdens_choose_kernel(z_vals, kernel)
plt.plot(D[0],D[1],color = '0.5', lw=3, alpha = 0.99, label= 'SAR')
#plt.xlim(0.0, 1)
plt.legend(loc=1, fontsize=fs+1)
plt.xlabel('$z$', fontsize=fs+3)
plt.ylabel('$density$', fontsize=fs+3)
plt.tick_params(axis='both', labelsize=fs)


'''
data = mydir + '/results/simulated_data/RAD-Data.csv'

RADs = []
with open(data) as f:
    for d in f:
        d = list(eval(d))

        sim = d.pop(0)
        ct = d.pop(0)

        d = sorted(d, reverse=True)
        RADs.append(d)

print 'Number of RADs:', len(RADs)

mete_r2s = []
pln_r2s = []

shuffle(RADs)
for i, obs in enumerate(RADs):

    N = int(sum(obs))
    S = int(len(obs))

    if S > 4 and N > 10 and obs.count(1)/len(obs) < 0.5:

        result = mete.get_mete_rad(S, N)
        pred1 = np.log10(result[0])
        obs1 = np.log10(obs)
        mete_r2 = mct.obs_pred_rsquare(np.array(obs1), np.array(pred1))
        mete_r2s.append(mete_r2)

        pred = get_rad_from_obs(obs, 'pln')
        pred1 = np.log10(pred)
        pln_r2 = mct.obs_pred_rsquare(np.array(obs1), np.array(pred1))
        pln_r2s.append(pln_r2)

        print i, 'N:', N, ' S:', S, ' n:', len(pln_r2s), ' |  mete:', mete_r2, '  pln:', pln_r2

    if len(pln_r2s) > 100: break


fig.add_subplot(2, 2, 4)
kernel = 0.5

D = get_kdens_choose_kernel(mete_r2s, kernel)
plt.plot(D[0],D[1],color = '0.5', lw=3, alpha = 0.99,label= 'METE')

D = get_kdens_choose_kernel(pln_r2s, kernel)
plt.plot(D[0],D[1],color = '0.1', lw=3, alpha = 0.99, label= 'PLN')

plt.xlim(0.0, 1)
plt.legend(loc=2, fontsize=fs+1)
plt.xlabel('$r$'+r'$^{2}$', fontsize=fs+3)
plt.ylabel('$density$', fontsize=fs+3)
'''
#### Final Format and Save #####################################################
plt.subplots_adjust(wspace=0.4, hspace=0.4)
plt.savefig(mydir + '/results/figures/MacroEcoPatterns.png', dpi=200, bbox_inches = "tight")
plt.close()
#sys.exit()
