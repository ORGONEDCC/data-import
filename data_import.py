import requests
import os

from lxml import etree

# need to have two urls as some samples projects names might not be consistent
URLS = ['https://www.ebi.ac.uk/biosamples/samples?size=100000&filter='
        'attr%3Aproject%20name%3AORG.one',
        'https://www.ebi.ac.uk/biosamples/samples?size=100000&filter='
        'attr%3Aproject%20name%3AORG.ONE']


def main():
    """
    This function collects data from BioSamples and calls other functions to
    download the data
    """
    for url in URLS:
        samples = requests.get(url).json()
        for sample in samples['_embedded']['samples']:
            parse_sample(sample['accession'])


def parse_sample(sample_id):
    # if directory doesn't exist
    if not os.path.exists(sample_id):
        # create directory with BioSample id name
        os.system(f"mkdir {sample_id}")
        # download metadata in json format
        os.system(
            f"wget -P {sample_id} "
            f"https://www.ebi.ac.uk/biosamples/samples/{sample_id}.json")
    # check for existing experiments
    experiments = get_reads(sample_id)
    for experiment in experiments:
        filename = experiment['fastq_ftp'].split("/")[-1]
        # if file doesn't exist, download it
        if not os.path.exists(f"{sample_id}/{filename}"):
            os.system(f"wget -P {sample_id} ftp://{experiment['fastq_ftp']}")
    # check for existing assemblies
    assemblies = parse_assemblies(sample_id)
    # for every assembly get ftp links on data and download it to directory
    for assembly in assemblies:
        data = requests.get(
            f"https://www.ebi.ac.uk/ena/browser/api/xml/{assembly['accession']}"
        )
        root = etree.fromstring(data.content)
        for link in root.find('ASSEMBLY').find('ASSEMBLY_LINKS').findall(
                'ASSEMBLY_LINK'):
            file_link = link.find('URL_LINK').find('URL').text
            filename = file_link.split("/")[-1]
            if not os.path.exists(f"{sample_id}/{filename}"):
                os.system(f"wget -p {sample_id} {file_link}")


def parse_assemblies(sample_id):
    """
    This function checks for assemblies linked with sample in ENA
    :param sample_id: BioSample id
    :return: list of assemblies linked with this sample
    """
    assemblies_data = requests.get(f"https://www.ebi.ac.uk/ena/portal/api/"
                                   f"links/sample?format=json"
                                   f"&accession={sample_id}&result=assembly"
                                   f"&offset=0&limit=1000")
    if assemblies_data.status_code != 200:
        return list()
    else:
        return assemblies_data.json()


def get_reads(sample_id):
    """
    This function check for raw data linked with sample in ENA
    :param sample_id: BioSample id
    :return: list of experiments linked with this sample
    """
    experiments_data = requests.get(f'https://www.ebi.ac.uk/ena/portal/'
                                        f'api/filereport?result=read_run'
                                        f'&accession={sample_id}'
                                        f'&offset=0&limit=1000&format=json'
                                        f'&fields=study_accession,'
                                        f'secondary_study_accession,'
                                        f'sample_accession,'
                                        f'secondary_sample_accession,'
                                        f'experiment_accession,run_accession,'
                                        f'submission_accession,tax_id,'
                                        f'scientific_name,instrument_platform,'
                                        f'instrument_model,library_name,'
                                        f'nominal_length,library_layout,'
                                        f'library_strategy,library_source,'
                                        f'library_selection,read_count,'
                                        f'base_count,center_name,first_public,'
                                        f'last_updated,experiment_title,'
                                        f'study_title,study_alias,'
                                        f'experiment_alias,run_alias,'
                                        f'fastq_bytes,fastq_md5,fastq_ftp,'
                                        f'fastq_aspera,fastq_galaxy,'
                                        f'submitted_bytes,submitted_md5,'
                                        f'submitted_ftp,submitted_aspera,'
                                        f'submitted_galaxy,submitted_format,'
                                        f'sra_bytes,sra_md5,sra_ftp,sra_aspera,'
                                        f'sra_galaxy,cram_index_ftp,'
                                        f'cram_index_aspera,cram_index_galaxy,'
                                        f'sample_alias,broker_name,'
                                        f'sample_title,nominal_sdev,'
                                        f'first_created')
    if experiments_data.status_code != 200:
        return list()
    else:
        return experiments_data.json()


if __name__ == "__main__":
    main()
