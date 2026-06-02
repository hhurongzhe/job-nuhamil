#!/usr/bin/env python3
import sys, os, itertools

HOME = os.path.expanduser("~")
sys.path.append(HOME)
import readline
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lib.ini_plot import *

# from mylib_python import myplt


def main():
    fs = 6
    Lstring = ["S", "P", "D", "F", "G"]
    ini_plot()
    fig, axs = plt.subplots(2, 3, figsize=(5, 4), sharex=True, sharey=False)
    df = pd.read_csv("phase-shift-analysis/Nijmegen.csv", sep="\s*,\s*", engine="python")
    NNlist = ["N3LO_EM500"]
    for J in range(3):
        for S, P in itertools.product(range(2), [1, -1]):
            if S == 1:
                axs[S, J].set_xlabel(r"$T_{\rm lab}$ (MeV)", fontsize=fs + 2)
            if J == 0:
                axs[S, J].set_ylabel(r"$\delta$", fontsize=fs + 2)
            ax = axs[S, J]
            ax.minorticks_on()
            ax.tick_params(direction="in", width=0.5, length=3, top=True, bottom=True, left=True, right=True, axis="both", labelsize=fs)
            ax.tick_params(which="minor", direction="in", width=0.3, length=2, top=True, bottom=True, left=True, right=True, axis="both")
            for spine in ax.spines.values():
                spine.set_linewidth(0.5)
            axs[S, J].set_title(r"$^{" + f"{2*S+1}" + "}$" + Lstring[J] + r"$_{" + str(J) + "}$", fontsize=fs + 2)
            partial_wave = f"{2*S+1}{Lstring[J]}{J}"
            pn = "pn"
            if J == 0 and P == -1 and S == 1:
                axs[S, J].set_title(r"$^{3}$P$_{0}$", fontsize=fs + 2)
                partial_wave = "3P0"
            Z = 0
            for idx, NN in enumerate(NNlist):
                filename = f"phase_shift_{NN}_bare_uncoupled.txt"
                data = np.loadtxt(filename, comments="#", skiprows=1)
                t, delta = [], []
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
                    delta.append(data[i, 6] * 180 / np.pi)
                if len(t) == 0:
                    continue
                axs[S, J].plot(t, delta, lw=0.8, label=NN)
            _ = df[(df["partial wave"] == partial_wave) & (df["pn"] == pn)]
            if not _.empty:
                axs[S, J].errorbar(_["Tlab"], _["delta"], yerr=_["error"], ls="", marker="o", ms=2, mfc="none", c="k", capsize=2)

    axs[0, 0].legend(fontsize=fs, loc="upper right", frameon=False)
    fig.tight_layout()
    plt.show()
    # plt.savefig("uncoupled.pdf")


if __name__ == "__main__":
    main()
