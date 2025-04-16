#!/usr/bin/env python
# coding: utf-8
# flake8: noqa

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


#Set standard elements of the gRNA oligo into items
BbsI = 'GAAGACggTATT'
Scaffold = 'GTTTTAGAGCTAGAAATAGCAAGTTAAAATAAGGCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC'
AvrII = 'CCTAGG'
PstI = 'CTGCAG'


#Load GFF file and extract positive and negative strand information
PBANKA_GFF_FILE = pd.read_csv("./resources/ko/GENE_ONLY_PlasmoDB-57_PbergheiANKA.gff", delimiter = "\t", comment = "#", header=None)
PBANKA_GFF_FILE.columns = ["seqid", "source", "type", "start", "end", "score", "strand", "phase", "attributes"]
PBANKA_GFF_FILE[['GENE ID', 'B','C']] = PBANKA_GFF_FILE.attributes.str.split(";", expand = True)
PBANKA_GFF_FILE['GENE ID']=PBANKA_GFF_FILE['GENE ID'].replace('ID=PBANKA','PBANKA',regex=True)

#PBANKA_GFF_FILE.head(10)


#Read gRNA excel files as table

#this file has top 3 gRNAs for each gene, read only until column C 'Total_score'
gRNA_EuPaGDT_top = pd.read_excel("./resources/ko/selected_gRNA.PbHIT_KO_Test.xlsx",index_col=None, na_values=['NA'], usecols="A:C")
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


#Combine gRNA strand information and gRNA file
gRNA_EuPaGDT_top = pd.merge(gRNA_EuPaGDT_top,PBANKA_GFF_FILE,on='GENE ID')
#gRNA_EuPaGDT_top.head()


pHIT_KO_HR = pd.read_excel("./resources/ko/PbHiT_KO_Vector_HR_List_April16_RE.xlsx")


#Load Gene List
#genes = pd.read_excel("./resources/CRISPR_PbHIT_KO_Vector/PbHIT_KO_Vector_Final/PbHIT_KO_Vector_Pool_100.xlsx",na_values=['NA'])
#gene_list=genes['Target Genes'].tolist()


#Convert to batch search
#gene_list=['PBANKA_1237100','PBANKA_1040100','PBANKA_0310300','PBANKA_0622100','PBANKA_0709700','PBANKA_0823400','PBANKA_0826800','PBANKA_0826900','PBANKA_0827100','PBANKA_0829700','PBANKA_0831200']
#rows=len(gene_list)
def get_sequence_list(gene_list):
    dftest=pd.DataFrame()

    for x in gene_list:
        input_gene=x
        gene_gRNA=gRNA_EuPaGDT_top[gRNA_EuPaGDT_top['GENE ID']==input_gene]
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
        strand=gene_HR['strand_x'].to_list()[0]
        #print(strand)
        if strand=='+':
            if not gene_HR.empty:
                Result2= Scaffold + gene_HR['HR2 Sequence Fw'] + AvrII + gene_HR['HR1 Sequence Fw']+ PstI
                #print(Result2)
            else: 
                raise RuntimeError(f'Gene Cannot be Found for {x}')

        if strand=='-':
            if not gene_HR.empty:
                Result2= Scaffold + gene_HR['HR1 Sequence Rev'] + AvrII + gene_HR['HR2 Sequence Rev']+ PstI
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



#dftest.to_excel("/Users/srchernandez/Desktop/PbHiT_KO_Vector_April16_kinases.xlsx", index=None)


#dftest.to_csv("/Users/srchernandez/Desktop/PbHiT_KO_Vector_List_test.csv", index=None)




