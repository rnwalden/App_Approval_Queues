# ######################################################
# Name of the module: approval_que_app
# Date of module creation: 7/25/2022
# Author of the module: Robert Walden
# Synopsis: Assists in the managing of banner approval queues.
# Modification history:
#
# ######################################################

#import datetime
from datetime import date
import time
import logging
import tkinter
from tkinter import filedialog
import os

import cx_Oracle
import getpass


my_logger = logging.getLogger('execution_logger')
my_logger.setLevel(logging.INFO)
my_logger_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
my_logger_handler = logging.FileHandler(f'logs/execution_logger_{date.today().isoformat()}.log')
my_logger_handler.setFormatter(my_logger_format)
my_logger.addHandler(my_logger_handler)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        exec_time = (te - ts)  # int((te - ts) * 1000)
        print(method.__name__, ' exec_time:', exec_time)
        return result
    return timed


class OracleConnect:
    def __init__(self):
        my_logger.info(f"""### OracleConnect :: __init__ ###' """)
        self.debug = False
        self.user = ''
        self.password = ''
        self.get_credentials()
        self.dsn_tns = self.select_database()
        self.engine_connection = self.connection()

        # defaults
        # xxxA
        self.foap_approvers = ['AMUSIAL1', 'EOBRIEN3']
        # xxxB
        self.acct_approvers = ['KJANISZEWSKI', 'UGOFF', 'BJESTER1', 'LNOWAK']
        # Bxxx
        self.budget_approvers = ['KJANISZEWSKI', 'UGOFF', 'BJESTER1', 'LNOWAK']

        try:
            os.mkdir('logs')
        except:
            print('logs file exists in project_root')

    def connection(self):
        try:
            _connection = cx_Oracle.connect(self.user, self.password,
                                            dsn=self.dsn_tns,
                                            encoding="UTF-8")

            my_logger.info(f"""###OracleConnect :: Connection Established ###, self.user: {self.user}, self.dsn_tns: {self.dsn_tns} """)

            return _connection

        except Exception as e:
            print(e)
            self.get_credentials()

        if self.debug is True:
            print('### ##### connection #######')
            print('## DB Connection as:', self.user, 'TNS string:', self.dsn_tns)
            print('## DB Connection object:', (_connection if _connection else 'no connection'))
            print('## if error:', (e if e else 'no error'))

    def get_credentials(self):
        self.user = getpass.getpass("Username: ")
        self.password = getpass.getpass("Password: ")

        if self.debug is True:
            print('### ##### get_credentials #######')
            print('## DB Connection as:', self.user, 'password:', self.password)

    def select_database(self):
        _db = input('which database to use (PROD,PREP):')
        if _db.upper() == 'PREP':
            _dsn_tns = cx_Oracle.makedsn('bandb-at1.test.avc.edu', '1521', 'avcprep')
        elif _db.upper() == 'PROD':
            _dsn_tns = cx_Oracle.makedsn('bandb-aws1.avc.edu', '1521', 'avcprod')
        else:
            print("Ex. 'bandb-at1.test.avc.edu', '1521', 'avcprep'")
            _dsn_tns = cx_Oracle.makedsn(input('enter dns_tns string:'))

        if self.debug is True:
            print('### ##### select_database #######')
            print('## DB TNS String:', _dsn_tns)

        return _dsn_tns

    # Generic DB Query Update Insert Delete
    def db_query(self, _select, _from, _where, _order_by, _group_by, _max_records_returned):
        _select = f"""select  {_select}"""
        _from = f"""from {_from}"""
        _where = (f"""where {_where}""" if _where else '')
        _order_by = (f"""order by {_order_by}""" if _order_by else '')
        _group_by = (f"""group by {_group_by}""" if _group_by else '')
        _max_records_returned = (f"""fetch next {_max_records_returned} rows only""" if _max_records_returned else '')
        _query = f"""{_select} {_from} {_where} {_order_by} {_group_by} {_max_records_returned}"""
        app_data = self.execute_sql_query(_query)

        if self.debug is True:
            print('### ##### db_query #######')

        return app_data

    @timeit
    def execute_sql_query(self, _query):
        print(_query)
        with self.engine_connection.cursor() as _cur:
            _cur.execute(_query)
            app_data = _cur.fetchall()

        if self.debug is True:
            print('### ##### execute_sql_query #######')
            print('_query:', _query)

        # my_logger.info(f"""'execute_sql_query', '_query:', {_query}, 'app_data:', {app_data}""")

        return app_data

    def db_update(self, my_update, my_set, my_where):
        _update = f"""update {my_update}"""
        _set = f"""set {my_set}"""
        _where = f"""where {my_where}"""
        update_statement = f"""{_update} {_set} {_where}"""
        _result = self.execute_sql_update(update_statement)

        if self.debug is True:
            print('### ##### db_update #######')

        return _result

    @timeit
    def execute_sql_update(self, update_statement):
        print(update_statement)
        with self.engine_connection.cursor() as _cur:
            try:
                _cur.execute(update_statement)
                _result = self.engine_connection.commit()
            except Exception as e:
                self.engine_connection.rollback()
                return e

        if self.debug is True:
            print('### ##### execute_sql_update #######')

        my_logger.info(f"""'###OracleConnect :: execute_sql_update', 'update_statement:', {update_statement}, '_result:', {_result}""")

        return _result

    def db_insert(self, my_insert, my_values):
        _insert = f"""into {my_insert}"""
        _value = f"""values({my_values})"""
        insert_statement = f"""insert {_insert} {_value}"""
        _result = self.execute_sql_insert(insert_statement)

        if self.debug is True:
            print('### ##### db_insert #######')

        return _result

    @timeit
    def execute_sql_insert(self, insert_statement):
        print(insert_statement)
        with self.engine_connection.cursor() as _cur:
            try:
                _cur.execute(insert_statement)
                _result = self.engine_connection.commit()
            except Exception as e:
                self.engine_connection.rollback()
                return e

        if self.debug is True:
            print('### ##### execute_sql_insert #######')

        my_logger.info(f"""'execute_sql_insert', 'insert_statement:', {insert_statement}, '_result:', {_result}""")

        return _result

    def db_delete(self, my_from, my_where):
        _from = f"""from {my_from}"""
        _where = f"""where {my_where}"""
        delete_statement = f"""delete {_from} {_where}"""
        print('delete_statement', delete_statement)
        _result = self.execute_sql_delete(delete_statement)

        if self.debug is True:
            print('### ##### db_delete #######')

    @timeit
    def execute_sql_delete(self, delete_statement):
        print(delete_statement)
        with self.engine_connection.cursor() as _cur:
            try:
                _cur.execute(delete_statement)
                _result = self.engine_connection.commit()
            except Exception as e:
                self.engine_connection.rollback()
                return e

        if self.debug is True:
            print('### ##### execute_sql_delete #######')

        my_logger.info(f"""'execute_sql_delete', 'delete_statement:', {delete_statement}, '_result:', {_result}""")

        return _result

    # should split here and make another class out of it
    # Use specific methods
    # # Approval Queue Methods
    def query_foraqus(self, my_where='', my_order_by='', my_group_by='', my_max_records_returned=''):
        select = f"""FORAQUS_QUEUE_ID,FORAQUS_USER_ID_APPR,FORAQUS_QUEUE_LEVEL,FORAQUS_QUEUE_LIMIT,FORAQUS_EFF_DATE,
        FORAQUS_NCHG_DATE,FORAQUS_TERM_DATE"""
        from_ = f"""FORAQUS"""
        x = self.db_query(select, from_, my_where, my_order_by, my_group_by, my_max_records_returned)

        if self.debug is True:
            print('### ##### query_foraqus #######')

        return x

    def query_ftvappq(self, my_where='', my_order_by='', my_group_by='', my_max_records_returned=''):
        select = f"""FTVAPPQ_QUEUE_ID, FTVAPPQ_DESCRIPTION, FTVAPPQ_QUEUE_LIMIT, FTVAPPQ_NEXT_QUEUE_ID, FTVAPPQ_APPROVAL_REQ, FTVAPPQ_ACTIVITY_DATE, FTVAPPQ_USER_ID"""
        from_ = f"""FTVAPPQ"""
        x = self.db_query(select, from_, my_where, my_order_by, my_group_by, my_max_records_returned)

        if self.debug is True:
            print('### ##### query_ftvappq #######')

        return x

    def query_foraqrc(self, my_where='', my_order_by='', my_group_by='', my_max_records_returned=''):
        select = f"""FORAQRC_QUEUE_ID, FORAQRC_DOC_TYPE, FORAQRC_RULE_GROUP, FORAQRC_COAS_CODE, FORAQRC_FTYP_CODE, FORAQRC_FUND_CODE, FORAQRC_ORGN_CODE, FORAQRC_ATYP_CODE, FORAQRC_ACCT_CODE, FORAQRC_ACTIVITY_DATE, FORAQRC_USER_ID, FORAQRC_PROG_CODE"""
        from_ = f"""FORAQRC"""
        x = self.db_query(select, from_, my_where, my_order_by, my_group_by, my_max_records_returned)

        if self.debug is True:
            print('### ##### query_foraqrc #######')

        return x

    def insert_into_ftvappq(self, _my_value):
        my_insert = """FTVAPPQ(FTVAPPQ_QUEUE_ID, FTVAPPQ_DESCRIPTION, FTVAPPQ_QUEUE_LIMIT, FTVAPPQ_NEXT_QUEUE_ID, FTVAPPQ_APPROVAL_REQ, FTVAPPQ_ACTIVITY_DATE, FTVAPPQ_USER_ID)"""
        x = self.db_insert(my_insert, _my_value)
        print(x)

        if self.debug is True:
            print('### ##### insert_into_ftvappq #######')

    def insert_into_foraqus(self, _my_value):
        my_insert = """FORAQUS(FORAQUS_QUEUE_ID,FORAQUS_USER_ID_APPR,FORAQUS_QUEUE_LEVEL,FORAQUS_QUEUE_LIMIT,FORAQUS_EFF_DATE,FORAQUS_NCHG_DATE,FORAQUS_TERM_DATE,FORAQUS_ACTIVITY_DATE,FORAQUS_USER_ID)"""
        x = self.db_insert(my_insert, _my_value)
        print(x)

        if self.debug is True:
            print('### ##### insert_into_foraqus #######')

    def insert_into_foraqrc(self, _my_value):
        my_insert = """FORAQRC(FORAQRC_QUEUE_ID, FORAQRC_DOC_TYPE, FORAQRC_RULE_GROUP, FORAQRC_COAS_CODE, FORAQRC_FTYP_CODE, FORAQRC_FUND_CODE, FORAQRC_ORGN_CODE, FORAQRC_ATYP_CODE, FORAQRC_ACCT_CODE, FORAQRC_ACTIVITY_DATE, FORAQRC_USER_ID, FORAQRC_PROG_CODE) """
        x = self.db_insert(my_insert, _my_value)
        print(x)

        if self.debug is True:
            print('### ##### insert_into_foraqrc #######')

    def get_next_queue_number(self):
        _select = "max(to_number(substr(FTVAPPQ_QUEUE_ID,0,3)))"
        _from = "FTVAPPQ"
        _where = "substr(FTVAPPQ_QUEUE_ID,0,1) in ('0','1','2','3','4','5','6','7','8','9')"
        x = self.db_query(_select, _from, _where, _order_by='', _group_by='', _max_records_returned='')

        if self.debug is True:
            print('### ##### get_next_queue_number #######')
            print('current max queue num:', x[0][0], 'next queue to use:', (x[0][0]+1))

        my_logger.info(f"""'get_next_queue_number', 'current max queue num:',{x[0][0]}, 'next queue to use:', {x[0][0] + 1}""")

        next_queue = x[0][0] + 1

        return next_queue

    def get_approvers_queues(self, approver_current_queue_list):
        x = self.query_foraqus(my_where=f"FORAQUS_USER_ID_APPR = '{approver_current_queue_list}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null", my_order_by='FORAQUS_QUEUE_ID')
        current_approver_queues = [y[0] for y in x]

        if self.debug is True:
            print('### ##### get_approvers_queues #######')

        return approver_current_queue_list, current_approver_queues

    # Procedures

    # # Build Queue Chain
    def build_a_new_queue_chain(self, queue_chain_number, queue_description, queues_to_build, orgns_to_route, bxxx_queue_appr=None):
        # add budget queue Bxxx to queues_to_build for processing
        if bxxx_queue_appr is None:
            budget_queue = ('budget', queues_to_build[2][0], 0, self.budget_approvers)
        else:
            budget_queue = ('budget', queues_to_build[2][0], 0, bxxx_queue_appr)

        queues_to_build.append(budget_queue)

        # build each queue in queue chain
        for que in queues_to_build:
            # build the queue
            the_que = str(queue_chain_number)+que[0] if que[0] != 'budget' else 'B'+str(queue_chain_number)
            exit_que = (que[1] if que[1] in ['VPAS', 'EXBS', 'PRES'] else str(queue_chain_number)+que[1])
            build_queue = f"""'{the_que}','{queue_description}',{que[2]},'{exit_que}', null, sysdate, 'RWALDEN'"""
            print(build_queue)
            self.insert_into_ftvappq(build_queue)

            # add approvers
            for approver in que[3]:
                insert_approvers = f"""'{the_que}', '{approver}', 10, {que[2]}, sysdate, null, null, sysdate, 'RWALDEN'"""
                print(insert_approvers)
                self.insert_into_foraqus(insert_approvers)

            # route orgns to Accounting queue in queue chain
            if que[0] == 'A':
                for orgn in orgns_to_route:
                    req_route_orgn = f"""'{the_que}', 1, 'REQG', 'A', '', '', '{orgn}', '', '', sysdate, 'RWALDEN', ''"""
                    po_route_orgn = f"""'{the_que}', 2, 'CORG', 'A', '', '', '{orgn}', '', '', sysdate, 'RWALDEN', ''"""
                    print(req_route_orgn)
                    print(po_route_orgn)
                    self.insert_into_foraqrc(req_route_orgn)
                    self.insert_into_foraqrc(po_route_orgn)

            # route orgns to Budget queue in queue chain
            if que[0] == 'budget':
                for orgn in orgns_to_route:
                    jv_route_orgn = f"""'{the_que}', 20, 'DBRG', 'A', '', '', '{orgn}', '', '', sysdate, 'RWALDEN', ''"""
                    print(jv_route_orgn)
                    self.insert_into_foraqrc(jv_route_orgn)

        if self.debug is True:
            print('### ##### build_a_new_queue_chain #######')
    # ## EX: Build new queue chain start
    # ## EX: queue_chain_number = 998
    # ## EX: queue_description = 'Test Queue Desc'
    # ## EX: queues_to_build = [('A','B',0,['AMUSIAL1','EOBRIEN3']),('B','G',.01,['KJANISZEWSKI','UGOFF', 'BJESTER1', 'LNOWAK']),('G','EXBS',4999.99,['SMILLER66'])]
    # ## EX: orgns_to_route = ['12345','67890','19283']
    # ## EX: build_a_new_queue_chain(queue_chain_number, queue_description, queues_to_build, orgns_to_route)
    # ## EX: Build new queue chain end

    # # Insert Proxy
    # ## Set Proxy date format '28-JUL-22' == July 28 2022

    # # Set Proxy Approver
    def set_proxy_approver(self, approver_to_proxy, proxy_approver, date_from, date_to):
        x = self.query_foraqus(my_where=f"FORAQUS_USER_ID_APPR = '{approver_to_proxy}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null")
        for y in x:
            insert_term_record = f"""'{y[0]}', '{proxy_approver}', {y[2]}, {y[3]}, '{date_from}', null, '{date_to}', sysdate, 'RWALDEN' """
            self.insert_into_foraqus(insert_term_record)

        if self.debug is True:
            print('### ##### set_proxy_approver #######')
    # ### EX: set_proxy_approver(approver_to_proxy = 'EKNUDSON',proxy_approver = 'RWALDEN',date_from = '22-JUL-22',date_to = '28-JUL-22')

    # # Replace Approver in Queues

    # Replace Approver
    def replace_approver(self, approver_to_place, new_approver, from_queues=()):
        if (len(from_queues) < 1) or (from_queues == ''):
            x = self.query_foraqus(my_where=f"FORAQUS_USER_ID_APPR = '{approver_to_place}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null")
        elif type(from_queues) == str:
            x = self.query_foraqus(my_where=f"FORAQUS_USER_ID_APPR = '{approver_to_place}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null and FORAQUS_QUEUE_ID in ('{from_queues}')")
        else:
            x = self.query_foraqus(my_where=f"FORAQUS_USER_ID_APPR = '{approver_to_place}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null and FORAQUS_QUEUE_ID in {from_queues}")

        for y in x:
            print(y[0], y[1], y[2], y[3], y[4], y[5], y[6])
            my_update = 'FORAQUS'
            my_set = 'FORAQUS_NCHG_DATE = sysdate'
            my_where = f"FORAQUS_USER_ID_APPR = '{approver_to_place}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null and FORAQUS_QUEUE_ID = '{y[0]}'"
            self.db_update(my_update, my_set, my_where)
            # insert term record
            insert_term_record = f"""'{y[0]}', '{y[1]}', {y[2]}, {y[3]}, sysdate, null, sysdate, sysdate, 'RWALDEN' """
            self.insert_into_foraqus(insert_term_record)
            # insert new approver
            insert_term_record = f"""'{y[0]}', '{new_approver}', {y[2]}, {y[3]}, sysdate, null, null, sysdate, 'RWALDEN' """
            self.insert_into_foraqus(insert_term_record)

        if self.debug is True:
            print('### ##### replace_approver #######')
    # ## EX: replace_approver(approver_to_place = 'BJESTER1', new_approver = 'RWALDEN')

    # # Term from queues
    # ## Term Approver date format '28-JUL-22' == July 28 2022
    # ## EX: from_queues = () or '000A' or ('000A') or ('000A','B000','000B') ; all queues , one queue, multiple queues
    def term_approver(self, approver_to_term, term_date, from_queues=()):
        if (len(from_queues) < 1) or (from_queues == ''):
            x = self.query_foraqus(my_where=f"FORAQUS_USER_ID_APPR = '{approver_to_term}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null")
        elif type(from_queues) == str:
            x = self.query_foraqus(my_where=f"FORAQUS_USER_ID_APPR = '{approver_to_term}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null and FORAQUS_QUEUE_ID in ('{from_queues}')")
        else:
            x = self.query_foraqus(my_where=f"FORAQUS_USER_ID_APPR = '{approver_to_term}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null and FORAQUS_QUEUE_ID in {from_queues}")

        for y in x:
            # update next change date in current active record
            my_update = 'FORAQUS'
            my_set = f"FORAQUS_NCHG_DATE = '{term_date}'"
            my_where = f"FORAQUS_USER_ID_APPR = '{approver_to_term}' and FORAQUS_NCHG_DATE is null and FORAQUS_TERM_DATE is null and FORAQUS_QUEUE_ID = '{y[0]}'"
            self.db_update(my_update, my_set, my_where)
            # insert term record
            insert_term_record = f"""'{y[0]}', '{y[1]}', {y[2]}, {y[3]}, sysdate, null, sysdate, sysdate, 'RWALDEN' """
            self.insert_into_foraqus(insert_term_record)

        if self.debug is True:
            print('### ##### term_approver #######')
    # ## EX: term_approver('AMUSIAL1', '28-JUL-22')
    # ## EX: term_approver('AMUSIAL1', '28-JUL-22', from_queues = ('005A'))
    # ## EX: term_approver('AMUSIAL1', '28-JUL-22', from_queues = ('005A','006A'))


    # search for empty queues
    def search_for_mt_queues(self):
        mt_list = []
        _select = f"""distinct foraqus.FORAQUS_QUEUE_ID,
        (select count(FORAQUS_USER_ID_APPR)
        from foraqus fa
        where fa.FORAQUS_QUEUE_ID = foraqus.FORAQUS_QUEUE_ID
                                    and fa.FORAQUS_TERM_DATE is null
                                    and fa.FORAQUS_NCHG_DATE is null) as OtherApprovers"""
        _from = f"""foraqus"""
        _where = f""""""
        _order_by = """2"""
        _group_by = """"""
        _max_records_returned = """"""
        x = self.db_query(_select, _from, _where, _order_by, _group_by, _max_records_returned)
        for y in x:
            if y[1] == 0:
                print('alert', y)
                mt_list.append(y)
            #print(y)
        return mt_list

    def orgn_to_queue(self, orgns):
        _select = f"""distinct FORAQRC_ORGN_CODE, SUBSTR( FORAQRC_QUEUE_ID, 1, 3 )"""
        _from = f"""FORAQRC"""
        _where = f"""FORAQRC_ORGN_CODE in ({orgns}) and SUBSTR( FORAQRC_QUEUE_ID, 1, 1 ) != 'B'"""
        _order_by = f""""""
        _group_by = f""""""
        _max_records_returned = f""""""

        x = self.db_query(_select, _from, _where, _order_by, _group_by, _max_records_returned)
        return x

    def queue_to_orgn(self, orgns):
        _select = f"""distinct FORAQRC_QUEUE_ID, FORAQRC_ORGN_CODE"""
        _from = f"""FORAQRC"""
        _where = f"""FORAQRC_QUEUE_ID in ({orgns})"""
        _order_by = f""""""
        _group_by = f""""""
        _max_records_returned = f""""""

        x = self.db_query(_select,_from,_where,_order_by,_group_by,_max_records_returned)
        return x

