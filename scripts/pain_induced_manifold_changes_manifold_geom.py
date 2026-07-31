#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 16:16:36 2024

@author: Lada Kohoutova
"""


def manifold_geom(manifold_code_dir,basedir,datdir,savedir,savename,filepattern,sub_ids, rois):

    # Function to compute manifold geometry for each subject and ROI, and save the results in a pickle file
    # Uses the manifold_analysis_all function available on request

    # Input:
    # manifold_code_dir: path to the capacity_share repo
    # basedir: path to the pain-induced-manifold-changes repo
    # datdir: path to the pain-induced-manifold-changes/data
    # savedir: path to the directory where the results will be saved
    # savename: name of the file where the results will be saved
    # filepattern: pattern to match the files to be processed 
    # sub_ids: list of subject IDs to be processed
    # rois: list of ROIs to be processed        

    import os

    import sys
    sys.path.append(manifold_code_dir)
    from capacity_share.utils import manifold_analysis_all

    import pickle
    import numpy as np
    import pandas as pd



    import warnings
    warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

    import time
    import logging
    import glob



    datdir = os.path.join(basedir, datdir)

    files = glob.glob(os.path.join(datdir, 'manifold_geom_data', f'pain-induced-manifold-changes*{filepattern}*.pickle'))

    savedir = os.path.join(basedir, savedir)

    # get manifold samples
    file = os.path.join(datdir, 'pain-induced-manifold-changes_image_sample_numbers.pickle')
    with open(file, 'rb') as f:
        samples = pickle.load(f)



    stim = ['Warmth', 'LowHeat', 'HighHeat']
    np.random.seed(42)
    for sub_temp in sub_ids:
        sub_files = list(filter(lambda x: sub_temp in x, files))

        logging.basicConfig(filename=os.path.join(savedir, f'manifold_voxel_sampling_{sub_temp}.log'), encoding='utf-8', level=logging.INFO)

        for layer in rois:

            geom_results_sampling_df = pd.DataFrame(columns = ['Subject', 'ROI', 'Condition', 'Capacity', 'Radius',
                                                               'Dimensions', 'cor_axes', 'cor_center', 'cor_center_axes'])

            layer_file = list(filter(lambda x: layer in x, sub_files))[0]
            with open(layer_file, "rb") as f:
                layer_dat = pickle.load(f)

            for condition in layer_dat:


                for i, sample in enumerate(samples):
                    start = time.time()

                    dat_temp = layer_dat[condition]

                    dat_temp = dat_temp[:,:,sample]


                    man_results = manifold_analysis_all(dat_temp)
                    end = time.time()
                    print(end - start)

                    logging.info(f'{sub_temp} - {layer} - {stim[condition]} - {i}')

                # save log including sub id - roi - condition - perm number
                                                                                                                          
                    geom_results_temp = pd.DataFrame({'Subject' : sub_temp,
                                                       'ROI' : layer,
                                                       'Condition' : stim[condition],
                                                       'Capacity' : [man_results['alpha_cor_mf']],
                                                       'Radius' : [man_results['R_M_cor']],
                                                       'Dimensions' : [man_results['D_M_cor']],
                                                       'cor_axes' : [man_results['cor_axes']],
                                                       'cor_center' : [man_results['cor_center']],
                                                       'cor_center_axes' : [man_results['cor_center_axes']]})

                    geom_results_sampling_df = pd.concat([geom_results_sampling_df, geom_results_temp], ignore_index=True)

             #save manifold geom results
            file = os.path.join(savedir, f'{savename}_{sub_temp}_{layer}.pickle')
            with open(file, "wb") as f:
                pickle.dump(geom_results_sampling_df, f)
