# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 21:33:58 2024

@author: rkpal
"""

# streamlit run d:\Projects\PubMedRead\gui.py

import streamlit as st
import json
from Bio import Entrez
import time
from pubmedreadLLM import*

start_time = time.time()

isDevt = 0

#-------------------------------------------------------------------

def search(query):
    Entrez.email = "rk.palvannan@gmail.com"
    handle = Entrez.esearch(db='pubmed',term = query, retmax = retmax)
    results = Entrez.read(handle)
    return(results)

def get_abstract(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'rk.palvannan@gmail.com'
    handle = Entrez.efetch(db='pubmed', id = ids, retmode='xml')
    results = Entrez.read(handle)
    return(results)


def get_citation(papers, i):
# Extract citations of article (except abstract)
    Title = papers['PubmedArticle'][i]['MedlineCitation']['Article']['ArticleTitle']
    Journal = papers['PubmedArticle'][i]['MedlineCitation']['Article']['Journal']['Title']
    
    try:
        Year = papers['PubmedArticle'][i]['MedlineCitation']['Article']['ArticleDate'][0]['Year']
    except:
        Year = ''
    try:
        authorLastName = papers['PubmedArticle'][i]['MedlineCitation']['Article']['AuthorList'][0]['LastName']
    except:
        authorLastName = ''
    try:
        authorForeName = papers['PubmedArticle'][i]['MedlineCitation']['Article']['AuthorList'][0]['ForeName']
    except:
        authorForeName = ''
    
    s = str(authorLastName + ', ' + authorForeName + '. ' + Title + ' ' + Journal + ' (' + Year + ')'  )
    return(s)


def summaryDownload(question, query, time, summary, abstracts):
# input: string, List<String>, int | output: single string

    s = f"Question: {question} \n\
Query: {query} \n\
Time taken min: {time} \n\n\
SUMMARY: \n\n\
{summary} \n\n"

#    for i, title in enumerate(titles):
#        s = s + str(i+1) + ') ' + title + '\n'

    for i, abstract in enumerate(abstracts):
        s = s + str(i+1) + ') ' + abstract + '\n\n'

    return(s)

#-----------------------------------------------------------------


topic = 'mrsa'


st.title("PubMed Abstracts Summary")
    
# Get user input for text string
question = st.text_input("What is your question? e.g. Is universal screening for MRSA effective?")
query = st.text_input("Enter PubMed query e.g. 'universal screening' [title] AND MRSA [title] OR hospital")
#topic = st.text_input("Filename to be saved")

# max num of abstracts to extracted
radio_label_maxNumAbs = ['5', '20', '50']
radio_maxNumAb = st.radio('Max num of abstracts - ', radio_label_maxNumAbs)
retmax = int(radio_maxNumAb)


isSubmit = st.button("Run query") 

# Display the entered text
if isSubmit:

    # extract papers, [studies] & [papers] are deep dict
    studies = search(query) # deep dict
    studiesIdList = studies['IdList'] # list of strings of ids
    papers = get_abstract(studiesIdList) # deep dict
    p = json.dumps(papers, indent = 4) # this is to viz the hierarchy (unused), p is a string
    
    # combine dict into simple list of abstracts (each abstract is a string)
    numAbstracts = len(papers['PubmedArticle'])
    titles = []
    abstracts = []
    for i in range(numAbstracts):

        print('Pubmed article - ', i+1)
        try:
            #
            txtElem = papers['PubmedArticle'][i]['MedlineCitation']['Article']['Abstract']['AbstractText']
            txt = ' '.join(txtElem)
            
            title = get_citation(papers, i) 
            titles.append(title)
            
            abstracts.append(title + '\n\n' + txt)

        except:
            print('Missing elements of abstract')
            
    numAbstracts = len(titles) # absracts with titles and abstract texts

    # Summary each article and then summarise the summaries (Use OpenAI LLM)
    summary = call_llm(abstracts, question, query, topic, start_time, isDevt)

    stop_time = time.time()
    time_taken = str(round((stop_time - start_time)/60,2))


#   To download file    
    file_download = summaryDownload(question, query, time_taken, summary, abstracts)
    st.download_button('Download results', file_download, 'text/csv')
    
    
#   print to screen    
    st.write('Time taken (min): ', time_taken )
    st.write('Num of titles/abstracts: ', str(len(titles)), '/', str(len(abstracts)))
    st.write('SUMMARY: \n')
    st.write(summary)
        
    st.write("\n\n\nREFERENCES\n")
    for i in range(numAbstracts):
        s = titles[i]
        st.write(str(i+1) + ') ' + titles[i] + '\n')



    

