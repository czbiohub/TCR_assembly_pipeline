# Makefile
# authors: Lincoln Harris
# date: 10.11.18

# test_tracer -- run tracer pipeline, just on a single cell
#
test:
	reflow run tracer_pipeline.rf -input_fq1 s3://darmanis-group/singlecell_lungadeno/rawdata/fastq_all/rename/A10_1001000293_R1.fastq.gz -input_fq2 s3://darmanis-group/singlecell_lungadeno/rawdata/fastq_all/rename/A10_1001000293_R2.fastq.gz -sample_id A10_1001000293 -output_dir s3://darmanis-group/singlecell_lungadeno/immune/immune_fastqs_9.27/trinity_out/A10_1001000293/ -threads 4

test1:
	reflow run tracer_pipeline.rf -input_fq1 s3://darmanis-group/singlecell_lungadeno/rawdata/fastq_all/rename/A11_1001000293_R1.fastq.gz -input_fq2 s3://darmanis-group/singlecell_lungadeno/rawdata/fastq_all/rename/A11_1001000293_R2.fastq.gz -sample_id A11_1001000293 -output_dir s3://darmanis-group/singlecell_lungadeno/immune/immune_fastqs_9.27/trinity_out/A11_1001000293/ -threads 4
 
