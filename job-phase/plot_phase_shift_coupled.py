#!/usr/bin/env python3
import sys, os

HOME = os.path.expanduser("~")
sys.path.append(HOME)
import readline
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lib.ini_plot import *


def main():
    fs = 6
    Lstring = ["S", "P", "D", "F", "G", "H"]
    ini_plot()
    fig, axs = plt.subplots(3, 2, figsize=(3, 4), sharex=True, sharey=False)
    df = pd.read_csv("phase-shift-analysis/Nijmegen.csv", sep="\s*,\s*", engine="python")
    NNlist = ["N3LO_EM500"]
    S = 1
    for J in range(1, 3):
        axs[2, J - 1].set_xlabel(r"$T_{\rm lab}$ (MeV)", fontsize=fs + 2)
        if J == 1:
            axs[0, J - 1].set_ylabel(r"$\delta_{--}$", fontsize=fs + 2)
            axs[1, J - 1].set_ylabel(r"$\delta_{++}$", fontsize=fs + 2)
            axs[2, J - 1].set_ylabel(r"$\epsilon$", fontsize=fs + 2)
        axs[0, J - 1].set_title(r"$^{3}$" + Lstring[J - 1] + r"$_{" + str(J) + "}$", fontsize=fs + 2)
        axs[1, J - 1].set_title(r"$^{3}$" + Lstring[J + 1] + r"$_{" + str(J) + "}$", fontsize=fs + 2)
        axs[2, J - 1].set_title(r"$^{3}$" + Lstring[J - 1] + r"$_{" + str(J) + "}$-" + r"$^{3}$" + Lstring[J + 1] + r"$_{" + str(J) + "}$", fontsize=fs + 2)
        for ax in axs[:, J - 1]:
            ax.minorticks_on()
            ax.tick_params(direction="in", width=0.5, length=3, top=True, bottom=True, left=True, right=True, axis="both", labelsize=fs)
            ax.tick_params(which="minor", direction="in", width=0.3, length=2, top=True, bottom=True, left=True, right=True, axis="both")
            for spine in ax.spines.values():
                spine.set_linewidth(0.5)
        pn = "pn"
        partial_wave_mm = f"3{Lstring[J-1]}{J}"
        partial_wave_pp = f"3{Lstring[J+1]}{J}"
        partial_wave_mp = f"3{Lstring[J-1]}{J}-3{Lstring[J+1]}{J}"
        P = (-1) ** (J - 1)
        Z = 0
        for idx, NN in enumerate(NNlist):
            filename = f"phase_shift_{NN}_bare_coupled.txt"
            data = np.loadtxt(filename, comments="#", skiprows=1)
            t, delta_m, delta_p, eps = [], [], [], []
            for i in range(len(data[:, 0])):
                if data[i, 0] != J:
                    continue
                if data[i, 1] != S:
                    continue
                if data[i, 2] != P:
                    continue
                if data[i, 3] != Z:
                    continue
                t.append(data[i, 5])
                if partial_wave_mm == "3S1" and (data[i, 6] < 0 and data[i, 5] < 100):
                    delta_m.append(180 + data[i, 6] * 180 / np.pi)
                    eps.append(-data[i, 8] * 180 / np.pi)
                else:
                    delta_m.append(data[i, 6] * 180 / np.pi)
                    eps.append(data[i, 8] * 180 / np.pi)
                delta_p.append(data[i, 7] * 180 / np.pi)
            if len(t) == 0:
                continue
            axs[0, J - 1].plot(t, delta_m, lw=0.8, label=NN)
            axs[1, J - 1].plot(t, delta_p, lw=0.8, label=NN)
            axs[2, J - 1].plot(t, eps, lw=0.8, label=NN)
        _mm = df[(df["partial wave"] == partial_wave_mm) & (df["pn"] == pn)]
        _pp = df[(df["partial wave"] == partial_wave_pp) & (df["pn"] == pn)]
        _mp = df[(df["partial wave"] == partial_wave_mp) & (df["pn"] == pn)]
        if not _mm.empty:
            axs[0, J - 1].errorbar(_mm["Tlab"], _mm["delta"], yerr=_mm["error"], ls="", marker="o", ms=2, mfc="none", c="k", capsize=2)
        if not _pp.empty:
            axs[1, J - 1].errorbar(_pp["Tlab"], _pp["delta"], yerr=_pp["error"], ls="", marker="o", ms=2, mfc="none", c="k", capsize=2)
        if not _mp.empty:
            axs[2, J - 1].errorbar(_mp["Tlab"], _mp["delta"], yerr=_mp["error"], ls="", marker="o", ms=2, mfc="none", c="k", capsize=2)

    axs[0, 0].legend(fontsize=fs, loc="upper right", frameon=False)
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
