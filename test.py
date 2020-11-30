import pandas as pd
import numpy as np
from pprint import pprint

import os
import shutil
import psycopg2
import pyodbc


def connect_db_credit_score():
    db_host = "172.16.30.240"
    port = 5432
    db_name = "credit_score"
    user = "credit_score"
    password = "lbHoKPMYyuc5LO4z"

    conn = psycopg2.connect(host=db_host, port=port, database=db_name, user=user, password=password)
    return conn


def connect_db_mecash_sql_server():

    conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                          "Server=42.112.23.25;"
                          "Database=Mecash;"
                          "UID=BigData;"
                          "PWD={-bZW[Bh*wdQ#>5('Nw;CL9h[9W\\qf\\y\"}")
    return conn


def query_db(conn, sql_query):
    result = pd.read_sql(sql_query, conn)
    return result


if __name__ == '__main__':
    conn_credit = connect_db_credit_score()
    conn_mecash = connect_db_mecash_sql_server()

    day_1 = "'2020-06-01'"
    day_2 = "'2020-10-01'"
    sth = "'month'"

    query_credit = 'select distinct on (loan.id) loan.id as loan_id, ' \
                   f'date_part({sth}, score.updated_at) as month_updated, loan."FromDate", loan."TotalMoney" ' \
                   'from (' \
                   '    select * ' \
                   'from daily_credit_scoring_transformer ' \
                   f'where updated_at >= {day_1} ' \
                   f'and updated_at <= {day_2} ' \
                   'and score >= 970 ' \
                   'and label_risk_lv1 is False ' \
                   'order by updated_at ' \
                   ') score ' \
                   'inner join history_loan_enrichment loan ' \
                   'on score."LoanID" = loan.id ' \
                   'order by loan.id'

    df_credit = query_db(conn_credit, query_credit)

    loan_ids = df_credit['loan_id'].values

    query_mecash = "select loan.LoanID as loan_id, loan_return.sum_paid " \
                   "from ( " \
                   "select LoanID, sum(MoneyAdd-MoneySub) as sum_paid " \
                   "from tblTransactionLoan " \
                   f"where LoanID in {tuple(loan_ids)} " \
                   "and ActionID not in (1, 14, 18, 28) " \
                   "group by LoanID) loan_return " \
                   "inner join tblLoanCredit loan on loan.LoanID = loan_return.LoanID " \
                   "order by loan.LoanID"

    df_mecash = query_db(conn_mecash, query_mecash)

    merge_df = pd.merge(df_credit, df_mecash, how='left', on='loan_id')
    merge_df = merge_df.replace(np.NaN, 0)
    merge_df['profit'] = merge_df['sum_paid'] - merge_df['TotalMoney']
    print(merge_df)

    print(merge_df[['month_updated', 'profit']].groupby('month_updated').sum())