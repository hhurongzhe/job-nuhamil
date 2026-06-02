import os
import sys
import subprocess
from collections import OrderedDict
import time

HOME = "/Users/mac/Desktop/job-nuhamil"
path_to_nninput = f"{HOME}/input_nn_files"
exe_file = f"{HOME}/NuHamil.exe"

n_nodes = 1
n_omp_threads = 32
mpi = n_nodes > 1

batch = "terminal"
# batch = 'slurm'

partition = "c128m512"
# partition = "c128m1024"

# 3-body SRG space
# ramp_space = "ramp40-5-36-7-32-9-28-11-24"  # This should be enough up to 40Ca or so. From Phys. Rev. C90, 024325 (2014).
# ramp_space = "ramp40-7-38-9-36" # This should be enough up to A~100. From Phys. Lett. B736, 119 (2014).
ramp_space = "ramp12"  # only for testing
# ramp_space = "ramp46"


NNF, TNF = "N3LO_EM500", "EM1.8_2.0"
# NNF, TNF = "N3LO_EM500", "EM7.5"
# NNF, TNF = "N3LO_EM500", "EM2.0_2.0"
# NNF, TNF = "N3LO_EM500", "EM2.0_2.5"
# NNF, TNF = "N3LO_EM500", "EM2.2_2.0"
# NNF, TNF = "N3LO_EM500", "EM2.8_2.0"
# NNF, TNF = "N3LO_EM500", "3NF400"
# NNF, TNF = "N2LO_sat", "N2LOsat"
# NNF, TNF = "DNLOGO450", "DNLOGO450"
# NNF, TNF = "DN2LOGO450", "DN2LOGO450"
# NNF, TNF = "DN2LOGO394", "DN2LOGO394"
# NNF, TNF = "N3LO_EM500", "N3LOEMlnl"
# NNF, TNF = "N4LO_EMN500", "N4LOEMNlnl"
# NNF, TNF = "N3LO_local1.2", "local"
# NNF, TNF = "N3LO_local1.2", "lnl"
# NNF, TNF  = "N3LO_texas", "N3LO_texas"

# ext_3bme = ".me3j.gz"
ext_3bme = ".stream.bin"

hw_temp = None  # if using hw-conversion technique...
# hw_temp = 30

hw_list = [16]
emax_list = [6]
e3max_list = [12]
# hw_list = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]
# emax_list = [2, 4, 6, 8, 10, 12, 14, 16]
# e3max_list = [18, 24]


if batch == "terminal":
    header = ""
elif batch == "slurm":
    header = "#!/bin/bash\n"
    header += f"#SBATCH --partition {partition}\n"
    header += f"#SBATCH -J {TNF}\n"
    header += "#SBATCH --nodes=" + str(n_nodes) + "\n"
    header += "#SBATCH --ntasks-per-node=1\n"
    header += "#SBATCH --cpus-per-task=" + str(n_omp_threads) + "\n"
    header += "#SBATCH --output=./result/slurm-%j.out\n"
    header += "source sourceme.sh\n"


def set_input(params, hw=20, hw_target=None, emax=14, e2max=28, e3max=16):
    # basic parameters
    params["rank"] = 3
    params["hw"] = hw
    if hw_target != None:
        params["hw_target"] = hw_target  # hw conversion
    params["renorm"] = "bare"
    params["lambda"] = 2.0
    params["emax"] = emax
    params["e2max"] = e2max
    params["e3max"] = e3max
    params["NNInt"] = NNF
    params["input_nn_file"] = f"{path_to_nninput}/{params['NNInt']}_kmax8_N100_Jmax8.bin"
    # params["input_nn_file"] = f"{path_to_nninput}/{params['NNInt']}_kmax20_N200_Jmax8.bin"
    # params["nmesh2"] = 200
    # params["pmax2"] = 20.0
    params["3nf"] = TNF
    # params["jmax3"] = params["e3max"] * 2 + 3
    params["jmax3"] = 15
    params["ramp"] = ramp_space
    params["genuine_3bf"] = True
    params["only_no2b_elements"] = True
    # params['lab_3bme_precision'] = "half"
    # params["path_to_Hebeler_files"] = "/Users/mac/Desktop/input_3n_files"
    params["path_to_tmp_dir"] = f"{HOME}/workspace"
    if params["genuine_3bf"]:
        set_three_body_force(params)
    if params["rank"] == 3:
        set_file_name_3n(params)


