# Makefile
# authors: Lincoln Harris
# date: 10.11.18

# test_tracer -- run tracer pipeline, just on a single cell
#
test_tracer:
	reflow run tracer_pipeline.rf -input_fq1 s3://darmanis-group/singlecell_lungadeno/immuneCells_9.27/170125/A10_1001000293/A10_1001000293_S85_R1_001.fastq.gz -input_fq2 s3://darmanis-group/singlecell_lungadeno/immuneCells_9.27/170125/A10_1001000293/A10_1001000293_S85_R2_001.fastq.gz -sample_id A10_1001000293 -output_dir s3://darmanis-group/singlecell_lungadeno/immuneCells_9.27/trinity_out/ -threads 4

test_tracer1:
	reflow run tracer_pipeline.rf -input_fq1 s3://darmanis-group/singlecell_lungadeno/immuneCells_9.27/170125/A11_1001000293/A11_1001000293_S86_R1_001.fastq.gz -input_fq2 s3://darmanis-group/singlecell_lungadeno/immuneCells_9.27/170125/A11_1001000293/A11_1001000293_S86_R2_001.fastq.gz -sample_id A11_1001000293 -output_dir s3://darmanis-group/singlecell_lungadeno/immuneCells_9.27/trinity_out/ -threads 4

test_tracer2:
	reflow runbatch 