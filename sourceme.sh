#!/bin/bash

module purge
# module load gcc/12.2.0

export NUHAMIL_DEPS_ROOT=/tns/hrz/opt_setup/opt
# export NUHAMIL_DEPS_ROOT=/lustre/home/2101110124/opt_setup/opt

export OPENMPI_ROOT=${NUHAMIL_DEPS_ROOT}/openmpi
export GSL_ROOT=${NUHAMIL_DEPS_ROOT}/gsl
export HDF5_ROOT=${NUHAMIL_DEPS_ROOT}/hdf5
export OPENBLAS_ROOT=${NUHAMIL_DEPS_ROOT}/openblas
export BOOST_ROOT=${NUHAMIL_DEPS_ROOT}/boost

export PATH=${OPENMPI_ROOT}/bin:${HDF5_ROOT}/bin:${GSL_ROOT}/bin:$PATH
export CPATH=${BOOST_ROOT}/include:${HDF5_ROOT}/include:${GSL_ROOT}/include:${OPENBLAS_ROOT}/include:${CPATH:-}
export LIBRARY_PATH=${BOOST_ROOT}/lib:${HDF5_ROOT}/lib:${GSL_ROOT}/lib:${OPENBLAS_ROOT}/lib:${OPENMPI_ROOT}/lib:${LIBRARY_PATH:-}
export LD_LIBRARY_PATH=${BOOST_ROOT}/lib:${HDF5_ROOT}/lib:${GSL_ROOT}/lib:${OPENBLAS_ROOT}/lib:${OPENMPI_ROOT}/lib:${LD_LIBRARY_PATH:-}
export HDF5_USE_FILE_LOCKING=FALSE

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
export OMP_PLACES=cores
export OMP_PROC_BIND=spread
export OMP_STACKSIZE=512M

export OPENBLAS_NUM_THREADS=1
export GOTO_NUM_THREADS=1
export MKL_NUM_THREADS=1

ulimit -s unlimited
