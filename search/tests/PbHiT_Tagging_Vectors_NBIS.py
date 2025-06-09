#!/usr/bin/env python
# coding: utf-8

# In[14]:


#Load Libraries/modules
from Bio import SeqUtils
from Bio import SeqIO
import pandas as pd
#import matplotlib.pyplot as plt
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import numpy as np
from random import randint
#get_ipython().run_line_magic('matplotlib', 'inline')


# In[15]:


#Set standard elements of the gRNA oligo into items
BbsI = 'GAAGACggTATT'
Scaffold = 'GTTTTAGAGCTAGAAATAGCAAGTTAAAATAAGGCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC'
AvrII = 'CCTAGG'
PstI = 'CTGCAG'


# In[16]:


#Read gRNA excel files as table

# Load the Excel file, reading only columns A to C
gRNA_EuPaGDT_tag_top = pd.read_excel(
    "./resources/tag/all_gRNA.CRISPR_tagging_250bp.xlsx",
    index_col=None,
    na_values=['NA'],
    usecols="A:C"
)

# Split 'gRNA_id' into 'GENE ID', 'gRNA ID', and 'directionality'
split_cols = gRNA_EuPaGDT_tag_top['gRNA_id'].str.split("_", expand=True)
split_cols.columns = ['GENE ID', 'gRNA ID', 'directionality']

# Drop the original 'gRNA_id' column and add the new columns
gRNA_EuPaGDT_tag_top.drop(columns=['gRNA_id'], inplace=True)
gRNA_EuPaGDT_tag_top = pd.concat([gRNA_EuPaGDT_tag_top, split_cols], axis=1)

# Optional: clean up 'GENE ID' format
gRNA_EuPaGDT_tag_top['GENE ID'] = gRNA_EuPaGDT_tag_top['GENE ID'].str.replace('PBANKA', 'PBANKA_', regex=True)

# Preview result
gRNA_EuPaGDT_tag_top.head(5)


# In[17]:


def duplication_status_check(row):
    sequence = Seq(row['Oligo Sequence'])
    segments = [
        AvrII,
        PstI,
        BbsI,
    ]
    return sum(
        sequence.count_overlap(segment)
        for segment in segments
    ) == 3


# In[18]:


#Create a DataFrame that has the Gene ID, HR1, and HR2 

#Read HR1 FASTA file 
HR1_fasta = "./resources/tag/PbHiT_Tag_HR1.fasta"
HR1_seq= [i for i in SeqIO.parse(HR1_fasta,'fasta')]

#Store HR1 sequences into a string
genes = []
HR1_seq = []
for seq_record in SeqIO.parse(HR1_fasta,'fasta'):
    genes.append(seq_record.id)
    HR1_seq.append(str(seq_record.seq))

#to see items in a FASTA file 
#PBANKA1 = HR1_seq[0]
#print (PBANKA1)

#Read HR2 FASTA file 
HR2_fasta = "./resources/tag/PbHiT_Tag_HR2.fasta"
HR2_seq= [i for i in SeqIO.parse(HR2_fasta,'fasta')]

#Store HR2 sequences into a string 
genes = []
HR2_seq = []

for seq_record in SeqIO.parse(HR2_fasta,'fasta'):
    genes.append(seq_record.id)
    HR2_seq.append(str(seq_record.seq))

#Read HR2 Rev FASTA file 
HR2_fasta_rev = "./resources/tag/PbHiT_Tagging_HR2_Final_rev_comp.fasta"
HR2_seq_rev= [i for i in SeqIO.parse(HR2_fasta_rev,'fasta')]

#Store HR2 sequences into a string 
genes = []
HR2_seq_rev = []

for seq_record in SeqIO.parse(HR2_fasta_rev,'fasta'):
    genes.append(seq_record.id)
    HR2_seq_rev.append(str(seq_record.seq))

#Generate table with Genes, HR1, HR2

pHIT_Tag_HR = pd.DataFrame({
    "GENE ID": genes,
    "HR1 Sequence":HR1_seq,
    "HR2 Sequence":HR2_seq,
    "HR2 Sequence Rev": HR2_seq_rev,
})