def get_script_name(params):
    fbase = "vHamil_MECalc_A" + str(params["rank"]) + "_hw" + str(params["hw"])
    ms = ""
    fbase += ms
    if params["rank"] > 2:
        if params["genuine_3bf"]:
            try:
                fbase += "_" + params["3nf"]
            except:
                pass
    if "3nf" in params:
        del params["3nf"]
    fbase = "vHamil_MECalc_A3_" + params["file_name_3n"].split(ext_3bme)[0]
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


def set_three_body_force(params):
    warning = False
    if params["rank"] < 3:
        return
    if not params["genuine_3bf"]:
        return
    if params["3nf"] == "EM1.8_2.0":  # use with SRG evolved two-body interaction (EM500)
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 4
        params["LECs"] = [-8.1e-1, -3.2, 5.4, 1.264, -0.120]
        params["lambda_3nf_nonlocal"] = 2 * 197.3269788
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "EM7.5":  # use with SRG evolved two-body interaction (EM500)
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 4
        params["LECs"] = [-8.1e-1, -3.2, 5.4, 7.5, 0.942]
        params["lambda_3nf_nonlocal"] = 2 * 197.3269788
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "EM2.0_2.0":  # use with SRG evolved two-body interaction (EM500)
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 4
        params["LECs"] = [-8.1e-1, -3.2, 5.4, 1.271, -0.131]
        params["lambda_3nf_nonlocal"] = 2 * 197.3269788
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "EM2.0_2.5":  # use with SRG evolved two-body interaction (EM500)
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 4
        params["LECs"] = [-8.1e-1, -3.2, 5.4, -0.292, -0.592]
        params["lambda_3nf_nonlocal"] = 2.5 * 197.3269788
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "EM2.2_2.0":  # use with SRG evolved two-body interaction (EM500)
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 4
        params["LECs"] = [-8.1e-1, -3.2, 5.4, 1.214, -0.137]
        params["lambda_3nf_nonlocal"] = 2 * 197.3269788
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "EM2.8_2.0":  # use with SRG evolved two-body interaction (EM500)
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 4
        params["LECs"] = [-8.1e-1, -3.2, 5.4, 1.278, -0.078]
        params["lambda_3nf_nonlocal"] = 2 * 197.3269788
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "PWA2.0_2.0":  # use with SRG evolved two-body interaction (EM500)
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 4
        params["LECs"] = [-7.6e-1, -4.78, 3.96, -3.007, -0.686]
        params["lambda_3nf_nonlocal"] = 2 * 197.3269788
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "N2LOsat":  # use with bare two-body interaction (N2LO_sat)
        params["NNInt"] = "N2LO_sat"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 3
        params["LECs"] = [-1.12152120, -3.92500586, 3.76568716, 0.81680589, -0.03957471]
        params["lambda_3nf_nonlocal"] = 450
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "DN2LOGO394":
        params["NNInt"] = "DN2LOGO394"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 4
        params["LECs"] = [-0.74, -3.622246, 2.446123, 0.081, -0.002]
        params["lambda_3nf_nonlocal"] = 394
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "DN2LOGO450":
        params["NNInt"] = "DN2LOGO450"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 3
        params["LECs"] = [-0.74, -3.622246, 2.446123, -0.454, -0.186]
        params["lambda_3nf_nonlocal"] = 450
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "DNLOGO450":
        params["NNInt"] = "DNLOGO450"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 3
        params["LECs"] = [0.0, -2.972246, 1.486123, 0.0, 0.0]
        params["lambda_3nf_nonlocal"] = 450
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    if params["3nf"] == "N3LO_NoggaA":
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 2
        params["LECs"] = [-8.1e-1, -3.2, 5.4, -1.11, -0.66]
        params["lambda_3nf_nonlocal"] = 500
        return

    if params["3nf"] == "N3LO_NoggaB":
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 2
        params["LECs"] = [-8.1e-1, -3.2, 5.4, 8.14, -2.02]
        params["lambda_3nf_nonlocal"] = 500
        return

    if params["3nf"] == "3NF400":  # use with EM500 two-body interaction
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "Local"
        params["RegulatorPower"] = 2
        params["LECs"] = [-8.1e-1, -3.2, 5.4, -2.0e-1, 9.8e-2]
        params["lambda_3nf_local"] = 400
        return

    if params["3nf"] == "3NF500_BetaDecay_Local":  # use with EM500 two-body interaction
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "Local"
        params["RegulatorPower"] = 2
        params["LECs"] = [-8.1e-1, -3.2, 5.4, 0.83, -0.052]
        params["lambda_3nf_local"] = 500
        return

    if params["3nf"] == "N3LOEMlnl":  # use with EM500 two-body interaction
        params["NNInt"] = "N3LO_EM500"
        params["Regulator"] = "LNL"
        params["RegulatorPower"] = 2
        params["LECs"] = [-8.1e-1, -3.2, 5.4, 7.0e-1, -6.0e-2]
        params["lambda_3nf_local"] = 650
        params["lambda_3nf_nonlocal"] = 500
        return

    if params["3nf"] == "N4LOEMNlnl":  # use with EMN500 two-body interaction
        params["NNInt"] = "N4LO_EMN500"
        params["Regulator"] = "LNL"
        params["RegulatorPower"] = 2
        params["LECs"] = [-7.3e-1, -3.38, 1.69, -1.8, -3.1e-1]
        params["lambda_3nf_local"] = 650
        params["lambda_3nf_nonlocal"] = 500
        return

    if params["3nf"] == "local":
        params["NNInt"] = "N3LO_local1.2"
        params["Regulator"] = "Local"
        params["RegulatorPower"] = 2
        params["LECs"] = [-0.74, -3.61, 2.44, -2.0, -0.541]
        params["lambda_3nf_local"] = 500
        return

    if params["3nf"] == "lnl":
        params["NNInt"] = "N3LO_local1.2"
        params["Regulator"] = "LNL"
        params["RegulatorPower"] = 2
        params["LECs"] = [-0.74, -3.61, 2.44, 6.0, 0.894]
        params["lambda_3nf_local"] = 700
        params["lambda_3nf_nonlocal"] = 500
        return

    if params["3nf"] == "N3LO_texas":
        params["NNInt"] = "N3LO_texas"
        params["Regulator"] = "NonLocal"
        params["RegulatorPower"] = 4
        params["LECs"] = [-1.07, -5.32, 3.56, -5.060563, -1.034629]
        params["lambda_3nf_nonlocal"] = 394
        if params["rank"] > 2:
            params["renorm"] = "bare"
        return

    print("Unknown three-body force keyword" + params["3nf"])
    sys.exit()


