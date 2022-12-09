
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import scipy.stats as stats 
import nibabel as nib
import nibabel.processing
import seaborn as sns
import os
import shutil
from itertools import combinations



def create_performance_figures(r2_scores, correlations,label, results_path, analysis_id, subsets):
    # The function create_performance_figures takes in the r2 scores, correlations, label, results path,
    # analysis id, and subsets as input. 
    # It formats the label by replacing certain substrings with more descriptive labels. 
    # It then sets the range for the y-axis based on the analysis id and creates box and whisker plots for the r2 scores and correlations.
    # It saves the plots with filenames that include the analysis id and the type of plot (r-squared or Pearson correlation). 
    # It also takes in the number of sets and uses that to determine the layout of the plots.

    title = ''
    xticklabels = label

    n_sets = subsets
    if analysis_id=='analysis_1':
        range_y = 'analysis1'
    if analysis_id=='analysis_2':
        range_y = 'analysis2'
    if analysis_id=='analysis_3':
        range_y = 'analysis3'    
    if analysis_id=='analysis_4':
        range_y = 'analysis4'  
    if analysis_id=='analysis_5':
        range_y = 'analysis5'    
    if analysis_id=='analysis_6':
        range_y = 'analysis6'  
    if analysis_id == 'analysis_7':
        range_y = 'analysis7'
    if analysis_id =='analysis_8':
        range_y = 'analysis8'
    # for loop over subsets
    
    print('Saving boxplots to folder: {}'.format(os.path.join(results_path,analysis_id)))    
    ylabel = 'R-squared'
    path_file = os.path.join(results_path,analysis_id, analysis_id + '_boxplots_rsquared.png')
    box_and_whisker(np.transpose(r2_scores), title, ylabel, xticklabels, path_file,n_sets,range_y)
    
    ylabel = 'Pearson correlation'
    path_file = os.path.join(results_path,analysis_id, analysis_id + '_boxplots_correlations.png')

    box_and_whisker(np.transpose(correlations), title, ylabel, xticklabels, path_file,n_sets,range_y)

def create_performance_figures_loo(r2_scores, correlations,label, results_path, output_path, filename):
    font = {'family' : 'normal',
            'size'   : 15}

    matplotlib.rc('font', **font)
    
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize =(20, 20))
    plt.subplots_adjust(bottom=0.6)

    ax1.boxplot(np.transpose(r2_scores))
    ax1.set_ylim([np.min(r2_scores)-0.1, np.max(r2_scores)+0.3])
    ax1.set_ylabel('{}'.format('$R^2$'))
    ax1.xaxis.set_ticks([x for x in range(1,len(label)+1)])
    ax1.xaxis.set_ticklabels(label, rotation=90)
    
    correlations = np.transpose(correlations)
    
    # remove data points that are nan or from a site with one subject
    mask = np.logical_and(~np.isnan(correlations),correlations<0.99)
    filtered_data = [d[m] for d, m in zip(correlations.T, mask.T)]
    
    ax2.boxplot(filtered_data)
    ax2.set_ylim([np.min(filtered_data)-0.1, np.max(filtered_data)+0.3])
    ax2.set_ylabel('Correlation')
    
    print([x for x in range(1,len(label)+1)])
    
    ax2.xaxis.set_ticks([x for x in range(1,len(label)+1)])
    ax2.xaxis.set_ticklabels(label, rotation=90)
    
    plt.savefig(os.path.join(results_path, output_path,filename+ '.png'))
    
    
