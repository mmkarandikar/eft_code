#!/usr/bin/env python3

#import libraries
# import h5py
import matplotlib.pyplot as plt
import numpy as np
import pickle
from matplotlib.markers import MarkerStyle
from functions import read_density, dc_in_finder, dn, smoothing
from tqdm import tqdm

def SPT(dc_in, L, a):
   """Returns the SPT PS upto 2-loop order"""
   Nx = dc_in.size
   F = dn(5, L, dc_in)
   d1k = (np.fft.fft(F[0]) / Nx)
   d2k = (np.fft.fft(F[1]) / Nx)
   d3k = (np.fft.fft(F[2]) / Nx)
   d4k = (np.fft.fft(F[3]) / Nx)
   d5k = (np.fft.fft(F[4]) / Nx)

   P11 = np.real((d1k * np.conj(d1k)) * (a**2))
   P12 = np.real(((d1k * np.conj(d2k)) + (d2k * np.conj(d1k)))  * (a**3))
   P22 = np.real((d2k * np.conj(d2k)) * (a**4))
   P13 = np.real(((d1k * np.conj(d3k)) + (d3k * np.conj(d1k))) * (a**4))
   P14 = np.real(((d1k * np.conj(d4k)) + (d4k * np.conj(d1k))) * (a**5))
   P23 = np.real(((d2k * np.conj(d3k)) + (d3k * np.conj(d2k))) * (a**5))
   P33 = np.real((d3k * np.conj(d3k)) * (a**6))
   P15 = np.real(((d1k * np.conj(d5k)) + (d5k * np.conj(d1k))) * (a**6))
   P24 = np.real(((d2k * np.conj(d4k)) + (d4k * np.conj(d2k))) * (a**6))
   return P11, P12, P22, P13, P14, P23, P33, P15, P24

path = 'cosmo_sim_1d/sim_k_1_11/run1/'
kind = 'sharp'
kind_txt = 'sharp cutoff'
# kind = 'gaussian'
# kind_txt = 'Gaussian smoothing'

Lambda_int = 3
Lambda = Lambda_int*(2*np.pi)
# m = 6


file = open(f"./{path}/alpha_c_{kind}_{Lambda_int}.p", "rb")
read_file = pickle.load(file)
a_list, alpha_c_true, alpha_c_F3P, alpha_c_F6P, alpha_c_MW, alpha_c_SC, alpha_c_SCD, _, _, _, alpha_c_pred = np.array(read_file)
file.close()

alpha_c_F3P /= ((2*np.pi)**2)


