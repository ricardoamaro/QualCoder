# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Colin Curtain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Author: Colin Curtain (ccbogel)
https://github.com/ccbogel/QualCoder
"""

import logging
import os
import shutil
import sqlite3

from PyQt5 import QtWidgets

from .helpers import Message

path = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)


def exception_handler(exception_type, value, tb_obj):
    """ Global exception handler useful in GUIs.
    tb_obj: exception.__traceback__ """
    tb = '\n'.join(traceback.format_tb(tb_obj))
    text = 'Traceback (most recent call last):\n' + tb + '\n' + exception_type.__name__ + ': ' + str(value)
    print(text)
    logger.error(_("Uncaught exception: ") + text)
    QtWidgets.QMessageBox.critical(None, _('Uncaught Exception'), text)


class MergeProjects:
    """ Merge one external Qualcoder project (source) database into existing project (destination).
    The merge will combine files, and codings.
    Copies files from source to destination folders.
    Adds new source code names to destination database.
    Adds journals and stored_sql to destination database, as long as they have unique names,
    Adds text codings, annotations, image codings, av codings to destination database.

    TODO
        Does not insert the Source Categories tree into the Destination.
        Does not add new category names.
        Does not add cases, case_text.
        Does not add attributes.
     """

    app = None
    path_d = ""  # Path to destination project folder
    conn_d = None
    path_s = ""  # Path to source project folder
    conn_s = None
    source_s = []  # source text from Source project
    code_text_s = []  # coded text segments from Source project
    annotations_s = []  # annotations from Source project
    journals_s = []
    stored_sql_s = []
    summary_msg = ""
    code_image_s = []  # coded image areas from Source project
    code_av_s = []  # coded A/V segments from Source project
    codes_s = []  # codes from Source project
    categories_s = []  # code cats from Source project
    cases_s = []  # cases
    case_text_s = []  # case text and links to non-text files

    def __init__(self, app, path_s):
        self.app = app
        self.path_s = path_s
        self.conn_s = sqlite3.connect(os.path.join(self.path_s, 'data.qda'))
        self.conn_d = self.app.conn
        self.path_d = self.app.project_path
        self.summary_msg = _("Merging: ") + self.path_s + "\n" + _("Into: ") + self.app.project_path + "\n"
        self.copy_source_files_into_destination()
        loaded = self.get_source_data()
        if loaded:
            self.fill_sources_get_new_file_ids()
            self.update_coding_file_ids()
            self.insert_categories()
            self.update_code_name_cid_insert_code()
            self.insert_coding_and_journal_data()
            #TODO update cases caseid and case text caseid, fid
            self.insert_cases()
            self.summary_msg += _("Finished merging " + self.path_s + " into " + self.path_d) + "\n"
            self.summary_msg += _("NOT MERGED: code categories, cases, attributes") + "\n"
            self.summary_msg += _("NOT LINKED: text transcript to audio/video")
            Message(self.app, _('Project merged'), _("Review the action log for details.")).exec_()
        else:
            Message(self.app, _('Project not merged'), _("Project not merged")).exec_()

    def update_code_name_cid_insert_code(self):
        """ Update the cid to the one already in Destination.code_name.
        Check for no matches and insert these into the Destination.code_name table.
        """

        cur_d = self.conn_d.cursor()
        sql = "select cid, name from code_name"
        cur_d.execute(sql)
        res = cur_d.fetchall()
        for r in res:
            for cn in self.codes_s:
                if cn['name'] == r[1]:
                    cn['newcid'] = r[0]
        for cn in self.codes_s:
            # Unmatched code name
            if cn['newcid'] == -1:
                cur_d.execute("insert into code_name (name,memo,owner,date,catid,color) values(?,?,?,?,?,?)",
                              (cn['name'], cn['memo'], cn['owner'], cn['date'], None, cn['color']))
                self.conn_d.commit()
                cur_d.execute("select last_insert_rowid()")
                cid = cur_d.fetchone()[0]
                cn['newcid'] = cid
                self.summary_msg += _("Adding code name: ") + cn['name'] + "\n"
        # Update code_text, code_image, code_av cids
        print("Updating Source.code_text cid to Destination.cid")
        for cn in self.codes_s:
            for ct in self.code_text_s:
                if ct['cid'] == cn['cid']:
                    ct['newcid'] = cn['newcid']
            for ci in self.code_image_s:
                if ci['cid'] == cn['cid']:
                    ci['newcid'] = cn['newcid']
            for cav in self.code_av_s:
                if cav['cid'] == cn['cid']:
                    cav['newcid'] = cn['newcid']

    def insert_categories(self):
        """ Insert categories into destination code_cat table.
         The categories have already been filtered to remove any names that match names in the destination.
         """

        cur_d = self.conn_d.cursor()
        # Insert top level categories
        remove_list = []
        for c in self.categories_s:
            if c['supercatname'] is None:
                self.summary_msg += _("Adding top level category: ") + c['name'] + "\n"
                cur_d.execute("insert into code_cat (name,memo,owner,date,supercatid) values(?,?,?,?,?)",
                              (c['name'], c['memo'], c['owner'], c['date'], c['supercatid']))
                self.conn_d.commit()
                remove_list.append(c)
        for item in remove_list:
            self.categories_s.remove(item)
        print("TODO SUB CATS")
        for c in self.categories_s:
            print("SUBCAT\n", c)

        ''' Add child categories. look at each unmatched category, iterate through
        to add as child, then remove matched categories from the list '''
        count = 0
        while len(self.categories_s) > 0 and count < 10000:
            remove_list = []
            for c in self.categories_s:
                count2 = 0
                cur_d.execute("select name, catid from code_cat")
                dest_cats = cur_d.fetchall()


                '''item = 
                while item and count2 < 10000:  # While there is an item in the list
                    if item.text(1) == 'catid:' + str(c['supercatid']):
                        memo = ""
                        if c['memo'] != "" and c['memo'] is not None:
                            memo = _("Memo")
                        # db insert HERE
                        remove_list.append(c)
                    it += 1
                    item = it.value()
                    count2 += 1'''
            for item in remove_list:
                self.categories_s.remove(item)
            count += 1

        print("END CATEGORIES METHOD\n")


    def insert_coding_and_journal_data(self):
        """ Coding fid and cid have been updated, annotation fid has been updated.
        Insert code_text, code_image, code_av, journal and stored_sql data into Destination project. """

        cur_d = self.conn_d.cursor()
        # Earlier db versions did not have unique journal name
        # Need to identify duplicate journal names and not import them
        cur_d.execute("select name from journal")
        j_names_res = cur_d.fetchall()
        j_names = []
        for j in j_names_res:
            j_names.append(j[0])
        for j in self.journals_s:
            # Possible to have two identical journal names in earlier db versions
            if j['name'] not in j_names:
                cur_d.execute("insert into journal (name, jentry, date, owner) values(?,?,?,?)",
                              (j['name'], j['jentry'], j['date'], j['owner']))
                self.summary_msg += _("Copying journal: ") + j['name'] + "\n"
                self.conn_d.commit()
        for s in self.stored_sql_s:
            # Cannot have two identical stored_sql titles, using 'or ignore'
            cur_d.execute("insert or ignore into stored_sql (title, description, grouper, ssql) values(?,?,?,?)",
                            (s['title'], s['description'], s['grouper'], s['ssql']))
            self.conn_d.commit()
        for c in self.code_text_s:
            cur_d.execute("insert or ignore into code_text (cid,fid,seltext,pos0,pos1,owner,\
                memo,date, important) values(?,?,?,?,?,?,?,?,?)", (c['newcid'], c['newfid'],
                                                                   c['seltext'], c['pos0'], c['pos1'], c['owner'],
                                                                   c['memo'], c['date'], c['important']))
            self.conn_d.commit()
        if len(self.code_text_s) > 0:
            self.summary_msg += _("Merging coded text") + "\n"
        for a in self.annotations_s:
            cur_d.execute("insert or ignore into annotation (fid,pos0,pos1,memo,owner,date) values(?,?,?,?,?,?)",
                          [a["newfid"], a["pos0"], a["pos1"], a["memo"], a["owner"], a["date"]])
            self.conn_d.commit()
        if len(self.annotations_s) > 0:
            self.summary_msg += _("Merging annotations") + "\n"
        for c in self.code_image_s:
            cur_d.execute("insert or ignore into code_image (cid, id,x1,y1,width,height,memo,owner,date,important) values(?,?,?,?,?,?,?,?,?,?)",
                          [c["newcid"], c["newfid"], c["x1"], c["y1"], c["width"], c["height"], c["memo"], c["owner"], c["date"], c["important"]])
            self.conn_d.commit()
        if len(self.code_image_s) > 0:
            self.summary_msg += _("Merging coded image areas") + "\n"
        for c in self.code_av_s:
            cur_d.execute("insert or ignore into code_av (cid, id,pos0,pos1,memo,owner,date,important) values(?,?,?,?,?,?,?,?)",
                [c["newcid"], c["newfid"], c["pos0"], c["pos1"], c["memo"], c["owner"], c["date"], c["important"]])
            self.conn_d.commit()
        if len(self.code_av_s) > 0:
            self.summary_msg += _("Merging coded audio/video segments") + "\n"

    def insert_cases(self):
        """ Insert case data into destination. """

        print("TODO update caseid in cases and case_text. Update fid in case_text")
        print("TODO load cases and case text data")

        '''{'caseid': 1, 'newcaseid': -1, 'name': 'first case', 'memo': 'first test case', 
         'owner': 'default',
         'date': '2022-03-11 22:00:21'}
        {'caseid': 1, 'newcaseid': -1, 'fid': 4, 'newfid': -1, 'pos0': 0, 'pos1': 0}
        {'caseid': 1, 'newcaseid': -1, 'fid': 5, 'newfid': -1, 'pos0': 0, 'pos1': 4}'''

        for i in self.cases_s:
            print(i)
        for i in self.case_text_s:
            print(i)

    def fill_sources_get_new_file_ids(self):
        """ Insert Source.source into Destination.source, unless source name is already present.
        update newfid in source_s and code_text_s.
        Update the av_text_id link to link A/V to the corresponding transcript.
        """

        cur_d = self.conn_d.cursor()
        for src in self.source_s:
            cur_d.execute("select id from source where name=?", [src['name']])
            res = cur_d.fetchone()
            if res is not None:
                # Existing same named source file in the destination project
                src['newid'] = res[0]
            else:
                # To update the av_text_id after all new ids have been generated
                cur_d.execute("insert into source(name,fulltext,mediapath,memo,owner,date, av_text_id) values(?,?,?,?,?,?,?)",
                              (src['name'], src['fulltext'], src['mediapath'], src['memo'], src['owner'], src['date'], None))
                self.conn_d.commit()
                cur_d.execute("select last_insert_rowid()")
                id_ = cur_d.fetchone()[0]
                src['newid'] = id_
        # Need to find matching av_text_filename to get its id to link as the av_text_id
        for src in self.source_s:
            if src['av_text_filename'] != "":
                cur_d.execute("select id from source where name=?", [src['av_text_filename']])
                res = cur_d.fetchone()
                if res is not None:
                    cur_d.execute("update source set av_text_id=? where id=?", [res[0], src['id']])
                    self.conn_d.commit()

    def update_coding_file_ids(self):
        """ Update the file ids in the codings and annotations data. """

        for src in self.source_s:
            for c_text in self.code_text_s:
                if c_text['fid'] == src['id']:
                    c_text['newfid'] = src['newid']
            for an in self.annotations_s:
                if an['fid'] == src['id']:
                    an['newfid'] = src['newid']
            for c_img in self.code_image_s:
                if c_img['fid'] == src['id']:
                    c_img['newfid'] = src['newid']
            for c_av in self.code_av_s:
                if c_av['fid'] == src['id']:
                    c_av['newfid'] = src['newid']

    def copy_source_files_into_destination(self):
        """ Copy source files into destination project.
        Do not copy over existing files.
        """

        print("Copy source files into dest")
        folders = ["audio", "documents", "images", "video"]
        for folder_name in folders:
            dir_ = self.path_s + "/" + folder_name
            files = os.listdir(dir_)
            for f in files:
                if not os.path.exists(self.app.project_path + "/" + folder_name + "/" + f):
                    try:
                        shutil.copyfile(dir_ + "/" + f, self.app.project_path + "/" + folder_name + "/" + f)
                        self.summary_msg += _("File copied: ") + f + "\n"
                    except shutil.SameFileError:
                        pass
                    except PermissionError:
                        self.summary_msg += f + " " + _("NOT copied. Permission error")

    def get_source_data(self):
        """ Load the entire database data into Lists of Dictionaries.
        TODO
        cases (caseid integer primary key, name text, memo text, owner text,date text
        TODO
        case_text (id integer primary key, caseid integer, fid integer, pos0 integer, pos1 integer, "
            "owner text, date text, memo
        TODO
        ##code_cat (catid integer primary key, name text, owner text, date text, memo text, supercatid integer, unique(name)
        TODO
        attribute_type (name text primary key, date text, owner text, memo text, caseOrFile text, "
            "valuetype
        TODO
        attribute (attrid integer primary key, name text, attr_type text, value text, id integer, "
            "date text, owner

        return:
            True or False if data was able to be loaded
        """

        self.journals_s = []
        self.stored_sql_s = []
        self.codes_s = []
        self.categories_s = []
        self.code_text_s = []
        self.annotations_s = []
        self.code_image_s = []
        self.code_av_s = []
        self.cases_s = []
        self.case_text_s = []
        cur_s = self.conn_s.cursor()
        # Database version must be v5
        cur_s.execute("select databaseversion from project")
        version = cur_s.fetchone()
        if version[0] < "v5":
            self.summary_msg += _("Need to update the source project database.") + "\n"
            self.summary_msg += _("Please open the source project using QualCoder. Then close the project") + "n"
            self.summary_msg += _("Project not merged") + "\n"
            return False
        # Journal data
        sql_journal = "select name, jentry, date, owner from journal"
        cur_s.execute(sql_journal)
        res_journals = cur_s.fetchall()
        for i in res_journals:
            src = {"name": i[0], "jentry": i[1], "date": i[2], "owner": i[3]}
            self.journals_s.append(src)
        # Stored sql data
        sql_stored_sql = "select title, description, grouper, ssql from stored_sql"
        cur_s.execute(sql_stored_sql)
        res_stored_sqls = cur_s.fetchall()
        for i in res_stored_sqls:
            src = {"title": i[0], "description": i[1], "grouper": i[2], "ssql": i[3]}
            self.stored_sql_s.append(src)
        # Source data
        sql_source = "select id, name, fulltext,mediapath,memo,owner,date,av_text_id from source"
        cur_s.execute(sql_source)
        res_source = cur_s.fetchall()
        # Later update av_text_id
        for i in res_source:
            src = {"id": i[0], "newid": -1, "name": i[1], "fulltext": i[2], "mediapath": i[3], "memo": i[4],
                   "owner": i[5], "date": i[6], "av_text_id": i[7], "av_text_filename": ""}
            self.source_s.append(src)
        # The av_text_id is not enough to recreate linkages. Need the refernced text file name.
        for i in self.source_s:
            if i['av_text_id'] is not None:
                cur_s.execute("select name from source where id=?", [i['av_text_id']])
                res = cur_s.fetchone()
                if res is not None:
                    i['av_text_filename'] = res[0]
        # Category data
        sql_codecats = "select catid, supercatid, name, memo, owner, date from code_cat"
        cur_s.execute(sql_codecats)
        res_codecats = cur_s.fetchall()
        for i in res_codecats:
            ccat = {"catid": i[0], "supercatid": i[1], "supercatname": None,
                    "name": i[2], "memo": i[3], "owner": i[4], "date": i[5], }
            self.categories_s.append(ccat)
        # Remove categories from the source list, that are already present in the destination database
        cur_d = self.app.conn.cursor()
        cur_d.execute("select name from code_cat")
        res_dest_catnames = cur_d.fetchall()
        dest_cat_names_list = []
        for r in res_dest_catnames:
            dest_cat_names_list.append(r[0])
        temp_source_cats = []
        for cat in self.categories_s:
            if cat['name'] not in dest_cat_names_list:
                temp_source_cats.append(cat)
        self.categories_s = temp_source_cats
        # Add reference to linked supercat using category name
        for cat in self.categories_s:
            cur_s.execute("select name from code_cat where catid=?", [cat['supercatid']])
            res = cur_s.fetchone()
            if res is not None:
                cat['supercatname'] = res[0]
        # Code data
        sql_codenames = "select cid, name, memo, owner, date, color from code_name"
        cur_s.execute(sql_codenames)
        res_codenames = cur_s.fetchall()
        for i in res_codenames:
            cn = {"cid": i[0], "newcid": -1, "name": i[1], "memo": i[2], "owner": i[3], "date": i[4], "color": i[5],
                  "catid": None, "catname": None}
            self.codes_s.append(cn)
        for c in self.codes_s:
            cur_s.execute("select name from code_cat where catid=?", [c['catid']])
            res = cur_s.fetchone()
            if res is not None:
                cat['catname'] = res[0]
        # Code text data
        sql_codetext = "select cid, fid, seltext, pos0, pos1, owner, date, memo, important from code_text"
        cur_s.execute(sql_codetext)
        res_codetext = cur_s.fetchall()
        for i in res_codetext:
            ct = {"cid": i[0], "newcid": -1, "fid": i[1], "newfid": -1, "seltext": i[2], "pos0": i[3], "pos1": i[4],
                  "owner": i[5], "date": i[6], "memo": i[7], "important": i[8]}
            self.code_text_s.append(ct)
        # Text annotations data
        sql_annotations = "select fid, pos0, pos1, memo, owner, date from annotation"
        cur_s.execute(sql_annotations)
        res_annot = cur_s.fetchall()
        for i in res_annot:
            an = {"fid": i[0], "newfid": -1, "pos0": i[1], "pos1": i[2], "memo": i[3], "owner": i[4], "date": i[5]}
            self.annotations_s.append(an)
        # Code image data
        sql_code_img = "select cid, id, x1, y1, width, height, memo, date, owner, important from code_image"
        cur_s.execute(sql_code_img)
        res_code_img = cur_s.fetchall()
        for i in res_code_img:
            cimg = {"cid": i[0], "newcid": -1, "fid": i[1], "newfid": -1, "x1": i[2], "y1": i[3],
                    "width": i[4], "height": i[5], "memo": i[6], "date": i[7], "owner": i[8], "important": i[9]}
            self.code_image_s.append(cimg)
        # Code AV data
        sql_code_av = "select cid, id, pos0, pos1, owner, date, memo, important from code_av"
        cur_s.execute(sql_code_av)
        res_code_av = cur_s.fetchall()
        for i in res_code_av:
            c_av = {"cid": i[0], "newcid": -1, "fid": i[1], "newfid": -1, "pos0": i[2], "pos1": i[3],
                    "owner": i[4], "date": i[5], "memo": i[6], "important": i[7]}
            self.code_av_s.append(c_av)

        # Case data
        sql_cases = "select caseid, name, memo, owner, date from cases"
        cur_s.execute(sql_cases)
        res_cases = cur_s.fetchall()
        for i in res_cases:
            c = {"caseid": i[0], "newcaseid": -1, "name": i[1], "memo": i[2], "owner": i[3], "date": i[4]}
            self.cases_s.append(c)
        sql_case_text = "select caseid, fid, pos0, pos1 from case_text"
        cur_s.execute(sql_case_text)
        res_case_text = cur_s.fetchall()
        for i in res_case_text:
            c = {"caseid": i[0], "newcaseid": -1, "fid": i[1], "newfid": -1, "pos0": i[2], "pos1": i[3]}
            self.cases_s.append(c)
        return True