def box_and_whisker(data, title, ylabel, xticklabels, path,n_sets, range_y):
    
    # The function box_and_whisker takes in data (R-squared or correlation values for different model runs), a title for the plot, the y-axis label, 
    # the x-axis tick labels, the path where the figure should be saved, the number of sets of data, and the range of y-values for the plot.
    # It creates a box-and-whisker plot with significance bars, setting the figure quality and font size, labeling the axes and setting the tick sizes,
    # hiding the major x-axis ticks and showing the minor ones, and coloring the boxes in the plot using Seaborn's 'pastel' palette.
    # It then checks for statistical significance between the data sets, adding significance bars to the plot if necessary. 
    # Finally, it saves the figure to the specified path.

    # Source: https://rowannicholls.github.io/python/graphs/ax_based/boxplots_significance.html

    font = {'family' : 'Arial',
            'size'   : 15}
    matplotlib.rc('font', **font)

    # Change figure quality
    plt.rc('figure', dpi=300)

    fig, ax = plt.subplots(ncols=1, figsize =(7, 7))
    
    
    bp = ax.boxplot(data, widths=0.6, patch_artist=True)
    # Graph title
    ax.set_title(title, fontname="Arial", fontsize=16)
    # Label y-axis
    ax.set_ylabel(ylabel,fontname="Arial", fontsize=20)
    # Label x-axis ticks
    ax.set_xticklabels(xticklabels,rotation=90,fontname="Arial",fontsize=20)
    # Change y-tick fontsize
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=20)
   
    # Hide x-axis major ticks
    ax.tick_params(axis='x', which='major', length=0)
    # Show x-axis minor ticks
    xticks = [0.5] + [x + 0.5 for x in ax.get_xticks()]
    ax.set_xticks(xticks, minor=True)
    # Clean up the appearance
    ax.tick_params(axis='x', which='minor', length=3, width=1)

    ncolors = np.int8(data.shape[1]/n_sets)

    # Change the colour of the boxes to Seaborn's 'pastel' palette
    colors = sns.color_palette('colorblind', ncolors)
    indexes = np.arange(0, data.shape[1])
    
    for patch, i in zip(bp['boxes'], indexes):
        # repeat colors if there's > 1 "sets" (e.g. crossval types, acute/chronic training)
        patch.set_facecolor(colors[i % ncolors])

    # Colour of the median lines
    plt.setp(bp['medians'], color='k')

    # Check for statistical significance
    significant_combinations = []
    
    # Check from the outside pairs of boxes inwards
    ls = list(range(1, data.shape[1] + 1))
    
    # This code generates all possible pairs of columns from a 2D data array. 
    # If n_sets is greater than 1, the code will first generate all possible pairs of columns within each group of nsets columns,
    # and then generate all possible pairs of columns across each group of columns. If n_sets is 1, then the code will simply 
    # generate all possible pairs of columns in the entire data array. The resulting pairs are stored in the combos list.
    
    if n_sets >1: #imagine nsets = 3
        print(n_sets)
        print('nsets math')
        # first within each group compare with each other.
        allsets = [] # store within-group combinations here.

        counter = 0
        groupsize = np.int8(data.shape[1]/n_sets)
        
        for set in range(0, n_sets):
            end = groupsize+counter
            set_combinations = list(combinations((ls[counter:end]), 2))

            allsets = allsets + set_combinations
            counter = counter + groupsize
        
        # then compare each 'corresponding' result between groups.
        for set in range(0, np.int8(data.shape[1]/n_sets)): 
            #set = 0
            x_th_elements=[]
            x=set
            for ignore in range(0, n_sets): 
                x_th_elements.append(ls[x])
                x = x + groupsize 
            
            allsets = allsets + list(combinations(x_th_elements,2))
            
        combos = allsets
    else:
        combos = [(ls[x], ls[x + y]) for y in reversed(ls) for x in range((len(ls) - y))]
        
    for c in combos:
        data1 = data[:,c[0]-1]
        data2 = data[:,c[1]-1]
        #print(data2.shape)
        # Significance
        try:
            U, p = stats.mannwhitneyu(data1, data2, alternative='two-sided')
        except:
            ValueError('Values all the same! ')
        if p < 0.05:
            significant_combinations.append([c, p])
            
    # Get info about y-axis
    bottom_actual, top_actual = ax.get_ylim()
    factor = 0.02
    if range_y == 'analysis1' :
        if ylabel == 'Pearson correlation':
            top = 0.5
            bottom = 0.35
            factor=0.008
        elif ylabel == 'R-squared':
            top = 0.2
            bottom = 0.1
            factor = 0.02
    if range_y == 'analysis2':
        if ylabel == 'Pearson correlation':
            top = 0.7
            bottom = 0.2
        elif ylabel == 'R-squared':
            top = 0.3
            bottom = -0.1
    if range_y == 'analysis3':
        if ylabel == 'Pearson correlation':
            top = 0.5
            bottom = 0.3
            factor= 0.01

        elif ylabel == 'R-squared':
            top = 0.2
            bottom = -0.1
            factor= 0.02

    if range_y == 'analysis4' or range_y == 'analysis5':
        if ylabel == 'Pearson correlation':
            top = 0.5  
            bottom = 0.3
            factor= 0.01
        elif ylabel == 'R-squared':
            top = 0.2
            bottom = 0.1
            factor= 0.01

    if range_y == 'analysis6' :
        if ylabel == 'Pearson correlation':
            top = 0.6
            bottom = 0.3
            factor = 0.012
        elif ylabel == 'R-squared':
            top = 0.6
            bottom = -0.1
            factor = 0.03
            
    if range_y == 'analysis7':
        if ylabel == 'Pearson correlation':
            top = 0.6
            bottom = 0.3
            factor = 0.005
        elif ylabel == 'R-squared':
            top = 0.4
            bottom = 0.2
            factor = 0.005
            
    if range_y == 'analysis8':
        if ylabel == 'Pearson correlation':
            top = 0.6
            bottom = 0.3
            factor = 0.004
        elif ylabel == 'R-squared':
            top = 0.2
            bottom = 0.15
            factor = 0.005
            
    yrange = top - bottom
    
    #yrange = 1.75 -0
    # Significance bars
    add_sig_bars=True
    if add_sig_bars:
        for i, significant_combination in enumerate(significant_combinations):
            # Columns corresponding to the datasets of interest
            x1 = significant_combination[0][0]
            x2 = significant_combination[0][1]
            # What level is this bar among the bars above the plot?
            level = len(significant_combinations) - i
            # Plot the bar
            bar_height = (top_actual * factor * level) + top_actual
            bar_tips = bar_height - (yrange * 0.01)
            plt.plot(
                [x1, x1, x2, x2],
                [bar_tips, bar_height, bar_height, bar_tips], lw=0.5, c='k')
            # Significance level
            p = significant_combination[1]
            if p < 0.001:
                sig_symbol = '***'
            elif p < 0.01:
                sig_symbol = '**'
            elif p < 0.05:
                sig_symbol = '*'
            text_height = bar_height - 0.0001
            plt.text((x1 + x2) * 0.5, text_height, sig_symbol, ha='center', c='k',fontsize=6)

    # Adjust y-axis
    bottom, top = ax.get_ylim()
    if bottom < 0:
        bottom = 0
    yrange = top - bottom
    if range_y == 'analysis1':
        #ax.set_ylim(bottom - 0.1 * yrange, top)
        if ylabel == 'Pearson correlation':
            ax.set_ylim(0.35, 0.52)
        elif ylabel == 'R-squared':
            ax.set_ylim(0.1, 0.28)
    if range_y == 'analysis2':
        #ax.set_ylim(bottom - 0.1 * yrange, top)
        if ylabel == 'Pearson correlation':
            ax.set_ylim(0.2, 0.8)
        elif ylabel == 'R-squared':
            ax.set_ylim(-0.1, 0.35)
    if range_y == 'analysis4' or range_y == 'analysis5':
        #ax.set_ylim(bottom - 0.1 * yrange, top)
        if ylabel == 'Pearson correlation':
            ax.set_ylim(0.35, 0.55)
        elif ylabel == 'R-squared':
            ax.set_ylim(0.1, 0.3)
    if range_y == 'analysis6' or range_y == 'analysis7':
        #ax.set_ylim(bottom - 0.1 * yrange, top)
        if ylabel == 'Pearson correlation':
            ax.set_ylim(0.4, 0.7)
        elif ylabel == 'R-squared':
            ax.set_ylim(0.2, 0.4)
            
    if range_y == 'analysis3':
        #ax.set_ylim(bottom - 0.1 * yrange, top)
        if ylabel == 'Pearson correlation':
            ax.set_ylim(0.3, 0.65)
        elif ylabel == 'R-squared':
            ax.set_ylim(0.05, 0.33)
            
    if range_y == 'analysis8':
        #ax.set_ylim(bottom - 0.1 * yrange, top)
        if ylabel == 'Pearson correlation':
            ax.set_ylim(0.35, 0.60)
        elif ylabel == 'R-squared':
            ax.set_ylim(0.1, 0.28)
    # Annotate sample size below each box
    #for i, dataset in enumerate(data):
        #sample_size = len(dataset)
        #ax.text(i + 1, bottom, fr'n = {sample_size}', ha='center', size='x-small')

    plt.savefig(path,bbox_inches='tight')
    