# j = 50
for j in tqdm(range(50, 51)):
   a = np.genfromtxt(path + 'aout_{0:04d}.txt'.format(j))
   x = np.arange(0, 1.0, 0.001)
   dc_in, k = dc_in_finder(path, x, interp=True)
   dc_in = smoothing(dc_in, k, Lambda, kind)

   P11, P12, P22, P13, _, _, _, _, _ = SPT(dc_in, 1.0, a)

   del_J_F3P, del_J_F6P, del_J_SC = [], [], []
   m = 18
   for mode in np.arange(1, m+1, 1):
       mode = int(mode)
       file = open(f"./{path}/stoch_del_{kind}_{Lambda_int}_{mode}.p", "rb")
       read_file = pickle.load(file)
       a_list, del_J_F3P_m, del_J_F6P_m, del_J_SC_m = np.array(read_file)
       del_J_F3P.append(del_J_F3P_m[j])
       del_J_F6P.append(del_J_F6P_m[j])
       del_J_SC.append(del_J_SC_m[j])
       file.close()

   P_JJ_F3P = np.log10(np.abs(k[:m]**2 * del_J_F3P[:m])**2)
   P_JJ_F6P = np.log10(np.abs(k[:m]**2 * del_J_F6P[:m])**2)
   P_JJ_SC = np.log10(np.abs(k[:m]**2 * del_J_SC[:m])**2)
   
   # P_ctr_1l = 2 * alpha_c_F3P[j] * k**2 * P11
   P_ctr_1l = alpha_c_SC[j] * k**2 * P11

   k /= (2*np.pi)

   plt.rcParams.update({"text.usetex": True})
   plt.rcParams.update({"font.family": "serif"})

   P13 = np.log10(np.abs(P13))
   P22 = np.log10(np.abs(P22))
   Pctr = np.log10(np.abs(P_ctr_1l))

   fig, ax = plt.subplots()
   ax.set_title(rf'$a={a},\,\Lambda = {Lambda_int} \,k_{{\mathrm{{f}}}}$ ({kind_txt})', fontsize=18)

   # # ax.scatter(k[:m], P13[:m], s=45, c='b', marker='o', label=r'$P_{13}$')
   # # ax.scatter(k[:m], Pctr[:m], s=40, c='k', marker='v', label=r'$k^{2}\alpha_{c}P_{11}$')
   # ax.scatter(k[:m], P22[:m], s=35, c='b', marker='*', label=r'$P_{22}$')
   # ax.scatter(k[:m], P_JJ_F3P[:m], s=30, c='k', marker='o', label=r'$P_{\mathrm{J}\mathrm{J}}$: F3P')
   # ax.scatter(k[:m], P_JJ_F6P[:m], s=30, c='seagreen', marker='^', label=r'$P_{\mathrm{J}\mathrm{J}}$: F6P')
   # ax.scatter(k[:m], P_JJ_SC[:m], s=30, facecolors='none', edgecolor='r', marker=MarkerStyle('o', fillstyle='none'), label=r'$P_{\mathrm{J}\mathrm{J}}$: SC')

   # ax.plot(k[:m], P22[:m], lw=1.5, c='b', marker='*', label=r'$P_{22}$')

   # for l in range(m):
   ax.vlines(x=k[:m], ymin=-25, ymax=P22[:m], lw=1.5, colors='b')
   #, marker='*')
   ax.scatter(k[:m], P22[:m], s=25, c='b', marker='*', label=r'$P_{22}$')

   ax.plot(k[:m], P_JJ_F3P[:m], lw=1.5, c='k', marker='o', label=r'$P_{\mathrm{J}\mathrm{J}}$: F3P')
   # ax.plot(k[:m], P_JJ_F6P[:m], lw=1.5, c='seagreen', marker='^', label=r'$P_{\mathrm{J}\mathrm{J}}$: F6P')
   ax.plot(k[:m], P_JJ_SC[:m], lw=1.5, c='r', marker=MarkerStyle('o', fillstyle='none'), label=r'$P_{\mathrm{J}\mathrm{J}}$: SC')

   ax.set_ylabel(r'$\log_{10}P(k)$', fontsize=20)
   # ax.set_xlabel(r'$k\,[k_{\mathrm{f}}]$', fontsize=20)
   ax.set_xlabel(r'$k/k_{\mathrm{f}}$', fontsize=20)

   ax.tick_params(axis='both', which='both', direction='in', labelsize=15)
   ax.yaxis.set_ticks_position('both')
   ax.minorticks_on()
   ax.legend(fontsize=14, framealpha=1)#, loc='lower left')#, loc=2, bbox_to_anchor=(1,1))

   ax.set_ylim(-20, 2)
   ax.set_xlim(0.5, 16.5)
   # ax[0].set_xlim(-0.5, 11.5)
   # plt.savefig('../plots/paper_plots_final/PS_SPT/PS_SC_{0:03d}.png'.format(j), bbox_inches='tight', dpi=300)
   plt.tight_layout()
   plt.savefig(rf'../plots/paper_plots_final/PS_stoch_{kind}.pdf', bbox_inches='tight', dpi=300)
   plt.close()
   # plt.show()


   # plt.rcParams.update({"text.usetex": True})
   # plt.rcParams.update({"font.family": "serif"})
   # # ax.scatter(k[1:m], P_JJ_F3P, s=50, c='b', marker='o', label=r'F3P')
   # # ax.scatter(k[1:m], P_JJ_F6P, s=30, c='k', marker='*', label='F6P')
   # # ax.scatter(k[1:m], P_JJ_SC, s=20, c='r', marker='v', label='SC')

   # P13 = np.log10(np.abs(P13))
   # P22 = np.log10(np.abs(P22))
   # Pctr = np.log10(np.abs(P_ctr_1l))

   # fig, ax = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(12, 6))
   # fig.suptitle(rf'$a={a},\,\Lambda = {Lambda_int} \,k_{{\mathrm{{f}}}}$ ({kind_txt})', fontsize=18, y=0.975)

   # ax[0].scatter(k[:m], P13[:m], s=45, c='b', marker='o', label=r'$P_{13}$')
   # ax[0].scatter(k[:m], Pctr[:m], s=40, c='k', marker='v', label=r'$k^{2}\alpha_{c}P_{11}$')
   # ax[1].scatter(k[:m], P22[:m], s=35, c='b', marker='*', label=r'$P_{22}$')
   # ax[1].scatter(k[:m], P_JJ_SC[:m], s=30, c='k', marker='x', label=r'$P_{\mathrm{J}\mathrm{J}}$; SC')
   # for i in range(2):
   #    ax[i].set_ylabel(r'$\log_{10}P(k)$', fontsize=20)
   #    ax[i].set_xlabel(r'$k\,[k_{\mathrm{f}}]$', fontsize=20)
   #    ax[i].tick_params(axis='both', which='both', direction='in', labelsize=15)
   #    ax[i].yaxis.set_ticks_position('both')
   #    ax[i].minorticks_on()
   #    ax[i].legend(fontsize=14)#, loc='lower left')#, loc=2, bbox_to_anchor=(1,1))


   # #  ax.tick_params(axis='x', which='minor', bottom=False, top=False)
   # ax[0].set_ylim(-25, 2)
   # # ax[0].set_xlim(-0.5, 11.5)
   # ax[1].yaxis.set_label_position('right')
   # plt.subplots_adjust(wspace=0)
   # # plt.savefig('../plots/paper_plots_final/PS_SPT/PS_SC_{0:03d}.png'.format(j), bbox_inches='tight', dpi=300)
   # # plt.savefig('../plots/paper_plots_final/PS_{0:03d}.png'.format(j), bbox_inches='tight', dpi=300)
   # # plt.close()
   # plt.show()