class TableBackUp:
    def __init__(self, connection_obj):
        self.name = 'test'
        self.connection_obj = connection_obj  # aqa.OracleConnect()
        self.conn = self.connection_obj.engine_connection
        self.current_dir = os.getcwd()
        self.logs_folder = 'logs'

        self.session_bk_FORAQUS_file_name = ''
        self.session_bk_FORAQRC_file_name = ''
        self.session_bk_FTVAPPQ_file_name = ''

        try:
            os.mkdir('back_ups')
        except:
            print('back_ups file exists in project_root')
        try:
            os.mkdir('back_ups/session_back_ups')
        except:
            print('session_back_ups file exists in back_ups')
        try:
            os.mkdir('back_ups/user_back_ups')
        except:
            print('user_back_ups file exists in back_ups')

    # ### User Back Up Section ###
    def user_back_up_foraqus(self):
        root = tkinter.Tk()
        root.withdraw() # use to hide tkinter window
        FORAQUS_file_name = f"FORAQUS_{date.today()}"
        file = filedialog.asksaveasfile(parent=root, mode='w', defaultextension=".csv", title="Backup FORAQUS Table to CSV", initialdir=self.current_dir, initialfile=FORAQUS_file_name, filetypes=(("comma separated values", "*.csv"), ("all files", "*.*")))
        columns = 'FORAQUS_QUEUE_ID, FORAQUS_USER_ID_APPR, FORAQUS_QUEUE_LEVEL, FORAQUS_QUEUE_LIMIT, FORAQUS_EFF_DATE, FORAQUS_NCHG_DATE, FORAQUS_TERM_DATE, FORAQUS_ACTIVITY_DATE, FORAQUS_USER_ID, FORAQUS_SURROGATE_ID, FORAQUS_VERSION, FORAQUS_DATA_ORIGIN, FORAQUS_VPDI_CODE'
        table_data = self.connection_obj.db_query(columns, 'FORAQUS', '', '', '', '')
        file.write(f"{columns} \n")
        for line in table_data:
            activity_date = line[7].strftime('%d-%b-%y')
            effective_date = line[4].strftime('%d-%b-%y')
            nchg_date = ("'"+line[5].strftime('%d-%b-%y')+"'" if line[5] is not None else None)
            term_date = ("'"+line[6].strftime('%d-%b-%y')+"'" if line[6] is not None else None)
            file.write(f"'{line[0]}','{line[1]}',{line[2]},'{line[3]}','{effective_date}',{nchg_date},{term_date},'{activity_date}','{line[8]}',None,{line[10]},{line[11]},{line[12]} \n")
        file.close()
        return FORAQUS_file_name

    def user_back_up_foraqrc(self):
        root = tkinter.Tk()
        root.withdraw() # use to hide tkinter window
        FORAQRC_file_name = f"FORAQRC_{date.today()}"
        file = filedialog.asksaveasfile(parent=root, mode='w', defaultextension=".csv", title="Backup FORAQRC Table to CSV", initialfile=FORAQRC_file_name, filetypes=(("comma separated values", "*.csv"), ("all files", "*.*")))
        columns = 'FORAQRC_QUEUE_ID, FORAQRC_DOC_TYPE, FORAQRC_RULE_GROUP, FORAQRC_COAS_CODE, FORAQRC_FTYP_CODE, FORAQRC_FUND_CODE, FORAQRC_ORGN_CODE, FORAQRC_ATYP_CODE, FORAQRC_ACCT_CODE, FORAQRC_ACTIVITY_DATE, FORAQRC_USER_ID, FORAQRC_PROG_CODE, FORAQRC_SURROGATE_ID, FORAQRC_VERSION, FORAQRC_DATA_ORIGIN, FORAQRC_VPDI_CODE'
        table_data =  self.connection_obj.db_query(columns,'FORAQRC','','','','')
        file.write(f"{columns} \n")
        for line in table_data:
            act_date = line[9].strftime("%d-%b-%y")
            file.write(f"'{line[0]}',{line[1]},'{line[2]}','{line[3]}',{line[4]},{line[5]},'{line[6]}',{line[7]},{line[8]},'{act_date}','{line[10]}',{line[11]},{line[12]},{line[13]},{line[14]},{line[15]} \n")
            #break
        file.close()
        return FORAQRC_file_name

    def user_back_up_ftvappq(self):
        root = tkinter.Tk()
        root.withdraw() # use to hide tkinter window
        FTVAPPQ_file_name = f"FTVAPPQ_{date.today()}"
        file = filedialog.asksaveasfile(parent=root, mode='w', defaultextension=".csv", title="Backup FTVAPPQ Table to CSV", initialfile=FTVAPPQ_file_name, filetypes=(("comma separated values", "*.csv"), ("all files", "*.*")))
        columns = 'FTVAPPQ_QUEUE_ID, FTVAPPQ_DESCRIPTION, FTVAPPQ_QUEUE_LIMIT, FTVAPPQ_NEXT_QUEUE_ID, FTVAPPQ_APPROVAL_REQ, FTVAPPQ_ACTIVITY_DATE, FTVAPPQ_USER_ID, FTVAPPQ_SURROGATE_ID, FTVAPPQ_DATA_ORIGIN, FTVAPPQ_VERSION, FTVAPPQ_VPDI_CODE'
        table_data =  self.connection_obj.db_query(columns,'FTVAPPQ','','','','')
        file.write(f"{columns} \n")
        for line in table_data:
            act_date = line[5].strftime('%d-%b-%y')
            file.write(f"'{line[0]}','{line[1]}',{line[2]},'{line[3]}','{line[4]}','{act_date}','{line[6]}',{line[7]},{line[8]},{line[9]},{line[10]} \n")
        file.close()
        return FTVAPPQ_file_name

    # ### User Restore Section ###
    def user_restore_foraqus(self):
        print(self.name, 'foraqus')
        root = tkinter.Tk()
        root.withdraw()  # use to hide tkinter window
        currdir = os.getcwd()
        tempfile = filedialog.askopenfilename(parent=root, initialdir=currdir, title='Please select a FORAQUS file to restore from')
        if len(tempfile) > 0:
            print("You chose: %s" % tempfile)

        with self.conn.cursor() as _cur:
            _cur.execute('TRUNCATE TABLE FIMSMGR.FORAQUS')

        with open(f"{tempfile}", "r") as file:
            my_insert = 'FORAQUS(FORAQUS_QUEUE_ID, FORAQUS_USER_ID_APPR, FORAQUS_QUEUE_LEVEL, FORAQUS_QUEUE_LIMIT, FORAQUS_EFF_DATE, FORAQUS_NCHG_DATE, FORAQUS_TERM_DATE, FORAQUS_ACTIVITY_DATE, FORAQUS_USER_ID, FORAQUS_SURROGATE_ID, FORAQUS_VERSION, FORAQUS_DATA_ORIGIN, FORAQUS_VPDI_CODE)'
            for i, line in enumerate(file):
                print(line.replace('None', 'null').replace("'null'", 'null'))
                if i > 0:
                    my_values = line.replace('None','null').replace("'null'", 'null')
                    _result = self.connection_obj.db_insert(my_insert, my_values)
                    print(_result)

        return tempfile

    def user_restore_foraqrc(self):
        print(self.name)
        root = tkinter.Tk()
        root.withdraw()  # use to hide tkinter window
        currdir = os.getcwd()
        tempfile = filedialog.askopenfilename(parent=root, initialdir=currdir, title='Please select a FORAQRC file to restore from')

        with self.conn.cursor() as _cur:
            _cur.execute('TRUNCATE TABLE FIMSMGR.FORAQRC')

        with open(f"{tempfile}", "r") as file:
            my_insert = 'FORAQRC(FORAQRC_QUEUE_ID, FORAQRC_DOC_TYPE, FORAQRC_RULE_GROUP, FORAQRC_COAS_CODE, FORAQRC_FTYP_CODE, FORAQRC_FUND_CODE, FORAQRC_ORGN_CODE, FORAQRC_ATYP_CODE, FORAQRC_ACCT_CODE, FORAQRC_ACTIVITY_DATE, FORAQRC_USER_ID, FORAQRC_PROG_CODE, FORAQRC_SURROGATE_ID, FORAQRC_VERSION, FORAQRC_DATA_ORIGIN, FORAQRC_VPDI_CODE)'
            for i, line in enumerate(file):
                print(line.replace('None', 'null').replace("'null'", 'null'))
                if i > 0:
                    my_values = line.replace('None', 'null').replace("'null'", 'null')
                    _result = self.connection_obj.db_insert(my_insert, my_values)
                    print(_result)

    def user_restore_ftvappq(self):
        print(self.name)
        root = tkinter.Tk()
        root.withdraw()  # use to hide tkinter window
        currdir = os.getcwd()
        tempfile = filedialog.askopenfilename(parent=root, initialdir=currdir, title='Please select a FTVAPPQ file to restore from')

        with self.conn.cursor() as _cur:
            _cur.execute('TRUNCATE TABLE FIMSMGR.FTVAPPQ')

        with open(f"{tempfile}", "r") as file:
            my_insert = 'FTVAPPQ(FTVAPPQ_QUEUE_ID, FTVAPPQ_DESCRIPTION, FTVAPPQ_QUEUE_LIMIT, FTVAPPQ_NEXT_QUEUE_ID, FTVAPPQ_APPROVAL_REQ, FTVAPPQ_ACTIVITY_DATE, FTVAPPQ_USER_ID, FTVAPPQ_SURROGATE_ID, FTVAPPQ_DATA_ORIGIN, FTVAPPQ_VERSION, FTVAPPQ_VPDI_CODE)'
            for i, line in enumerate(file):
                print(line.replace('None', 'null').replace("'null'", 'null'))
                if i > 0:
                    my_values = line.replace('None', 'null').replace("'null'", 'null')
                    _result = self.connection_obj.db_insert(my_insert, my_values)
                    print(_result)

    # ### Session Back Up Section ###
    def session_back_up_foraqus(self, session_backup_folder='back_ups/session_back_ups'):
        FORAQUS_file_name = f"FORAQUS_{date.today()}"
        file_dir_name = f"""{session_backup_folder}/{FORAQUS_file_name}"""
        print(file_dir_name)
        with open(f"{file_dir_name}.csv", "w") as file:
            columns = 'FORAQUS_QUEUE_ID, FORAQUS_USER_ID_APPR, FORAQUS_QUEUE_LEVEL, FORAQUS_QUEUE_LIMIT, FORAQUS_EFF_DATE, FORAQUS_NCHG_DATE, FORAQUS_TERM_DATE, FORAQUS_ACTIVITY_DATE, FORAQUS_USER_ID, FORAQUS_SURROGATE_ID, FORAQUS_VERSION, FORAQUS_DATA_ORIGIN, FORAQUS_VPDI_CODE'
            table_data =  self.connection_obj.db_query(columns,'FORAQUS','','','','')
            file.write(f"{columns} \n")
            for line in table_data:
                activity_date = line[7].strftime('%d-%b-%y')
                effective_date = line[4].strftime('%d-%b-%y')
                nchg_date = ("'"+line[5].strftime('%d-%b-%y')+"'" if line[5] is not None else None)
                term_date = ("'"+line[6].strftime('%d-%b-%y')+"'" if line[6] is not None else None)
                file.write(f"'{line[0]}','{line[1]}',{line[2]},'{line[3]}','{effective_date}',{nchg_date},{term_date},'{activity_date}','{line[8]}',None,{line[10]},{line[11]},{line[12]} \n")
        return FORAQUS_file_name

    def session_back_up_foraqrc(self, session_backup_folder='back_ups/session_back_ups'):
        FORAQRC_file_name = f"FORAQRC_{date.today()}"
        file_dir_name  = f"""{session_backup_folder}/{FORAQRC_file_name}"""
        with open(f"{file_dir_name}.csv", "w") as file:
            columns = 'FORAQRC_QUEUE_ID, FORAQRC_DOC_TYPE, FORAQRC_RULE_GROUP, FORAQRC_COAS_CODE, FORAQRC_FTYP_CODE, FORAQRC_FUND_CODE, FORAQRC_ORGN_CODE, FORAQRC_ATYP_CODE, FORAQRC_ACCT_CODE, FORAQRC_ACTIVITY_DATE, FORAQRC_USER_ID, FORAQRC_PROG_CODE, FORAQRC_SURROGATE_ID, FORAQRC_VERSION, FORAQRC_DATA_ORIGIN, FORAQRC_VPDI_CODE'
            table_data =  self.connection_obj.db_query(columns,'FORAQRC','','','','')
            #print(len(x))
            file.write("'FORAQRC_QUEUE_ID', 'FORAQRC_DOC_TYPE', 'FORAQRC_RULE_GROUP', 'FORAQRC_COAS_CODE', 'FORAQRC_FTYP_CODE', 'FORAQRC_FUND_CODE', 'FORAQRC_ORGN_CODE', 'FORAQRC_ATYP_CODE', 'FORAQRC_ACCT_CODE', 'FORAQRC_ACTIVITY_DATE', 'FORAQRC_USER_ID', 'FORAQRC_PROG_CODE', 'FORAQRC_SURROGATE_ID', 'FORAQRC_VERSION', 'FORAQRC_DATA_ORIGIN', 'FORAQRC_VPDI_CODE' \n")
            for line in table_data:
                act_date = line[9].strftime("%d-%b-%y")
                file.write(f"'{line[0]}',{line[1]},'{line[2]}','{line[3]}',{line[4]},{line[5]},'{line[6]}',{line[7]},{line[8]},'{act_date}','{line[10]}',{line[11]},{line[12]},{line[13]},{line[14]},{line[15]} \n")
                #break
        return FORAQRC_file_name

    def session_back_up_ftvappq(self, session_backup_folder='back_ups/session_back_ups'):
        FTVAPPQ_file_name = f"FTVAPPQ_{date.today()}"
        file_dir_name  = f"""{session_backup_folder}/{FTVAPPQ_file_name}"""
        with open(f"{file_dir_name}.csv", "w") as file:
            columns = 'FTVAPPQ_QUEUE_ID, FTVAPPQ_DESCRIPTION, FTVAPPQ_QUEUE_LIMIT, FTVAPPQ_NEXT_QUEUE_ID, FTVAPPQ_APPROVAL_REQ, FTVAPPQ_ACTIVITY_DATE, FTVAPPQ_USER_ID, FTVAPPQ_SURROGATE_ID, FTVAPPQ_DATA_ORIGIN, FTVAPPQ_VERSION, FTVAPPQ_VPDI_CODE'
            table_data =  self.connection_obj.db_query(columns,'FTVAPPQ','','','','')
            file.write(f"{columns} \n")
            for line in table_data:
                act_date = line[5].strftime('%d-%b-%y')
                file.write(f"'{line[0]}','{line[1]}',{line[2]},'{line[3]}','{line[4]}','{act_date}','{line[6]}',{line[7]},{line[8]},{line[9]},{line[10]} \n")
        return FTVAPPQ_file_name

    # ### Session Restore Section ###
    def session_restore_foraqus(self, FORAQUS_file_name):
        with open(f"session_back_ups/{FORAQUS_file_name}.csv", "r") as file:
            my_insert = 'FORAQUS(FORAQUS_QUEUE_ID, FORAQUS_USER_ID_APPR, FORAQUS_QUEUE_LEVEL, FORAQUS_QUEUE_LIMIT, FORAQUS_EFF_DATE, FORAQUS_NCHG_DATE, FORAQUS_TERM_DATE, FORAQUS_ACTIVITY_DATE, FORAQUS_USER_ID, FORAQUS_SURROGATE_ID, FORAQUS_VERSION, FORAQUS_DATA_ORIGIN, FORAQUS_VPDI_CODE)'
            for i, line in enumerate(file):
                print(line.replace('None', 'null').replace("'null'", 'null'))
                if i > 0:
                    my_values = line.replace('None', 'null').replace("'null'", 'null')
                    _result = self.connection_obj.db_insert(my_insert, my_values)
                    print(_result)

    def session_restore_foraqrc(self, FORAQRC_file_name):
        with open(f"session_back_ups/{FORAQRC_file_name}.csv", "r") as file:
            my_insert = 'FORAQRC(FORAQRC_QUEUE_ID, FORAQRC_DOC_TYPE, FORAQRC_RULE_GROUP, FORAQRC_COAS_CODE, FORAQRC_FTYP_CODE, FORAQRC_FUND_CODE, FORAQRC_ORGN_CODE, FORAQRC_ATYP_CODE, FORAQRC_ACCT_CODE, FORAQRC_ACTIVITY_DATE, FORAQRC_USER_ID, FORAQRC_PROG_CODE, FORAQRC_SURROGATE_ID, FORAQRC_VERSION, FORAQRC_DATA_ORIGIN, FORAQRC_VPDI_CODE)'
            for i, line in enumerate(file):
                print(line.replace('None', 'null').replace("'null'", 'null'))
                if i > 0:
                    my_values = line.replace('None', 'null').replace("'null'", 'null')
                    _result = self.connection_obj.db_insert(my_insert, my_values)
                    print(_result)

    def session_restore_ftvappq(self, FTVAPPQ_file_name):
        with open(f"session_back_ups/{FTVAPPQ_file_name}.csv", "r") as file:
            my_insert = 'FTVAPPQ(FTVAPPQ_QUEUE_ID, FTVAPPQ_DESCRIPTION, FTVAPPQ_QUEUE_LIMIT, FTVAPPQ_NEXT_QUEUE_ID, FTVAPPQ_APPROVAL_REQ, FTVAPPQ_ACTIVITY_DATE, FTVAPPQ_USER_ID, FTVAPPQ_SURROGATE_ID, FTVAPPQ_DATA_ORIGIN, FTVAPPQ_VERSION, FTVAPPQ_VPDI_CODE)'
            for i, line in enumerate(file):
                print(line.replace('None', 'null').replace("'null'", 'null'))
                if i > 0:
                    my_values = line.replace('None', 'null').replace("'null'", 'null')
                    _result = self.connection_obj.db_insert(my_insert, my_values)
                    print(_result)

    # #####
    def perform_session_backup(self):
        self.session_bk_FORAQUS_file_name = self.session_back_up_foraqus()

        self.session_bk_FORAQRC_file_name = self.session_back_up_foraqrc()

        self.session_bk_FTVAPPQ_file_name = self.session_back_up_ftvappq()

    def perform_session_restore(self):
        with self.conn.cursor() as _cur:
            _cur.execute('TRUNCATE TABLE FIMSMGR.FORAQUS')
        print(self.session_bk_FORAQUS_file_name)
        self.session_restore_foraqus(self.session_bk_FORAQUS_file_name)


        with self.conn.cursor() as _cur:
            _cur.execute('TRUNCATE TABLE FIMSMGR.FORAQRC')
        print(self.session_bk_FORAQRC_file_name)
        self.session_restore_foraqrc(self.session_bk_FORAQRC_file_name)


        with self.conn.cursor() as _cur:
            _cur.execute('TRUNCATE TABLE FIMSMGR.FTVAPPQ')
        print(self.session_bk_FTVAPPQ_file_name)
        self.session_restore_ftvappq(self.session_bk_FTVAPPQ_file_name)


# add current date and format return
# add check for empty queues - queues with no approvers
# build class to build new queue layout

#%%
