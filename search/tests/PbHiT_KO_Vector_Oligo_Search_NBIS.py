#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


#Set standard elements of the gRNA oligo into items
BbsI = 'GAAGACggTATT'
Scaffold = 'GTTTTAGAGCTAGAAATAGCAAGTTAAAATAAGGCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC'
AvrII = 'CCTAGG'
PstI = 'CTGCAG'


# In[3]:


#Reverse Complement Function 
from Bio.SeqRecord import SeqRecord

def make_rc_record(record):
    """Returns a new SeqRecord with the reverse complement sequence."""
    return SeqRecord(seq = record.seq.reverse_complement(), \
                 id = record.id, \
                 description = "reverse complement")


# In[4]:


#Reverse Complement HR1 and HR2

HR1_fasta = "./resources/corrected_GENE_SEQ_WITH_100_FLANKING_BASES_HR1.fasta"
records = map(make_rc_record, SeqIO.parse(HR1_fasta, "fasta"))
SeqIO.write(records, "./resources/HR1_rev_comp.fasta", "fasta")

HR2_fasta = "./resources/corrected_GENE_SEQ_WITH_100_FLANKING_BASES_HR2.fasta"
records = map(make_rc_record, SeqIO.parse(HR2_fasta, "fasta"))
SeqIO.write(records, "./resources/HR2_rev_comp.fasta", "fasta")


# In[5]:


#Read gRNA excel files as table

#this file has top 3 gRNAs for each gene, read only until column C 'Total_score'
gRNA_EuPaGDT_top = pd.read_excel("./resources/selected_gRNA.PbHIT_KO_Test.xlsx",index_col=None, na_values=['NA'], usecols="A:C")
gRNA_EuPaGDT_top[['GENE ID', 'gRNA ID','directionality']] = gRNA_EuPaGDT_top.gRNA_id.str.split("_", expand = True)
#gRNA_EuPaGDT_top.rename(columns={'gRNA_id':'GENE ID'}, inplace = True)
gRNA_EuPaGDT_top['GENE ID']=gRNA_EuPaGDT_top['GENE ID'].replace('PBANKA','PBANKA_', regex= True)

#gRNA_EuPaGDT_top.head(5)

#this file has all gRNAs for each gene, read only until column C 'Total_score'
#gRNA_EuPaGDT_all = pd.read_excel("./resources/all_gRNA.PbHIT_KO_Test.xlsx",index_col=None, na_values=['NA'], usecols="A:C")
#gRNA_EuPaGDT_all[['GENE ID', 'gRNA ID','directionality']] = gRNA_EuPaGDT_all.gRNA_id.str.split("_", expand = True)
#gRNA_EuPaGDT_all.rename(columns={'gRNA_id':'GENE ID'}, inplace = True)
#gRNA_EuPaGDT_all['GENE ID']=gRNA_EuPaGDT_all['GENE ID'].replace('PBANKA','PBANKA_', regex= True)

#gRNA_EuPaGDT_all.head(5)


# In[6]:


#Create a DataFrame that has the Gene ID, HR1, and HR2
#Read HR1 FASTA file 
HR1_fasta_rev = "./resources/HR1_rev_comp.fasta"
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
HR2_fasta_rev = "./resources/HR2_rev_comp.fasta"
HR2_seq_rev= [i for i in SeqIO.parse(HR2_fasta_rev,'fasta')]

#Store HR2 sequences into a string 
genes = []
HR2_seq_rev = []

for seq_record in SeqIO.parse(HR2_fasta_rev,'fasta'):
    genes.append(seq_record.id)
    HR2_seq_rev.append(str(seq_record.seq))

#Generate table with Genes, HR1, HR2

pHIT_KO_HR = pd.DataFrame({
    "GENE ID": genes,
    "HR1 Sequence": HR1_seq_rev,
    "HR2 Sequence": HR2_seq_rev
})

#pHIT_KO_HR.head(5)


# In[7]:


#Load Gene List
#genes = pd.read_excel("./resources/Carina_Genes.xlsx",na_values=['NA'])
#gene_list=genes['Target Genes'].tolist()


# In[8]:


#Convert to batch search
#gene_list=['PBANKA_1034300,PBANKA_1231600,PBANKA_1437500,PBANKA_1015500,PBANKA_1319700']
#rows=len(gene_list)
def get_sequence_list(gene_list):
    dftest=pd.DataFrame()

    for x in gene_list:
        input_gene=x
        gene_gRNA=gRNA_EuPaGDT_top[gRNA_EuPaGDT_top['GENE ID']==input_gene]
        Result1 = None
        if not gene_gRNA.empty:
            Result1 = BbsI + gene_gRNA['gRNA_sequence']
            #print(Result1)
        else:
            raise RuntimeError(f'No gRNA for {x}')
        
        #Store Results in a data frame 
        pHIT_KO_BbsI_gRNA = pd.DataFrame({
            "GENE ID": input_gene,
            "Sequence": Result1
        })
        
        pHIT_KO_BbsI_gRNA_top2=pHIT_KO_BbsI_gRNA.iloc[:3]
        
        gene_HR=pHIT_KO_HR[pHIT_KO_HR['GENE ID']==input_gene]
        Result1 = None
        if not gene_HR.empty:
            Result2= Scaffold + gene_HR['HR2 Sequence'] + AvrII + gene_HR['HR1 Sequence']+ PstI
            #print(Result2)
        else: 
            raise RuntimeError(f'Gene Cannot be Found for {x}')

            #Convert Result2 into a list
        pHIT_KO_HR_seq=Result2.values.tolist()

            #Generate final oligo
        PbHOT_KO_Vector_List=pd.DataFrame(columns=['GENE ID', 'Oligo Sequence'])
        PbHOT_KO_Vector_List['GENE ID']=pHIT_KO_BbsI_gRNA_top2['GENE ID']
        PbHOT_KO_Vector_List['Oligo Sequence']=pHIT_KO_BbsI_gRNA_top2['Sequence']+pHIT_KO_HR_seq
        
        new_row=PbHOT_KO_Vector_List
        dftest=pd.concat([dftest,new_row])
        #df=df.append(new_row,ignore_index=True)
    return dftest

#pHIT_KO_BbsI_gRNA.head(10)

#dftest.head(10)
    


# In[9]:


#dftest.to_csv("/Users/srchernandez/Desktop/PbHiT_KO_Vector_Carina", index=None)


# In[10]:


#dftest.to_excel("/Users/srchernandez/Desktop/PbHiT_KO_Vector_Carina.xlsx", index=None)


# In[ ]:




