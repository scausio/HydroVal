import os


def submit_concatClim(routine, expName, grid, years, suffix, outdir, bproj, force=False):
    """

    :param routine: script to run
    :param expName: experiment name in the conf.yaml
    :param grid: [T, V ,U]
    :param year:
    :param suffix: suffix for intermediate files [argo, argoCORA, sst, sla]
    :param outdir:
    :param force: if true, runs the script even thought the outfile is already created
    :return:
    """
    outfile = os.path.join(outdir, f'{expName}_{grid}_{years[0]}-{years[-1]}_{suffix}.nc')
    grid_files = os.path.join(outdir, f'{expName}_{grid}_*_{suffix}.nc')
    cmd = f'bsub -P {bproj} python  ./bins/{routine} {grid_files}'

    if os.path.exists(outfile):
        if force:
            print('submitting ', cmd)
            os.system(cmd)
        else:
            print(f'Climatology concatenation for {years}: completed!')
    else:
        print('submitting ', cmd)
        os.system(cmd)


def submit_concatPY(routine, expName, years, suffix, outdir, force=False):
    """

    :param routine: script to run
    :param expName: experiment name in the conf.yaml
    :param grid: [T, V ,U]
    :param year:
    :param suffix: suffix for intermediate files [argo, argoCORA, sst, sla]
    :param outdir:
    :param force: if true, runs the script even thought the outfile is already created
    :return:
    """
    outfile = os.path.join(outdir, f'{expName}_{years[0]}-{years[-1]}_{suffix}.nc')
    files = os.path.join(outdir, f'{expName}_*_{suffix}.nc')
    cmd = f" python  ./bins/{routine} {files}"

    if os.path.exists(outfile):
        if force:
            print('submitting ', cmd)
            os.system(cmd)
        else:
            print(f'Concat  completed!')
    else:
        print('submitting ', cmd)
        os.system(cmd)


def submit_PQ(routine, expName, grid, year,inputFile, suffix, outdir,bproj, force=False):
    """

    :param routine: script to run
    :param expName: experiment name in the conf.yaml
    :param grid: [T, V ,U]
    :param year:
    :param suffix: suffix for intermediate files [argo, argoCORA, sst, sla]
    :param outdir:
    :param force: if true, runs the script even thought the outfile is already created
    :return: absolute path to outfile
    """
    outfile = os.path.join(outdir, f'{expName}_{grid}_{year}_{suffix}.nc')

    exp=f'{expName}_{grid}'
    if inputFile:
        cmd = f'bsub -P {bproj} -R "rusage[mem=35G]" python ./preprocessing/{routine} -c catalog_hydroval.yaml -n {exp} -s {int(year) - 1}-12-24 -e {year + 1}-01-06 -i {inputFile}  -o {outdir}/{exp}_{year}_{suffix}.nc'
    else:
        cmd = f'bsub -P {bproj} -R "rusage[mem=35G]" python ./preprocessing/{routine} -c catalog_hydroval.yaml -n {exp} -s {int(year) - 1}-12-24 -e {year + 1}-01-06 -o {outdir}/{exp}_{year}_{suffix}.nc'

    if os.path.exists(outfile):
        if force:
            print('submitting ', cmd)
            #os.system(cmd)
            return cmd
        else:
            print(f'{suffix} preprocessing : completed!')
            return False
    else:
        print('submitting ', cmd)
        return cmd
        #os.system(cmd)
    #return outfile


def submit_hov( expName, year, outdir,bproj, force=False):
    """

    :param routine: script to run
    :param expName: experiment name in the conf.yaml
    :param year:
    :param outdir:
    :param force: if true, runs the script even thought the outfile is already created
    :return: absolute path to outfile
    """

    outfile = os.path.join(outdir, f'{expName}_{year}_domainHov.nc')
    #f'bsub -P {bproj} -R "rusage[mem=35G]" python ./preprocessing/{routine} -c catalog_hydroval.yaml -n {exp} -s {int(year) - 1}-12-24 -e {year + 1}-01-06 -o {outdir}/{exp}_{year}_{suffix}.nc'
    cmd = f"bsub -R 'rusage[mem=35G]' -P {bproj}  python ./preprocessing/hovmoller_pq.py -c catalog_hydroval.yaml -n {expName} -s {int(year) - 1}-12-24 -e {year + 1}-01-06 -o {outfile}"
    if os.path.exists(outfile):
        if force:
            print('submitting ', cmd)
            return cmd
        else:
            print(f'Hovmoller preprocessing for : completed!')
            return False
    else:
        print('submitting ', cmd)
        return cmd

