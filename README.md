# Data import script for ORG.one project

1. Install requirements
```shell
pip install -r requirements.txt
```

2. Run script
```shell
python data_import.py
```

This script collects samples from BioSamples that have project field equals to 
ORG.one or AORG.ONE (parameters in get requests are case-sensitive). Then for
every BioSample id: 
1. script creates directory (if it doesn't exist), 
2. downloads metadata information in JSON format (if it doesn't exist)
3. Check for experiments and downloads fast.gz files (if it doesn't exist)
4. Check for assemblies and downloads .dat.gz, fasta.gz and 
5. sequence_report.txt (if it doesn't exist)