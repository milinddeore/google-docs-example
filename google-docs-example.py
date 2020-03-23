# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Written by Milind Deore <tomdeore@gmail.com>, March-2020

from __future__ import print_function
import pickle
import os.path
import sys
import random
import wikipediaapi
import uuid
from datetime import date
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

DEBUG = 0
if DEBUG:
    import json

class Covid19Docs:
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        self.DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
        self.creds = None
        # Add all your created templates in the below list.
        self.templates = ['1a0C3AQ290uc0yFcVhLD36sj12mQdmv_VnSjh4WhnNvQ']
        self.drive_service = None
        self.docs_service = None
        self.wiki = wikipediaapi.Wikipedia(language='en', extract_format=wikipediaapi.ExtractFormat.WIKI)
        self.covid19_wiki = self.wiki.page("Coronavirus_disease_2019")


        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.DRIVE_SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        if self.creds == None:
            print('ERROR : Service credentials unavailable!')
            sys.exit()

        # Start drive and docs services.
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)



    def pick_a_template(self):
        """
        There can be a list of templated that you can pick from. Make sure you add them
        to template list.
        """

        title = 'covid-19_' + str(uuid.uuid1())
        body = {
            'name': title,
            'description': 'Covid-19 Wiki'
        }
        drive_response = self.drive_service.files().copy(
            fileId=random.choice(self.templates), body=body).execute()
        document_copy_id = drive_response.get('id')
        print('Dup copy ID : {0}'.format(document_copy_id))

        return document_copy_id


    def replace_a_data(self, key, value):
        """
        Replace text in the document using 'key/tag'
        """
        dic = {'replaceAllText': {
                    'containsText': {
                        'text': '{{' + key + '}}',
                        'matchCase':  'true'
                    },
                    'replaceText': value,
                }}
        return dic


    def insert_bullet_text(self, idx, title):
        """
        Create bullets in the document.
        """

        requests = [
         {
            'insertText': {
                'location': {
                    'index': idx,
                },
                'text': title
            }},{
                'createParagraphBullets': {
                 'range': {
                     'startIndex': idx,
                     'endIndex':  idx + len(title)
                 },
                 'bulletPreset': 'BULLET_DIAMONDX_ARROW3D_SQUARE',
             }
        }]

        result = self.docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()

        if result:
            pass

        return len(title)


    def insert_text(self, idx, text):
         """
         Insert raw text without formating.
         """
         req = {'insertText': {
                 'location': {
                     'index': idx,
                 },
                 'text': text
             }}

         return req, len(text)


    def format_text(self, starti, endi, is_bold, is_italic, is_underline):
        """
        Format the text as following:
        - Bold
        - Italic
        """
        req = {'updateTextStyle': {
                'range': {
                    'startIndex': starti,
                    'endIndex': endi
                },
                'textStyle': {
                    'bold': is_bold,
                    'italic': is_italic,
                    'underline': is_underline
                },
                'fields': 'bold, italic'
            }}

        return req


    def hwd_batch_update(self, doc_id, requests):
        """
        Batch update the document with the requests.
        """

        result = self.docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()

        return result


    def hwd_insert_hyperlink(self, doc_id, start_idx, end_idx, url):
        """
        Insert hyperlink to the text for a given range in the
        document body.
        """

        requests = [
          {
           "updateTextStyle": {
            "textStyle": {
             "link": {
              "url": url
             }
            },
            "range": {
             "startIndex": start_idx,
             "endIndex": end_idx
            },
            "fields": "link"
           }}
        ]

        result = self.docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()

        return result


    def get_text_range_idx(self, doc_id, match_text):
        """
        Find text and their start and end index.
        """

        # Do a document "get" request and print the results as formatted JSON
        result = self.docs_service.documents().get(documentId=doc_id).execute()
        if DEBUG:
            print('RX Data {0}'.format(json.dumps(result, indent=4)))
        with open('data.json', 'w') as f:
            json.dump(result, f, indent=4)
        data = result.get('body').get('content')
        startIdx = 0
        endIdx = 0

        for d in data:
            para = d.get('paragraph')
            if para is None:
                continue
            else:
                elements = para.get('elements')
                for e in elements:
                    if e.get('textRun'):
                        content = e.get('textRun').get('content')
                        print(' {}'.format(content))
                        if match_text in content:
                            print('matched')
                            startIdx = e.get('startIndex')
                            endIdx = e.get('endIndex')

        return startIdx, endIdx


    def insert_image(self, start_idx, url, h, w):
        """
        Insert PNG, JPEG, GIF images inline, while adding text.
        """

        request = [{
            'insertInlineImage': {
                'location': {
                    'index': start_idx
                },
                'uri':
                    url,
                'objectSize': {
                    'height': {
                        'magnitude': h,
                        'unit': 'PT'
                    },
                    'width': {
                        'magnitude': w,
                        'unit': 'PT'
                    }
                }
            }
        }]

        return request


    def print_main_sections(self, doc_id, endi):
        section_titles = ['Signs and symptoms', 'Cause', 'Diagnosis', 'Prevention']
        requests = []
        wr_idx = endi + 1

        for s in self.covid19_wiki.sections:
            if s.title in section_titles:
                section_title = '\n' + s.title + ' :\n'
                req, idx = self.insert_text(wr_idx, section_title)
                requests.append(req)
                req = self.format_text(wr_idx, wr_idx + idx, True, False, False)
                requests.append(req)
                wr_idx += idx
                req, idx = self.insert_text(wr_idx, s.text + '\n')
                requests.append(req)
                wr_idx += idx
                if s.title == 'Prevention':
                    req = self.insert_image(wr_idx, 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Covid-19-curves-graphic-social-v3.gif/640px-Covid-19-curves-graphic-social-v3.gif', 480, 276)
                    requests.append(req)
                    req = self.insert_image(wr_idx, 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Covid-19-curves-graphic2-stopthespread-v3.gif/640px-Covid-19-curves-graphic2-stopthespread-v3.gif', 480, 276)
                    requests.append(req)

        result = self.docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()

        return result, endi



if __name__ == '__main__':

    c_docs = Covid19Docs()
    doc_id = c_docs.pick_a_template()

    requests = []
    requests.append(c_docs.replace_a_data('title', 'Coronavirus Disease 2019'))

    today = date.today()
    requests.append(c_docs.replace_a_data('date', '{0}'.format(today)))
    c_docs.hwd_batch_update(doc_id, requests)

    starti, endi = c_docs.get_text_range_idx(doc_id, 'Details :')
    rlt, endi = c_docs.print_main_sections(doc_id, endi)


