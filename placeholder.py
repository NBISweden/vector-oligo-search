from bio import SeqIO
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from random import randint

#Set standard elements of the gRNA oligo into items
BbsI = 'GAAGACggTATT'
Scaffold = 'GTTTTAGAGCTAGAAATAGCAAGTTAAAATAAGGCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC'
AvrII = 'CCTAGG'
PstI = 'CTGCAG'



#Read gRNA excel files as table
#this file has top 3 gRNAs for each gene, read only until column C 'Total_score'
gRNA_EuPaGDT_top = pd.read_excel("selected_gRNA.PbHIT_KO_Test.xlsx",index_col=None, na_values=['NA'], usecols="A:C")
gRNA_EuPaGDT_top[['GENE ID', 'gRNA ID','directionality']] = gRNA_EuPaGDT_top.gRNA_id.str.split("_", expand = True)
gRNA_EuPaGDT_top['GENE ID']=gRNA_EuPaGDT_top['GENE ID'].replace('PBANKA','PBANKA_', regex= True)

#Create a DataFrame that has the Gene ID, HR1, and HR2
#Read HR1 FASTA file
HR1_fasta_rev = "HR1_rev_comp.fasta"
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
HR2_fasta_rev = "HR2_rev_comp.fasta"
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

genes = pd.read_excel("Carina_Genes.xlsx",na_values=['NA'])
gene_list = genes['Target Genes'].tolist()

#Convert to batch search
#gene_list=['PBANKA_1034300,PBANKA_1231600,PBANKA_1437500,PBANKA_1015500,PBANKA_1319700']
rows = len(gene_list)
dftest = pd.DataFrame()

for x in gene_list:
    input_gene=x
    gene_gRNA=gRNA_EuPaGDT_top[gRNA_EuPaGDT_top['GENE ID']==input_gene]
    if not gene_gRNA.empty:
        Result1 = BbsI + gene_gRNA['gRNA_sequence']
        #print(Result1)
    else:
        print('No gRNA')

    #Store Results in a data frame
    pHIT_KO_BbsI_gRNA = pd.DataFrame({
        "GENE ID": input_gene,
        "Sequence": Result1
    })

    pHIT_KO_BbsI_gRNA_top2=pHIT_KO_BbsI_gRNA.iloc[:3]

    gene_HR=pHIT_KO_HR[pHIT_KO_HR['GENE ID']==input_gene]
    if not gene_HR.empty:
        Result2= Scaffold + gene_HR['HR2 Sequence'] + AvrII + gene_HR['HR1 Sequence']+ PstI
        #print(Result2)
    else:
        # ERROR handling here
        print('Gene Cannot be Found')

        #Convert Result2 into a list
    pHIT_KO_HR_seq=Result2.values.tolist()

        #Generate final oligo
    PbHOT_KO_Vector_List=pd.DataFrame(columns=['GENE ID', 'Oligo Sequence'])
    PbHOT_KO_Vector_List['GENE ID']=pHIT_KO_BbsI_gRNA_top2['GENE ID']
    PbHOT_KO_Vector_List['Oligo Sequence']=pHIT_KO_BbsI_gRNA_top2['Sequence']+pHIT_KO_HR_seq

    new_row=PbHOT_KO_Vector_List
    dftest=pd.concat([dftest,new_row])

def VectorOligoSearch(id):
  d = {'key': ['BbsI', 'Scaffold', 'AvrII', 'PstI'], 'val': [BbsI, Scaffold, AvrII, PstI]}
  df = pd.DataFrame(data=d)
  return dftest.to_csv()