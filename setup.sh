#!/bin/bash
module purge
module load intel19.5/udunits/2.2.26
module load intel19.5/szip/2.1.1
module load curl/7.66.0
module load gcc_9.1.0
module load intel19.5/19.5.281
module load intel19.5/hdf5/1.10.5
module load intel19.5/netcdf/C_4.7.2-F_4.5.2_CXX_4.3.1
module load intel19.5/ncview/2.1.8
module load cmake
module load impi19.5
module load impi19.5/hdf5/1.10.5
module load impi19.5/parallel-netcdf/1.12.0
module load impi19.5/netcdf/C_4.7.2-F_4.5.2_CXX_4.3.1
module load anaconda

conda activate /work/opa/bsfs-dev/condas/envs/hydroval

export PYTHONPATH="/work/opa/sc33616/nemo/tools/bs-mfc-pq-2-refactor/"