def generate_wb_files(atlas, scenesdir, hcp_dir, wbpath, results_path, output_path, analysis_id, y_var,chaco_type, subset, model_tested,crossval):

    atlas_dir = scenesdir 
    hcp_dir =hcp_dir
    
    textfiles_betas = ['meanbetas_allperms_0', 'meanbetas_allperms_50', 'meanbetas_allperms_90', 'meanbetas_allperms_99']

    for file in textfiles_betas:
        print('making subcortical + surface betas files')
        
        textfile = os.path.join(results_path, output_path, '{}_{}_{}_{}_{}_crossval{}_{}.txt'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
        
        # load text file in fs86 parc (86,1) vector/shen268 parc (268,1)
        scalar = np.genfromtxt(textfile, dtype = "float32", delimiter = ',', usecols = 0)
        
        # freesurfer86 region
        if scalar.shape[0]==86:
            
            # fs86 parcellation - surface files
            atlas_file = nib.load(os.path.join(atlas_dir,'fs86_dil1_allsubj_mode.nii.gz')).get_fdata()
            nodes = np.unique(atlas_file)
            
            nodes = np.delete(nodes,0)
            data = np.zeros(atlas_file.shape, dtype=np.float32)
            for i,n in enumerate(nodes):
                if n<18:
                    continue
                data[atlas_file == n] = scalar[i]
                
            sample_img = nib.load(os.path.join(atlas_dir,'fs86_dil1_allsubj_mode.nii.gz'))
            save_file = os.path.join(results_path, analysis_id ,'{}_{}_{}_{}_{}_crossval{}_{}_surfacefile_betas.nii.gz'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
            
            # store nifti header info for saving file
            save_img = nib.Nifti1Image(data, sample_img.affine, sample_img.header)
            
            save_img.set_data_dtype(data.dtype)
            
            nib.save(save_img, save_file) 
            
            filename = save_file
            surf_prefix = filename.replace('.nii.gz', '')
            
            for hemi in ['L', 'R']:
                os.chdir(wbpath) 
                cmd = './wb_command' + ' -volume-to-surface-mapping '+  filename + ' ' + hcp_dir + '/S1200.' + hemi + '.midthickness_MSMAll.32k_fs_LR.surf.gii '+ surf_prefix + hemi + '.shape.gii -enclosing'
                os.system(cmd)
                #cmd = './wb_command -metric-dilate ' + surf_prefix + hemi + '.shape.gii' + ' ' + hcp_dir + '/S1200.' + hemi + '.midthickness_MSMAll.32k_fs_LR.surf.gii 20 ' + surf_prefix + hemi + '_filled.shape.gii -nearest'
                #os.system(cmd)

            os.remove(surf_prefix + '.nii.gz')
            
            
            # fs86 parcellation - subcortical volume ------------
            os.chdir('/home/ubuntu/enigma/motor_predictions/wb_files/workbench_ubuntu')

            roivol = nib.load(os.path.join(atlas_dir,'fs86_dil1_allsubj_mode.nii.gz'))
            Vroi = roivol.get_fdata()
            Vnew = np.zeros(Vroi.shape)
            roidata = np.genfromtxt( textfile, dtype = "float32", delimiter = ',', usecols = 0)

            for i,v in enumerate(np.unique(Vroi[Vroi>0])):
                Vnew[Vroi == v] = roidata[i]
            imgnew = nib.Nifti1Image(Vnew, affine = roivol.affine, header = roivol.header)
            
            nib.save(imgnew, "subcortical_volumes.nii.gz")
            datapath =  "subcortical_volumes.nii.gz"
            newdata = nib.load("subcortical_volumes.nii.gz")
            
            cc400 = nib.load(os.path.join(atlas_dir,'fs86_dil1_allsubj_mode.nii.gz'))
            atlas2 = nib.load(os.path.join(atlas_dir,'fs86_dil1_allsubj_mode_subcort.nii.gz'))
            
            atlas1=nibabel.processing.resample_from_to(atlas2, cc400, order=0)
            
            V400 = cc400.get_fdata()
            V1 = atlas1.get_fdata()
            
            subcortvals = np.unique(V400[(V400>0) * (V1>0)])
            V400_subcort = V400 * np.isin(V400,subcortvals)
                   
            imgdata = newdata.get_fdata()            
            Vnew = np.double(imgdata*(V400_subcort>0))
            
            cc400.header.set_data_dtype(np.float64)  # without this the visualization breaks. LOVE IT!
            
            newdata_subcort=nib.Nifti1Image(Vnew, affine=cc400.affine, header=cc400.header)

            save_file = os.path.join(results_path, analysis_id,'{}_{}_{}_{}_{}_crossval{}_{}_subcortical_betas_file.nii.gz'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
            print('saving betas file: {}'.format(save_file))
            nib.save(newdata_subcort, save_file)

        elif scalar.shape[0]==268:
            # It first loads the scalar data from the text file, and then loads the atlas file for the shen268 parcellation. 
            atlas_file = nib.load(os.path.join(atlas_dir, 'shen268_MNI1mm_dil1.nii.gz')).get_fdata()
            subcorticalshen = np.loadtxt(os.path.join(atlas_dir, 'shen_subcorticalROIs.txt'))
            
            # It then creates an array of nodes by extracting the unique values from the atlas file and removing the value 0. 
            # The code then creates an empty array of data with the same shape as the atlas file.    
            # It then iterates over the nodes, and if the node is not in the list of subcortical regions, it assigns the corresponding
            # value in the scalar array to the data array.    
            nodes = np.unique(atlas_file)
            nodes = np.delete(nodes,0)
            data = np.zeros(atlas_file.shape, dtype=np.float32)
            for i,n in enumerate(nodes):
                if n in subcorticalshen:
                    continue
                data[atlas_file == n] = scalar[i]
                
            sample_img = nib.load(os.path.join(atlas_dir, 'shen268_MNI1mm_dil1.nii.gz'))
            save_file = os.path.join(results_path, analysis_id, '{}_{}_{}_{}_{}_crossval{}_{}_surfacefile_betas.nii.gz'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
            
            # store nifti header info for saving file
            save_img = nib.Nifti1Image(data, sample_img.affine, sample_img.header)
            
            save_img.set_data_dtype(data.dtype)
            
            nib.save(save_img, save_file) 
            
            filename = save_file
            surf_prefix = filename.replace('.nii.gz', '')
            
            for hemi in ['L', 'R']: 
                os.chdir(wbpath)
                cmd = './wb_command' + ' -volume-to-surface-mapping '+  filename + ' ' + hcp_dir + '/S1200.' + hemi + '.midthickness_MSMAll.32k_fs_LR.surf.gii '+ surf_prefix + hemi + '.shape.gii -enclosing'
                os.system(cmd)


            os.remove(surf_prefix + '.nii.gz')
            
            
            # fs86 parcellation - subcortical volume ------------
            os.chdir('/home/ubuntu/enigma/motor_predictions/wb_files/workbench_ubuntu')

            roivol = nib.load(os.path.join(atlas_dir, 'shen268_MNI1mm_dil1.nii.gz'))
            Vroi = roivol.get_fdata()
            Vnew = np.zeros(Vroi.shape)
            roidata = np.genfromtxt( textfile, dtype = "float32", delimiter = ',', usecols = 0)

            for i,v in enumerate(np.unique(Vroi[Vroi>0])):
                Vnew[Vroi == v] = roidata[i]
            imgnew = nib.Nifti1Image(Vnew, affine = roivol.affine, header = roivol.header)
            
            nib.save(imgnew, "subcortical_volumes.nii.gz")
            datapath =  "subcortical_volumes.nii.gz"
            newdata = nib.load("subcortical_volumes.nii.gz")
            
            cc400 = nib.load(os.path.join(atlas_dir, 'shen268_MNI1mm_dil1.nii.gz'))
            atlas2 = nib.load(os.path.join(atlas_dir, 'shen268_MNI1mm_dil1_subcort.nii'))
            
            atlas1=nibabel.processing.resample_from_to(atlas2, cc400, order=0)
            
            V400 = cc400.get_fdata()
            V1 = atlas1.get_fdata()
            
            subcortvals = np.unique(V400[(V400>0) * (V1>0)])
            V400_subcort = V400 * np.isin(V400,subcortvals)
                   
            imgdata = newdata.get_fdata()            
            Vnew = np.double(imgdata*(V400_subcort>0))
            
            cc400.header.set_data_dtype(np.float64)  # without this the visualization breaks. LOVE IT!
            
            newdata_subcort=nib.Nifti1Image(Vnew, affine=cc400.affine, header=cc400.header)

            save_file = os.path.join(results_path, analysis_id ,'{}_{}_{}_{}_{}_crossval{}_{}_subcortical_betas_file.nii.gz'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))

            nib.save(newdata_subcort, save_file)
    
def generate_wb_figures_setup(hcp_dir, scenesdir):
    # update MNI volumetric template path (rel path stored in wb)
    # Read in the file
    with open(os.path.join(scenesdir, 'subcort_scene.scene'), "r") as f:
        scenefile = f.read()
        scenefile = scenefile.replace("HCP_S1200_GroupAvg_v1/","")
        scenefile = scenefile.replace('S1200_AverageT1w_restore.nii.gz',os.path.join(hcp_dir,'S1200_AverageT1w_restore.nii.gz'))
    # Write the file out again
    with open(os.path.join(scenesdir, 'subcort_scene.scene'), 'w') as f:
        f.write(scenefile)
        
    # update midthickness surface template path (rel path stored in wb)
    # Read in the file
    with open(os.path.join(scenesdir, 'landscape_surfaces.scene'), "r") as f:
        scenefile = f.read()
        scenefile = scenefile.replace("HCP_S1200_GroupAvg_v1/","")

        scenefile = scenefile.replace("S1200.L.inflated_MSMAll.32k_fs_LR.surf.gii",os.path.join(hcp_dir, "S1200.L.inflated_MSMAll.32k_fs_LR.surf.gii"))
        scenefile = scenefile.replace("S1200.R.inflated_MSMAll.32k_fs_LR.surf.gii",os.path.join(hcp_dir, "S1200.R.inflated_MSMAll.32k_fs_LR.surf.gii"))
        scenefile = scenefile.replace('shen268_normed_motor_scores_chacovol_chronic_ridge_crossval1_meanfeatureweight_allperms_50_surfacefileL.shape.gii', 'surfL.gii')
        
        scenefile = scenefile.replace('shen268_normed_motor_scores_chacovol_chronic_ridge_crossval1_meanfeatureweight_allperms_50_surfacefileR.shape.gii', 'surfR.gii')
    
    # Write the file out again
    with open(os.path.join(scenesdir, 'landscape_surfaces_edit.scene'), 'w') as f:
        f.write(scenefile)

        
    with open(os.path.join(scenesdir, 'dorsal_surfaces.scene'), "r") as f:
        scenefile = f.read()
        scenefile = scenefile.replace("HCP_S1200_GroupAvg_v1/","")

        scenefile = scenefile.replace("S1200.L.inflated_MSMAll.32k_fs_LR.surf.gii",os.path.join(hcp_dir, "S1200.L.inflated_MSMAll.32k_fs_LR.surf.gii"))
        scenefile = scenefile.replace("S1200.R.inflated_MSMAll.32k_fs_LR.surf.gii",os.path.join(hcp_dir, "S1200.R.inflated_MSMAll.32k_fs_LR.surf.gii"))
        scenefile = scenefile.replace('surfmetadataL.shape.gii', 'surfL.gii')
        
        scenefile = scenefile.replace('surfmetadataR.shape.gii', 'surfR.gii')
    # Write the file out again
    with open(os.path.join(scenesdir, 'dorsal_surfaces.scene'), 'w') as f:
        f.write(scenefile) 
    #these are the scene templates that will be used to create figures for the shen/fs feature weights.


def generate_wb_figures(atlas, results_path, analysis_id, y_var,chaco_type, subset, model_tested,crossval,scenesdir, wbpath):
    
    textfiles_betas = ['meanbetas_allperms_0','meanbetas_allperms_50', 'meanbetas_allperms_90', 'meanbetas_allperms_99']

    for file in textfiles_betas:

        subcortical_file = os.path.join(results_path, analysis_id,'{}_{}_{}_{}_{}_crossval{}_{}_subcortical_betas_file.nii.gz'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
        surface_fileR = os.path.join(results_path, analysis_id,'{}_{}_{}_{}_{}_crossval{}_{}_surfacefile_betasR.shape.gii'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
        surface_fileL = os.path.join(results_path, analysis_id, '{}_{}_{}_{}_{}_crossval{}_{}_surfacefile_betasL.shape.gii'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
        
        # because workbench is sooo intuitive, palette/visualization settings are stored in the nifti/gifti metadata!
        # have to rewrite the nifti files with nifti header info derived from manually setting the palette in workbench.
        niftimeta = nib.load(os.path.join(scenesdir, 'niftimetadata.nii.gz'))

        newsubcortfile = nib.Nifti1Image(nib.load(subcortical_file).get_fdata(), niftimeta.affine, niftimeta.header)
        nib.save(newsubcortfile, subcortical_file)
        
        #workbench changes the dataarray metadata.
        # keep the metadata for reference gifti, replace with data from actual feature file
        giftimetaR = nib.load(os.path.join(scenesdir, 'surfmetadataR.shape.gii')) # reference gifti
        giftimetaR.darrays[0].data = nib.load(surface_fileR).darrays[0].data
        newgifti = nib.gifti.gifti.GiftiImage(header=giftimetaR.header, extra=None, file_map = giftimetaR.file_map, labeltable=giftimetaR.labeltable, darrays=giftimetaR.darrays, meta = giftimetaR.meta, version='1.0')
        nib.save(newgifti, surface_fileR)
        giftimetaL = nib.load(os.path.join(scenesdir,'surfmetadataL.shape.gii')) # reference gifti
        giftimetaL.darrays[0].data = nib.load(surface_fileL).darrays[0].data
        newgifti = nib.gifti.gifti.GiftiImage(header=giftimetaL.header, extra=None, file_map = giftimetaL.file_map, labeltable=giftimetaL.labeltable, darrays=giftimetaL.darrays, meta = giftimetaL.meta, version='1.0')
        nib.save(newgifti, surface_fileL)

                
        # make copy of the scenes file that we modify for each figure.
        shutil.copy(os.path.join(scenesdir,'subcort_scene_edit.scene'), os.path.join(results_path,analysis_id,'subcortical_scene.scene'))
        shutil.copy(os.path.join(scenesdir,'landscape_surfaces_edit.scene'), os.path.join(results_path,analysis_id,'surfaces_scene.scene')) 
        shutil.copy(os.path.join(scenesdir,'dorsal_surface_edit.scene'), os.path.join(results_path,analysis_id,'dorsalsurfaces_scene.scene')) 

        # replace volume/surface files with specific results files.
        with open(os.path.join(results_path, analysis_id, 'subcortical_scene.scene'), "r") as f:
            scenefile = f.read()
            scenefile = scenefile.replace('subcortical_volumes.nii.gz',subcortical_file)
        with open(os.path.join(results_path, analysis_id, 'subcortical_scene.scene'), 'w') as f:
            f.write(scenefile)
            
        with open(os.path.join(results_path, analysis_id, 'surfaces_scene.scene'), "r") as f:
            scenefile = f.read()
            scenefile = scenefile.replace('surfL.gii',surface_fileL)
            scenefile = scenefile.replace('surfR.gii',surface_fileR)
        with open(os.path.join(results_path, analysis_id, 'surfaces_scene.scene'), 'w') as f:
            f.write(scenefile)
        
            
        with open(os.path.join(results_path, analysis_id, 'dorsalsurfaces_scene.scene'), "r") as f:
            scenefile = f.read()
            scenefile = scenefile.replace('surfL.gii',surface_fileL)
            scenefile = scenefile.replace('surfR.gii',surface_fileR)
        with open(os.path.join(results_path, analysis_id, 'dorsalsurfaces_scene.scene'), 'w') as f:
            f.write(scenefile)   
            
        
        # subcortical scene
        
        figurefile = os.path.join(results_path, analysis_id, '{}_{}_{}_{}_{}_crossval{}_{}_subcortical_betas_fig.png'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
        scenefile = os.path.join(results_path, analysis_id,'subcortical_scene.scene')
        print('Generating workbench figures:\n {}'.format(figurefile))
        os.system('bash {}/wb_command -show-scene {} 1 {} 1500 300'.format(wbpath, scenefile, figurefile))
            
        # surface scene2
        
        figurefile = os.path.join(results_path, analysis_id, '{}_{}_{}_{}_{}_crossval{}_{}_surfaces_betas_fig.png'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
        scenefile = os.path.join(results_path, analysis_id,'surfaces_scene.scene')
        print('Generating workbench figures:\n {}'.format(figurefile))
        os.system('bash {}/wb_command -show-scene {} 1 {} 1300 900'.format(wbpath, scenefile, figurefile))
        

        figurefile = os.path.join(results_path, analysis_id, '{}_{}_{}_{}_{}_crossval{}_{}_dorsalsurfaces_betas_fig.png'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))
        scenefile = os.path.join(results_path, analysis_id,'dorsalsurfaces_scene.scene')
        print('Generating workbench figures:\n {}'.format(figurefile))
        os.system('bash {}/wb_command -show-scene {} 1 {} 10000 1300'.format(wbpath, scenefile, figurefile))
        
    
    # smatt files:
    surface_fileR = os.path.join(results_path, analysis_id, '{}_{}_{}_{}_{}_crossval{}_{}_surfacefile_betasR.shape.gii'.format(atlas, y_var, chaco_type, subset, model_tested,crossval, file))

        
def generate_smatt_ll_figures(results_path,analysis_id, output_path, atlas, y_var, chaco_type, subset, model_tested, crossval):
    title=''
    rootname_truepred = os.path.join(results_path, output_path, '{}_{}_{}_{}_{}_crossval{}'.format(atlas, y_var, chaco_type, subset, model_tested,crossval))
    meanfeatureweights = np.loadtxt(os.path.join(rootname_truepred, '_meanfeatureweight_allperms.txt'))
    meanbetas= np.loadtxt(os.path.join(rootname_truepred, '_meanbetas_allperms.txt'))
    stdbetas = np.loadtxt(os.path.join(rootname_truepred, '_stdbetas_allpearms.txt'))
    betas = np.loadtxt(os.path.join(rootname_truepred, '_betas.txt'))
    
    # Change the colour of the boxes to match the SMATT figure.
    m1 = (89/255, 196/255, 89/255) # green
    s1 = (228/255, 212/255, 74/255) # yellow
    pmd = (219/255, 100/255, 221/255) # pink
    pmv = (236/255, 152/255, 81/255) # orange
    sma = (76/255, 73/255, 231/255) # blue
    psma = (221/255, 52/255, 50/255) # red
    
    if atlas == 'lesionload_all':
        xticklabels = ['M1','PMd','PMv','S1','SMA','preSMA']
        colors = (m1, pmd, pmv, s1, sma, psma)
        xsize= [0, 1, 2, 3, 4, 5]
    elif atlas == 'lesionload_all_2h':
        xticklabels = ['L-M1','L-PMd','L-PMv','L-S1','L-SMA','L-preSMA','R-M1','R-PMd','R-PMv','R-S1','R-SMA','R-preSMA']
        colors = (m1, pmd, pmv, s1, sma, psma,m1, pmd, pmv, s1, sma, psma)
        xsize = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    
    # plot untransformed betra coefficitsn
    data2 = betas
    
    path_file = os.path.join(results_path, analysis_id, analysis_id + '_' + atlas + '_' + subset + '_crossval' + crossval +  '_smatt_betas.png')
    ylabel = 'Beta coefficients'
    fig, ax = plt.subplots(ncols=1, figsize =(7, 7))
    
    bp = ax.boxplot(data2, widths=0.6, patch_artist=True)
    # Graph title
    ax.set_title(title,fontname="Arial", fontsize=16)
    # Label y-axis
    ax.set_ylabel(ylabel,fontname="Arial", fontsize=16)
    # Label x-axis ticks
    
    ax.set_xticklabels(xticklabels,rotation=90,fontname="Arial", fontsize=18)
    
    # Change y-tick fontsize
    ax.tick_params(axis='y', labelsize=16)
    #ax.set_yticklabels(yticklabs,rotation=90,fontname="Arial", fontsize=18)

    # Hide x-axis major ticks
    ax.tick_params(axis='x', which='major', length=0)
    # Show x-axis minor ticks
    xticks = [0.5] + [x + 0.5 for x in ax.get_xticks()]
    ax.set_xticks(xticks, minor=True)
    # Clean up the appearance
    ax.tick_params(axis='x', which='minor', length=3, width=1)

    # Change the colour of the boxes to Seaborn's 'pastel' palette
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_edgecolor(color)
    
    plt.setp(bp['medians'], color='k')
 
    # Colour of the median lines
    
       
    plt.savefig(path_file, bbox_inches ='tight')
    