pHIT_Tag_HR.head(5)
#df0=pHIT_Tag_HR
#df0.to_csv("./resources/PbHiT_test.csv")


# In[19]:


#Create data frame with HR1 HR2 and gRNA merged

def merge_dataframes(df1, df2, common_column, how='inner'):
    # Merge the two dataframes on the common column
    merged_df = pd.merge(df1, df2, on=common_column, how=how)
    return merged_df

df1=pHIT_Tag_HR
df2=gRNA_EuPaGDT_tag_top
#df2=gRNA_EuPaGDT_tag_all

merged_df = merge_dataframes(df1, df2, common_column='GENE ID', how='inner')

PbHiT_Tagging_Merge=pd.DataFrame(merged_df)

columns_to_convert = ['gRNA_sequence', 'HR1 Sequence', 'HR2 Sequence','HR2 Sequence Rev']
PbHiT_Tagging_Merge[columns_to_convert] = PbHiT_Tagging_Merge[columns_to_convert].fillna("").astype(str)

PbHiT_Tagging_Merge[columns_to_convert] = PbHiT_Tagging_Merge[columns_to_convert].astype(str)

#PbHiT_Tagging_Merge.head(10)


# In[20]:


# Extract HR2 sequence in data frame forward sequences

def extract_sequence(row, search_column, target_column, extract_length=100):
    search_pattern = row[search_column]
    target_sequence = row[target_column]

    # Find the position of the search pattern in the target sequence
    position = target_sequence.find(search_pattern)

    if position != -1:
        # Extract 100 characters after the search pattern
        start_position = position + 6 + len(search_pattern)
        return target_sequence[start_position:start_position + extract_length]

    else:
        return ''  # Return an empty string if the pattern is not found

# Use apply to perform the search and extract operation
PbHiT_Tagging_Merge['Extracted_Sequence_Fw'] =PbHiT_Tagging_Merge.apply(extract_sequence, axis=1, search_column='gRNA_sequence', target_column='HR2 Sequence')
PbHiT_HR1_Final_Fw=PbHiT_Tagging_Merge.copy()

#PbHiT_HR1_Final_Fw.head(5)
#df.to_excel("./resources/PbHiT_HR1_Final_test6.xlsx")


# In[21]:


# Extract HR2 Sequence in data frame reverse sequences
def extract_sequence_before(row, search_column, target_column, extract_length=100):
    search_pattern = row[search_column]
    target_sequence = row[target_column]

    # Find the position of the search pattern in the target sequence
    position = target_sequence.find(search_pattern)

    if position != -1:
        # Extract 100 characters before the search pattern
        start_position = max(0, position - extract_length)
        return target_sequence[start_position:position]

    else:
        return ''  # Return an empty string if the pattern is not found

# Use apply to perform the search and extract operation

PbHiT_Tagging_Merge['Extracted_Sequence_Rev'] = PbHiT_Tagging_Merge.apply(extract_sequence_before, axis=1, search_column='gRNA_sequence', target_column='HR2 Sequence Rev')
PbHiT_HR1_Final_Rev=PbHiT_Tagging_Merge.copy()

PbHiT_HR1_Final_Rev.head(5)

#PbHiT_HR1_Final_Rev.to_excel("./resources/PbHiT_HR1_Final_Rev.xlsx")


# In[22]:


# Merge 2 data frames on the single Extracted sequence single column 


# Merge the two DataFrames on two common columns (e.g., 'column1' and 'column2')
PbHiT_HR1_merge = pd.merge(PbHiT_HR1_Final_Fw, PbHiT_HR1_Final_Rev, on=['GENE ID','HR1 Sequence','HR2 Sequence','HR2 Sequence Rev','gRNA_sequence','Total_score','gRNA ID','directionality'], how='inner') 
# Save the merged DataFrame to a new CSV file
#PbHiT_HR1_merge.to_csv('merged_output.csv', index=False)

PbHiT_HR1_merge.head(20)


# In[23]:


#Convert Extracted Sequence y into Reverse complement

PbHiT_HR1_merge['Extracted_Sequence_Rev'] = PbHiT_HR1_merge['Extracted_Sequence_Rev'].apply(
    lambda seq: str(Seq(str(seq).strip().upper()).reverse_complement())
)

