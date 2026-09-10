import os
import sys
import subprocess
from collections import OrderedDict
import time

HOME = "/Users/mac/Desktop/job-nuhamil"
path_to_nninput = f"{HOME}/input_nn_files"
exe_file = f"{HOME}/NuHamil.exe"
n_omp_threads = 32

batch = "terminal"
# batch = "slurm"

partition = "c128m512"
# partition = "c128m1024"

if batch == "terminal":
    header = ""
elif batch == "slurm":
    header = "#!/bin/bash\n"
    header += f"#SBATCH --partition {partition}\n"
    header += "#SBATCH -J 2bme\n"
    header += "#SBATCH --nodes=1\n"
    header += "#SBATCH --ntasks-per-node=1\n"
    header += "#SBATCH --cpus-per-task=" + str(n_omp_threads) + "\n"
    header += "#SBATCH --output=./result/slurm-%j.out\n"
    header += "source sourceme.sh\n"

NNF = "N3LO_EM500"
# ext_2bme = ".MFDn"
ext_2bme = ".me2j.bin"

hw_list = [16, 20]
emax_list = [6, 12, 14]
# hw_list = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]
# emax_list = [2, 4, 6, 8, 10, 12, 14, 16]


def set_input(params, hw=20, emax=14, e2max=28):
    params["rank"] = 2
    params["hw"] = hw
    # params["Operators"] = "kinetic"
    # params["Operators"] = "Hcm"
    # params["Operators"] = f"HOHamil{hw}"
    params["renorm"] = "bare"
    params["lambda"] = 1.8
    params["emax"] = emax
    params["e2max"] = e2max
    params["NNInt"] = NNF
    params["input_nn_file"] = f"{path_to_nninput}/{params['NNInt']}_kmax8_N100_Jmax8.bin"
    # params["input_nn_file"] = f"{path_to_nninput}/{params['NNInt']}_kmax20_N200_Jmax8.bin"
    # params["nmesh2"] = 200
    # params["pmax2"] = 20.0
    params["path_to_tmp_dir"] = f"{HOME}/workspace"
    set_file_name_nn(params)


def get_script_name(params):
    fbase = "vHamil_MECalc_A" + str(params["rank"]) + "_hw" + str(params["hw"])
    ms = ""
    fbase += ms
    fbase = "vHamil_MECalc_A2_" + params["file_name_nn"].split(ext_2bme)[0]
    return fbase


def gen_script(params, batch):
    exe = exe_file
    if batch == "slurm":
        exe = "srun " + exe_file
    fbase = get_script_name(params)
    file_input = "./result/Input_" + fbase + ".dat"
    file_log = "./result/log_" + fbase + ".dat"
    fsh = "./script/run_" + fbase + ".sh"
    prt = header

    prt += 'echo "start ' + fsh + '..."\n'
    prt += "cat > " + file_input + " <<EOF\n"
    prt += "&input\n"
    for key, value in params.items():
        if isinstance(value, str):
            prt += "  " + str(key) + '= "' + str(value) + '" \n'
            continue
        if isinstance(value, list):
            prt += "  " + str(key) + "= "
            for x in value[:-1]:
                prt += str(x) + ", "
            prt += str(value[-1]) + "\n"
            continue
        prt += "  " + str(key) + "=" + str(value) + "\n"
    prt += "&end\n"
    prt += "EOF\n"
    if batch == "terminal":
        prt += exe + " " + file_input + "\n"
        prt += "rm " + file_input + "\n"
    else:
        prt += exe + " " + file_input + " > " + file_log + " 2>&1\n"
        prt += "rm " + file_input + "\n"
    f = open(fsh, "w")
    f.write(prt)
    f.close()
    os.chmod(fsh, 0o755)
    return fsh


def set_file_name_nn(params):
    try:
        f = "TwBME_"
        if "Operators" in params:
            f += params["Operators"] + "_"
        else:
            f += params["NNInt"] + "_"
        f += params["renorm"]
        if params["renorm"] != "Bare" and params["renorm"] != "bare":
            f += str(params["lambda"])
        f += "_hw" + str(params["hw"]) + "_emax" + str(params["emax"])
        f += "_e2max" + str(params["e2max"])
        f += ext_2bme
    except:
        f = "default"
    params["file_name_nn"] = f


def main():
    params = OrderedDict()
    for emax in emax_list:
        for hw in hw_list:
            set_input(params, hw, emax=emax, e2max=2 * emax)
            fsh = gen_script(params, batch)
            if batch == "terminal":
                cmd = "./" + fsh
            elif batch == "slurm":
                cmd = "sbatch " + fsh
            subprocess.call(cmd, shell=True)
            time.sleep(1)


if __name__ == "__main__":
    main()
