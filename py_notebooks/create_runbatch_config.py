
#////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////
# script: create_runbatch_config.py
# authors: Olga Botvinnik & Lincoln Harris
# date: 10.11.18
#
# Trying to build the input file to give tracer_pipeline.rf (required for batch mode run)
#		pandas!!
#////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////
import os
import pandas as pd
pd.options.display.max_colwidth = 500 # module config? 
pd.options.mode.chained_assignment = None  # disable warning message? 

# writeFunc()
#	TODO: ADD DESCRIPTION
#
def writeFunc(samples_df):
	import json

	out_dir = '../tracer/test'

	# write samples_df to file
	get_ipython().system(' mkdir -p $out_dir')
	samples_df.to_csv(f'{out_dir}/samples.csv', index=False)

	# write a config file
	config =     {
		"program": "../../reflow/tracer_pipeline.rf",
		"runs_file": "samples.csv"
	}

	with open(f'{out_dir}/config.json', 'w') as f:
		json.dump(config, f)
    
	get_ipython().system(' head -n 3 $out_dir/samples_big.csv $out_dir/config.json')

# get_fastqs_R1()
#      get full s3 paths for fastq file (R1), then add them to a new col in cells_df
# 
def get_fastqs_R1(cell):
	s3_location = f'{prefix}{cell}' #f? 
	lines = get_ipython().getoutput('aws s3 ls $s3_location')
	try:
		fq_line = [x for x in lines if x.endswith('R1_001.fastq.gz')][0] # get the fastq files, specifically
		fq_basename = fq_line.split()[-1]
		return f'{s3_location}{fq_basename}'
	except IndexError:
		return
    
# get_fastqs_R2()
#	get full s3 paths for fastq file (R2), then add them to a new col in cells_df
#
def get_fastqs_R2(cell):
	s3_location = f'{prefix}{cell}' #f? 
	lines = get_ipython().getoutput('aws s3 ls $s3_location')
	try:
		fq_line = [x for x in lines if x.endswith('R2_001.fastq.gz')][0] # get the fastq files, specifically
		fq_basename = fq_line.split()[-1]
		#print(s3_location)
		return f'{s3_location}{fq_basename}'
	except IndexError:
		return

# driver()
#     Gets cell names given a prefix, and sets up dataframe
#
def driver(prefix): 
     
    # get all of the cells in a given run directory
	txt = 'runX_cells.txt'
	get_ipython().system(' aws s3 ls $prefix > $txt')

    # read 180226 cell names into a dataframe
	cells_df = pd.read_table(txt, delim_whitespace=True, header=None, names=['is_prefix', 'cell_name'])

    # applying function, and assigning output to new col in cells_df
	cells_df['input_fq_1'] = cells_df['cell_name'].map(get_fastqs_R1) 

    # applying function, and assigning output to new col in cells_df
	cells_df['input_fq_2'] = cells_df['cell_name'].map(get_fastqs_R2)
    
    # add a sample_id col
	cells_df['sample_id'] = cells_df.cell_name.str.strip('/') # getting rid of the forward slashes
    
    # building the output vcf string
	cells_df['output_prefix'] = 's3://darmanis-group/singlecell_lungadeno/immuneCells_9.27/trinity_out/'
    
    # subset cells_df by only what we want
	cols_to_keep = ['sample_id', 'input_fq_1', 'input_fq_1', 'output_prefix']
	samples_df = cells_df[cols_to_keep]
    
    # rename cols and add ID col
	samples_df.columns = ['sample_id','input_fq1','input_fq2', 'output_dir']
	samples_df['id'] = samples_df['sample_id']

    # rearrange cols
	samples_df = samples_df[['id', 'sample_id', 'input_fq1', 'input_fq2', 'output_dir']]

	return samples_df

# main()
#	TODO: ADD DESCRIPTION
#

bucketPrefixes = 's3://darmanis-group/singlecell_lungadeno/immuneCells_9.27/'
f = 'nonImmune_bams_9.27_prefixes.txt'
get_ipython().system(' aws s3 ls $bucketPrefixes > $f')
    
# read run prefixes into a pandas df
runs_df = pd.read_table(f, delim_whitespace=True, header=None, names=['is_prefix', 'run_name'])
    
# add a full_path col
runs_df['full_path'] = 's3://darmanis-group/singlecell_lungadeno/immuneCells_9.27/' + runs_df['run_name']
    
big_df = pd.DataFrame() # init empty dataframe

for i in range(0, len(runs_df.index)-1):
	global prefix # dont like this
	prefix = runs_df['full_path'][i]
	print(prefix)
	curr_df = driver(prefix)
	toConcat = [big_df, curr_df]
	big_df = pd.concat(toConcat)
	print(big_df.shape)

writeFunc(big_df)

#////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////