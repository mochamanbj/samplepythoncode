import sys
from utils import db_utils, file_utils
from config import settings
from optparse import OptionParser
import logging
log = logging.getLogger('PM')

from models import sometbl1, sometbl2, sometbl3, sometbl4, sometbl4

def usage(argv):
    print 'Usage: %s -a <data3_id> -j <jira ticket>\nExample:  %s -a 2343 -j CIB-134 (no spaces)' % (argv[0], argv[0])
    sys.exit(1)    
    
def parse_arguments(arguments):
    parser = OptionParser()

    parser.add_option("-a", "--data3_id", type="string",
                      dest="data3_id",
                      default=None,
                      help="data3_id to blacklist")
#    parser.add_option("-f", "--first_name", type="string",
#                      dest="first_name",
#                      default=None,
#                      help="first_name of data3 to blacklist")
#    parser.add_option("-l", "--last_name", type="string",
#                      dest="last_name",
#                      default=None,
#                      help="last_name of data3 to blacklist")
    parser.add_option("-j", "--jira_ticket", type="string",
                      dest="jira_ticket",
                      default=None,
                      help="jira_ticket for the blacklist request (ex:CIB-134)")

    (blklist_options, arguments) = parser.parse_args()

    return blklist_options

def run_update_queries(conn, data3_id, data2_id):
    u_cursor=conn.cursor()
    
    update_data2_table_query = """
        UPDATE `%s` SET
        `first_name` = 'BLACKLISTED',
        `middle_name` = 'BLACKLISTED',
        `last_name` = 'BLACKLISTED',
        `updated_at` = NOW()
        WHERE id = %s
        """ % (sometbl2.table_name, data2_id)

    pt_count = u_cursor.execute(update_data2_table_query)

    update_data2identifiers_table_query = """
        UPDATE `%s` SET
        `value` = 'BLACKLISTED',
        `eligibility_import_id` = -1,
        `updated_at` = NOW()
        WHERE `data2_id` = %s
        """ % (sometbl4.table_name, data2_id)

    pi_count = u_cursor.execute(update_data2identifiers_table_query)

    update_eprd_table_query = """
        UPDATE `%s` SET
        `first_name` = 'BLACKLISTED',
        `middle_name` = 'BLACKLISTED',
        `last_name` = 'BLACKLISTED',
        `reserved_field_1` = NULL,
        `reserved_field_2` = NULL,
        `reserved_field_3` = NULL,
        `reserved_field_4` = NULL,
        `reserved_field_5` = NULL, 
        WHERE data2_id = %s
        """ % (sometbl1.eprd_table_name, data2_id)
        
    eprd_count = u_cursor.execute(update_eprd_table_query)
   
    update_sometbl3_table_query = """
        UPDATE `%s` SET
        `email` = 'BLACKLISTED',
        `updated_at` = NOW()
        WHERE data2_id = %s
        """ % (sometbl3.table_name, data2_id)

    acct_count = u_cursor.execute(update_sometbl3_table_query)
    
    update_data3attributes_table_query = """
        UPDATE `%s` aa 
        JOIN `%s` a ON a.id=aa.data3_id 
        SET
            aa.`value` = 'BLACKLISTED',
            aa.`updated_at` = NOW()
        WHERE a.`data2_id` = %s
        """ % (sometbl4.table_name,sometbl3.table_name, data2_id)

    aa_count = u_cursor.execute(update_data3attributes_table_query)
    
    log.info("Updated %s rows in sometbl2 table" % pt_count)
    log.info("Updated %s rows in sometbl4 table" % pi_count)
    log.info("Updated %s rows in sometbl3 table" % acct_count)
    log.info("Updated %s rows in sometbl1 table" % eprd_count)
    
def update_blklist_tbl(conn, data2_id, data1, jira_ticket):
    b_cursor = conn.cursor()
    insert_bl_query = """INSERT INTO `sometbl5` (data2_id, data1, description) VALUES (%s,'%s', 'See JIRA %s')""" % (data2_id, data1, jira_ticket)
    b_cursor.execute(insert_bl_query)


def clear_blacklisted_data(data3_id, jira_ticket):
    
    conn = db_utils.get_data2_master_conn()
    cursor = conn.cursor()
    
    get_data2_id_query = "SELECT data2_id FROM wh_sometbl3 WHERE id=%s" % data3_id
    cursor.execute(get_data2_id_query)
    data2id_row = cursor.fetchone()
    if data2id_row:
        data2_id = data2id_row['data2_id']
    else:
        log.info("Invalid Account ID provided, please verify and try again")
        sys.exit(0)
        
    get_data2_data1_query = "SELECT first_name, last_name FROM wh_sometbl2 WHERE id=%s" % data2_id
    cursor.execute(get_data2_data1_query)
    pt_row = cursor.fetchone()
    
    data1 = str(pt_row['data1'])
    db_firstname = pt_row['first_name']
    db_lastname = pt_row['last_name']
    
    verify_input = raw_input("Please confirm BLACKLISTING of: %s %s (data3_id=%s).  Enter Yes or No\n" % (db_firstname, db_lastname, data3_id))
    if verify_input.lower() in ['y','yes']:
        log.info("Confirmed blacklisting of: %s %s (data3_id=%s)" %(db_firstname,db_lastname,data3_id))
        run_update_queries(conn, data3_id, data2_id)
        update_blklist_tbl(conn, data2_id, data1, jira_ticket)
        conn.commit()
        log.debug("SUCCESS:  Blacklisted complete for %s %s" % (db_firstname, db_lastname))
    
    else:
        raise Exception("Please correct data3_id and try again")
    
def main(argv):
    file_utils.set_logger('blacklisting')
    try:
        args = parse_arguments(argv)
    except Exception, e:
        print "ERROR: %s" % str(e)
        return usage(argv)
    
    if args.data3_id == None or args.jira_ticket == None:
            return usage(argv)
    else:
        clear_blacklisted_data(args.data3_id, args.jira_ticket)
        
if __name__ == '__main__':
    main(sys.argv)