def submit_curr( expName, year, outdir,bproj, force=False):
    """

    :param routine: script to run
    :param expName: experiment name in the conf.yaml
    :param year:
    :param outdir:
    :param force: if true, runs the script even thought the outfile is already created
    :return: absolute path to outfile
    """

    outfile = os.path.join(outdir, f'{expName}_{year}_uvMOOR.nc')
    cmd = f"bsub -P {bproj}  -R 'rusage[mem=10G]' python   ./preprocessing/currentsMoor_pre.py {expName} {year} {outfile}"
    if os.path.exists(outfile):
        if force:
            print('submitting ', cmd)
            #os.system(cmd)
            return cmd
        else:
            print(f'Currents preprocessing for : completed!')
            return False
    else:
        print('submitting ', cmd)
        #os.system(cmd)
        return cmd

def submit_salVol( msk,expName, year, outdir,bproj, force=False):
    """

    :param routine: script to run
    :param expName: experiment name in the conf.yaml
    :param year:
    :param outdir:
    :param force: if true, runs the script even thought the outfile is already created
    :return: absolute path to outfile
    """

    outfile = os.path.join(outdir, f'{expName}_{year}_salVol.nc')

    #cmd = f"bsub -P {bproj} -x -q s_long python ./preprocessing/salinity_volume_pre.py {expName} {','.join(map(str,years))} {outfile}"
    cmd = f"bsub -P {bproj} -x -q s_long python ./preprocessing/salinity_volume_pq.py -c catalog_hydroval.yaml -m {msk} -n {expName} -s {int(year) - 1}-12-24 -e {year + 1}-01-06 -o {outfile}"

    if os.path.exists(outfile):
        if force:
            print('submitting ', cmd)
            os.system(cmd)
        else:
            print(f'Salinity Volume preprocessing : completed!')
    else:
        print('submitting ', cmd)
        os.system(cmd)

def submit_OC( expName, year, suffix, outdir,bproj,force=False):
    """

    :param routine: script to run
    :param expName: experiment name in the conf.yaml
    :param years:
    :param outdir:
    :param force: if true, runs the script even thought the outfile is already created
    :return: absolute path to outfile
    """
    #outfile = os.path.join(outdir, f'{expName}_{year}-{suffix}.nc')
    cmd = f"bsub -P {bproj} -R 'rusage[mem=20G]' -q s_long python ./preprocessing/overturningCirculation_pre.py {expName} {year} {suffix} {outdir}"
    print('submitting ', cmd)
    # os.system(cmd)
    return cmd

def submit_mld( expName, year, outdir,bproj, force=False):
    """

    :param routine: script to run
    :param expName: experiment name in the conf.yaml
    :param year:
    :param outdir:
    :param force: if true, runs the script even thought the outfile is already created
    :return: absolute path to outfile
    """

    outfile = os.path.join(outdir, f'{expName}_{year}_mld.nc')
    cmd = f"bsub -P {bproj} -Is -R 'rusage[mem=10G]' python   ./preprocessing/mld_pre.py {expName} {year} {outfile}"
    if os.path.exists(outfile):
        if force:
            print('submitting ', cmd)
            os.system(cmd)
            return cmd
        else:
            print(f'MLD preprocessing for {year}: completed!')
            return False
    else:
        print('submitting ', cmd)
        os.system(cmd)
        return cmd



def submit_decim(expName, grid, year, outdir,bproj,decim_factor, force=False):

    outfile = os.path.join(outdir, f'{expName}_{grid}_{year}_decim{decim_factor}.nc')

    exp=f'{expName}_{grid}'

    cmd = f'bsub -P {bproj} -R "rusage[mem=15G]" -M 3145728 python ./preprocessing/decimate_pre.py -c catalog_hydroval.yaml -n {exp} -s {int(year) - 1}-12-24 -e {year + 1}-01-06 -o {outfile}'

    if os.path.exists(outfile):
        if force:
            print('submitting ', cmd)
            os.system(cmd)
        else:
            print(f'Decimation preprocessing for {year}: completed!')
            return False
    else:
        print('submitting ', cmd)
        os.system(cmd)

def submit_job(job, **kwargs):
    if 'x' in kwargs:
        cmd = f"bsub -P 0512 -q s_long python ./bins/jobs.py {job}_{kwargs['x']}_{kwargs['y']}"
    elif 'decimFac' in kwargs:
        cmd = f"bsub -P 0512 -q s_long python ./bins/jobs.py {job}_{kwargs['decimFac']}"
    else:
        cmd = f'bsub -P 0512 -q s_long python ./bins/jobs.py {job} '
    print (f'Submitting {cmd}')
    os.system(cmd)