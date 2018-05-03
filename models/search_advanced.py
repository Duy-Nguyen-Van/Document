# -*- coding: utf-8 -*-
from odoo import models, fields,api
from datetime import datetime

import numpy as np
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata

class SearchAdvanced(models.Model):
    _name = 'se.advanced.auto'
    _description = 'Search Advanced'
    search1 = fields.Char('Content')
    result2 = fields.Text('Result')



    def text_cleaner(self, text):
        text = re.sub('[\.]', ' ', text)
        text = re.sub(
            '([^a-z0-9A-Z_ ÀÁÂÃÈÉÊẾÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽếềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵýỷỹ])\W|\s\(|\(|\)',
            ' ', text)
        text = re.sub('\W', ' ', text.lower())
        text = re.sub('\d', '', text)
        text = re.sub('[\_]', ' ', text)
        return text

    def tfidf_vectorizer(self, search_query,df, min_df=1):
        f = open('/home/odoo/odoo-dev/odoo/custom_addons/islabdocument/data/vietnamese_stopwords.txt')
        stop_words = f.readlines()
        stop_words = [x.strip('\n') for x in stop_words]
        tfidf_vec = TfidfVectorizer(stop_words=stop_words, min_df=min_df)
        doc_term_matrix = tfidf_vec.fit_transform(df['dense_content'])
        search_query_vec = tfidf_vec.transform([search_query])
        return doc_term_matrix, search_query_vec

    def SVD_lsa(self,search_query,df, n_components=300, min_df=1):
        SVD = TruncatedSVD(n_components=n_components)
        doc_term_matrix, search_query_vec = self.tfidf_vectorizer(search_query,df, min_df)

        lsa_doc_term = SVD.fit_transform(doc_term_matrix)
        search_query_lsa = SVD.transform(search_query_vec)

        return lsa_doc_term, search_query_lsa

    def grab_related_articles(self,search_query,df, n_results=5, n_components=300, min_df=1):
        lsa_doc_term, search_query_lsa = self.SVD_lsa(search_query,df, n_components=n_components, min_df=min_df)
        cos_sim_arr = cosine_similarity(lsa_doc_term, search_query_lsa).ravel()

        first_term = -1 * (n_results) - 1
        indices = (np.argsort(cos_sim_arr)[:first_term: -1])
        while len(list(set(df['dense_content'].iloc[indices]))) < n_results:
            first_term -= 1
            indices = (np.argsort(cos_sim_arr)[:first_term: -1])
        related_articles = list(set(df['data_id'].iloc[indices]))
        return related_articles

    def action_search_auto(self):
        content = self.search1
        info_list = []
        doc_list = self.env['doc.task'].search([])
        ids = []
        contents = []
        for doc in doc_list:
            ids.append(doc.id)
            contents.append(doc.otherinfor)

        df = pd.DataFrame({'data_id': ids, 'dense_content': contents})
        df = df.dropna(subset=['dense_content'])
        df.set_index('data_id')
        df['dense_content'] = df['dense_content'].apply(lambda x: unicodedata.normalize('NFC', x))
        df['dense_content'] = df['dense_content'].apply(lambda x: self.text_cleaner(x))
        a = self.grab_related_articles(content,df, n_results=5, n_components=6, min_df=1)
        result = []
        tup_a = tuple(a)
        for doc in doc_list:
            if doc.id in a:
                result.append(doc)
        print(result)
        # return {
        #     'res_model': 'doc.task',
        #     'view_type':'tree',
        #     'view_mode':'tree',
        #     'view_id' : False,
        #     'views': [('view_tree_doc_task','tree')],
        #     'type': 'ir.actions.act_window',
        #     'domain':"['id','in',%s]" %(a),
        # }
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            # 'view_id': 'False',
            'view-id': [(self.env.ref('islabdocument.view_tree_doc_task').id),(self.env.ref('islabdocument.view_form_doc_task').id)],
            'res_model': 'doc.task',
            'domain': [('id', 'in', a)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            # 'context': 'context',

        }

