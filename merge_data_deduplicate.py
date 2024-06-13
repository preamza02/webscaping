import pandas as pd

file_path = "combined.csv"
df = pd.read_csv(file_path)
df['Disease name (ClinVar Accession)'] =  '' + df['Disease name'].astype(str) +' (' + df['ClinVar Accession'].astype(str) + ')'

del df['ClinVar Accession']
del df['Disease name']
del df['Clinical Significant']
del df['Synonyms']

def combine_and_deduplicate(values):
    unique_values = list(dict.fromkeys(values))
    return ', '.join(map(str, unique_values))

combined_df = df.groupby(['Gene','rsId','Ref','Alt','Effect','Alleles Frequency','Number of citation','Publications','Cytogenetic location','Variant name']).agg({'Clinical Significant': combine_and_deduplicate, 'Disease name (ClinVar Accession)': combine_and_deduplicate}).reset_index()

combined_df.to_csv('cancer_file_final.csv', index=False)