def set_file_name_3n(params):
    try:
        f = "ThBME"
        if "only_hf_monopole" in params and params["only_hf_monopole"]:
            f += "_Monopole"
        elif "only_no2b_elements" in params and params["only_no2b_elements"]:
            f += "_NO2B"
        else:
            f += "_full"
        if "lab_3bme_precision" in params and params["lab_3bme_precision"] != "single":
            f += "_{:s}".format(params["lab_3bme_precision"])
        if params["3nf"] in ["EM1.8_2.0", "EM2.0_2.0", "EM2.0_2.5", "EM2.2_2.0", "EM2.8_2.0", "PWA2.0_2.0", "N2LOsat", "DN2LOGO394", "DN2LOGO450", "DNLOGO450", "EM7.5", "N3LO_NoggaA", "N3LO_NoggaB", "3NF400", "3NF500_BetaDecay_Local", "N3LOEMlnl", "N4LOEMNlnl", "local", "lnl", "N3LO_texas"]:
            f += "_" + params["3nf"]
            if "jmax3" in params and params["jmax3"] < 2 * params["e3max"] + 3:
                f += "_JJmax" + str(params["jmax3"])
        else:
            if params["renorm"] == "Bare" or params["renorm"] == "bare":
                if params["genuine_3bf"]:
                    if "j3max_initial_3nf" in params:
                        f += "_3NFJmax" + str(params["j3max_initial_3nf"])
                    if "jmax3" in params and params["jmax3"] < 2 * params["e3max"] + 3:
                        f += "_JJmax" + str(params["jmax3"])
                    f += "_c1_" + str(params["LECs"][0]) + "_c3_" + str(params["LECs"][1]) + "_c4_" + str(params["LECs"][2]) + "_cD_" + str(params["LECs"][3]) + "_cE_" + str(params["LECs"][4])
                    f += "_" + params["Regulator"] + str(params["RegulatorPower"])
                    if params["Regulator"] == "LNL":
                        f += "_" + str(params["lambda_3nf_local"]) + "_" + str(params["lambda_3nf_nonlocal"])
                    if params["Regulator"] == "Local":
                        f += "_" + str(params["lambda_3nf_local"])
                    if params["Regulator"] == "NonLocal":
                        f += "_" + str(params["lambda_3nf_nonlocal"])
            else:
                f += "_" + str(params["renorm"]) + str(params["lambda"]) + "_" + params["ramp"]
                f += "_" + str(params["NNInt"])
                if params["genuine_3bf"]:
                    if "j3max_initial_3nf" in params:
                        f += "_3NFJmax" + str(params["j3max_initial_3nf"])
                    if "jmax3" in params and params["jmax3"] < 2 * params["e3max"] + 3:
                        f += "_JJmax" + str(params["jmax3"])
                    f += "_c1_" + str(params["LECs"][0]) + "_c3_" + str(params["LECs"][1]) + "_c4_" + str(params["LECs"][2]) + "_cD_" + str(params["LECs"][3]) + "_cE_" + str(params["LECs"][4])
                    f += "_" + params["Regulator"] + str(params["RegulatorPower"])
                    if params["Regulator"] == "LNL":
                        f += "_" + str(params["lambda_3nf_local"]) + "_" + str(params["lambda_3nf_nonlocal"])
                    if params["Regulator"] == "Local":
                        f += "_" + str(params["lambda_3nf_local"])
                    if params["Regulator"] == "NonLocal":
                        f += "_" + str(params["lambda_3nf_nonlocal"])
        if "hw_target" in params:
            f += "_hwsrg" + str(params["hw"]) + "_hw" + str(params["hw_target"])
        if not "hw_target" in params:
            f += "_hw" + str(params["hw"])
        f += "_emax" + str(params["emax"]) + "_e2max" + str(params["e2max"]) + "_e3max" + str(params["e3max"])
        f += ext_3bme
    except:
        f = "default"
    params["file_name_3n"] = f


def main():
    params = OrderedDict()
    for hw in hw_list:
        for emax in emax_list:
            for e3max in e3max_list:
                if hw_temp == None:
                    set_input(params, hw, hw_target=None, emax=emax, e2max=2 * emax, e3max=e3max)
                else:
                    set_input(params, hw_temp, hw_target=hw, emax=emax, e2max=2 * emax, e3max=e3max)
                fsh = gen_script(params, batch)
                if batch == "terminal" or batch == "local":
                    cmd = "./" + fsh
                elif batch == "slurm":
                    cmd = "sbatch " + fsh
                subprocess.call(cmd, shell=True)
                time.sleep(1)


if __name__ == "__main__":
    main()