PbHiT_HR1_merge.head(20)


# In[26]:


# Concatenate the Extracted sequence column


PbHiT_HR1_merge['HR2_Tag'] = PbHiT_HR1_merge['Extracted_Sequence_Fw_x'].fillna('') + PbHiT_HR1_merge['Extracted_Sequence_Rev']
#PbHiT_HR1_merge.to_csv('merged_HR1_test.csv', index=False)
PbHiT_HR1_merge.head(10)
#PbHiT_HR1_merge.to_excel("./resources/PbHiT_Tagging_merge_Data.head.xlsx")


# In[27]:


#Search + Assemble Oligo BbsI and gRNA

#Convert to batch search
#gene_list=['PBANKA_1112300']
#rows=len(gene_list)
#dftest=pd.DataFrame()

#gene_list=['PBANKA_0825900']

#for x in gene_list:
#        input_gene=x
#        gene_gRNA=PbHiT_HR1_merge[PbHiT_HR1_merge['GENE ID']==input_gene]
#        if not gene_gRNA.empty:
#            Result1= BbsI + gene_gRNA['gRNA_sequence']+ Scaffold + gene_gRNA['HR2_Tag'] + AvrII + gene_gRNA['HR1 Sequence'] + PstI
#            print(Result1)
#        else:
#            print('No gRNA')
#
 #Convert Result2 into a list
#        PbHiT_Tag_constructs=Result1.values.tolist()
#
 #Generate final oligo list
#
#PbHiT_Tag_Vector_List=pd.DataFrame()
#PbHiT_Tag_Vector_List['GENE ID']=gene_gRNA['GENE ID']
#PbHiT_Tag_Vector_List['Oligo Sequence']=PbHiT_Tag_constructs


        #PbHiT_Tag_Vector_List=pd.DataFrame(gene_gRNA['GENE ID'], PbHiT_Tag_constructs, columns=['GENE ID', 'Oligo Sequence'])
        #PbHiT_Tag_Vector_List['GENE ID']=gene_gRNA['GENE ID']
        #PbHiT_Tag_Vector_List['Oligo Sequence']= PbHiT_Tag_constructs

#PbHiT_Tag_Vector_List.head(10)
#PbHiT_Tag_Vector_List.to_excel("./resources/Desktop/PbHiT_Tagging_test_PBANKA_093230.xlsx")


# In[28]:


# Define the list of gene IDs to process
#gene_list = ['PBANKA_0825900', 'PBANKA_0826100','PBANKA_0826200']  # Add as many genes as needed
def get_sequence_list(gene_list):
    # Filter only the genes of interest from the full dataset
    filtered_df = PbHiT_HR1_merge[PbHiT_HR1_merge['GENE ID'].isin(gene_list)].copy()

    if filtered_df.empty:
        raise RuntimeError(f'No tagging construct found: No gRNA found for: {gene_list}')

    # Drop rows with any missing required sequence data
    required_columns = ['GENE ID', 'gRNA_sequence', 'HR2_Tag', 'HR1 Sequence']
    filtered_df.dropna(subset=required_columns, inplace=True)

    # Construct the oligo by concatenating parts
    filtered_df['Oligo Sequence'] = (
        BbsI +
        filtered_df['gRNA_sequence'].astype(str) +
        Scaffold +
        filtered_df['HR2_Tag'].astype(str) +
        AvrII +
        filtered_df['HR1 Sequence'].astype(str) +
        PstI
    )

    # Final oligo list
    PbHiT_Tag_Vector_List = filtered_df[['GENE ID', 'Oligo Sequence']].reset_index(drop=True)


    # Preview and save

    #PbHiT_Tag_Vector_List.head(10)
    #PbHiT_Tag_Vector_List.to_excel("./resoruces/PbHiT_Tagging_test_June6_rev.xlsx", index=False)

    #Checks
    status = PbHiT_Tag_Vector_List.apply(duplication_status_check, axis=1)
    new_row = PbHiT_Tag_Vector_List[status]

    if len(new_row) == 0:
        raise RuntimeError(f'No valid sequences: {gene_list}')

    return new_row.head(3)


    # In[ ]:



