#!/usr/bin/env python
# coding: utf-8

#Load Libraries/modules
from Bio import SeqUtils
from Bio import SeqIO
import pandas as pd
import matplotlib.pyplot as plt
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import numpy as np
from random import randint
get_ipython().run_line_magic('matplotlib', 'inline')


#Set standard elements of the gRNA oligo into items
BbsI = 'GAAGACggTATT'
Scaffold = 'GTTTTAGAGCTAGAAATAGCAAGTTAAAATAAGGCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC'
AvrII = 'CCTAGG'
PstI = 'CTGCAG'


#Read gRNA excel files as table

#this file has top 3 gRNAs for each gene, read only until column C 'Total_score'
gRNA_EuPaGDT_tag_top = pd.read_excel("./resources/selected_gRNA.CRISPR_tagging.xlsx",index_col=None, na_values=['NA'], usecols="A:C")
gRNA_EuPaGDT_tag_top[['GENE ID', 'gRNA ID','directionality']] = gRNA_EuPaGDT_tag_top.gRNA_id.str.split("_", expand = True)
#gRNA_EuPaGDT_tag_top.rename(columns={'gRNA_id':'GENE ID'}, inplace = True)
gRNA_EuPaGDT_tag_top['GENE ID']=gRNA_EuPaGDT_tag_top['GENE ID'].replace('PBANKA','PBANKA_', regex= True)

#gRNA_EuPaGDT_tag_top.head(5)

#this file has all gRNAs for each gene, read only until column C 'Total_score'
#gRNA_EuPaGDT_tag_all = pd.read_excel("./resources/PbHiT_Tagging_Vector_Final/all_gRNA.CRISPR_tagging.xlsx",index_col=None, na_values=['NA'], usecols="A:C")
#gRNA_EuPaGDT_tag_all[['GENE ID', 'gRNA ID','directionality']] = gRNA_EuPaGDT_tag_all.gRNA_id.str.split("_", expand = True)
#gRNA_EuPaGDT_tag_all.rename(columns={'gRNA_id':'GENE ID'}, inplace = True)
#gRNA_EuPaGDT_tag_all['GENE ID']=gRNA_EuPaGDT_tag_all['GENE ID'].replace('PBANKA','PBANKA_', regex= True)

#gRNA_EuPaGDT_tag_all.head(5) 


#Create a DataFrame that has the Gene ID, HR1, and HR2 

#Read HR1 FASTA file 
HR1_fasta = "./resources/PbHiT_Tagging_HR1_Final.fasta"
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
HR2_fasta = "./resources/PbHiT_Tagging_HR2_Final.fasta"
HR2_seq= [i for i in SeqIO.parse(HR2_fasta,'fasta')]

#Store HR2 sequences into a string 
genes = []
HR2_seq = []

for seq_record in SeqIO.parse(HR2_fasta,'fasta'):
    genes.append(seq_record.id)
    HR2_seq.append(str(seq_record.seq))
    
#Read HR1_rev FASTA file 
HR1_fasta_rev = "./resources/PbHiT_Tagging_HR1_Final_rev_comp.fasta"
HR1_seq_rev= [i for i in SeqIO.parse(HR1_fasta_rev,'fasta')]

#Store HR1 sequences into a string
genes = []
HR1_seq_rev = []
for seq_record in SeqIO.parse(HR1_fasta_rev,'fasta'):
    genes.append(seq_record.id)
    HR1_seq_rev.append(str(seq_record.seq))
    
#to see items in a FASTA file 
#PBANKA1 = HR1_seq[0]
#print (PBANKA1)

#Read HR2 FASTA file 
HR2_fasta_rev = "./resources/PbHiT_Tagging_HR2_Final_rev_comp.fasta"
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
    "HR1 Sequence Rev": HR1_seq_rev,
    "HR2 Sequence Rev": HR2_seq_rev,
})

pHIT_Tag_HR.head(5)
#df0=pHIT_Tag_HR
#df0.to_csv("./resources/PbHiT_test.csv")


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
PbHiT_Tagging_Merge.head(10)


# Extract HR1 sequence in data frame forward sequences

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
PbHiT_Tagging_Merge['Extracted_Sequence'] =PbHiT_Tagging_Merge.apply(extract_sequence, axis=1, search_column='gRNA_sequence', target_column='HR1 Sequence')
PbHiT_HR1_Final_Fw=PbHiT_Tagging_Merge.copy()

#PbHiT_HR1_Final_Fw.head(5)
#df.to_excel("./resources/PbHiT_HR1_Final_test6.xlsx")


# Extract HR1 Sequence in data frame reverse sequences
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

PbHiT_Tagging_Merge['Extracted_Sequence'] = PbHiT_Tagging_Merge.apply(extract_sequence_before, axis=1, search_column='gRNA_sequence', target_column='HR1 Sequence Rev')
PbHiT_HR1_Final_Rev=PbHiT_Tagging_Merge.copy()

#PbHiT_HR1_Final_Rev.head(5)

#PbHiT_HR1_Final_Rev.to_excel("./resources/PbHiT_HR1_Final_Rev.xlsx")


# Merge 2 data frames on the single Extracted sequence single column 


# Merge the two DataFrames on two common columns (e.g., 'column1' and 'column2')
PbHiT_HR1_merge = pd.merge(PbHiT_HR1_Final_Fw, PbHiT_HR1_Final_Rev, on=['GENE ID','HR1 Sequence','HR2 Sequence','HR1 Sequence Rev','HR2 Sequence Rev','gRNA_id','gRNA_sequence','Total_score','gRNA ID','directionality'], how='inner') 
# Save the merged DataFrame to a new CSV file
PbHiT_HR1_merge.to_csv('merged_output.csv', index=False)

PbHiT_HR1_merge.head(20)


# Concatenate the Extracted sequence column


PbHiT_HR1_merge['HR1_Tag'] = PbHiT_HR1_merge['Extracted_Sequence_x'].fillna('') + PbHiT_HR1_merge['Extracted_Sequence_y']
#PbHiT_HR1_merge.to_csv('merged_HR1_test.csv', index=False)
PbHiT_HR1_merge.head(10)


#Search + Assemble Oligo BbsI and gRNA

#Convert to batch search
#gene_list=['PBANKA_1112300']
#rows=len(gene_list)
#dftest=pd.DataFrame()

gene_list=['PBANKA_1112300']

for x in gene_list:
        input_gene=x
        gene_gRNA=PbHiT_HR1_merge[PbHiT_HR1_merge['GENE ID']==input_gene]
        if not gene_gRNA.empty:
            Result1= BbsI + gene_gRNA['gRNA_sequence']+ Scaffold + gene_gRNA['HR1_Tag'] + AvrII + gene_gRNA['HR2 Sequence'] + PstI
            print(Result1)
        else:
            print('No gRNA')
            
 #Convert Result2 into a list
        PbHiT_Tag_constructs=Result1.values.tolist()
    
 #Generate final oligo list

PbHiT_Tag_Vector_List=pd.DataFrame()
PbHiT_Tag_Vector_List['GENE ID']=gene_gRNA['GENE ID']
PbHiT_Tag_Vector_List['Oligo Sequence']=PbHiT_Tag_constructs

        
PbHiT_Tag_Vector_List.head(10)
PbHiT_Tag_Vector_List.to_excel("./resources/PbHiT_Tagging_test.xlsx")

