import sys,datetime,os
sys.path.append(".")
sys.path.append("..")
from optparse import OptionParser
from config import settings
from utils import db_utils
from models import eligible_patient_record_dim

parser = OptionParser()
parser.add_option("-e", "--employer_id", type="string", dest="employer_id",  default=None, help="employer id for this test account")
parser.add_option("-p", "--plan_code", type="string", dest="plan_code", default=None, help="plan_code for this account")
parser.add_option("-i", "--insurance_carrier", type="string", dest="insurance_carrier", default=None, help="insurance_carrier for this account")
parser.add_option("-c", "--coverage_tier", type="string", dest="coverage_tier", default=None, help="coverage_tier for this account")
parser.add_option("-m", "--email", type="string", dest="email", default=None, help="email address for this account")
parser.add_option("-y", "--city", type="string", dest="city", default='San Francisco', help="city for this account")
parser.add_option("-t", "--state", type="string", dest="state", default='CA', help="state for this account")
parser.add_option("-z", "--zipcode", type="string", dest="zip", default='94123', help="zip for this account")
parser.add_option("-o", "--optional_values", type="string", dest="optional_values", default=None, help="comma separated list of 'field=value' pairs")
                  
(testaccount_options, args) = parser.parse_args()

tmp_dir = '/tmp/test_accounts'

#TODO    1.  read from file to add more than one user
#        2.  ability to add other fields via list

class TestAccountRecord:
    
    def __init__(self,record=None):
        self.indicator = record.get('indicator') if record is not None else ''
        self.first_name = record.get('first_name') if record is not None else 'test'
        self.middle_name = record.get('middle_name') if record is not None else ''
        self.last_name = record.get('last_name') if record is not None else 'test_name'
        self.ssn = record.get('ssn') if record is not None else ''
        self.date_of_birth = record.get('date_of_birth') if record is not None else ''
        self.gender = record.get('gender') if record is not None else 'M'
        self.relationship_code  = record.get('relationship_code') if record is not None else ''
        self.subscriber_ssn = record.get('subscriber_ssn') if record is not None else ''
        self.address_line_1 = record.get('address_line_1') if record is not None else ''
        self.address_line_2 = record.get('address_line_2') if record is not None else ''
        self.city = record.get('city') if record is not None else testaccount_options.city
        self.state = record.get('state') if record is not None else testaccount_options.state
        self.zip = record.get('zip') if record is not None else testaccount_options.zip
        self.phone_number = record.get('phone_number') if record is not None else ''
        self.email = record.get('email') if record is not None else ''
        self.member_number = record.get('member_number') if record is not None else ''
        self.employee_dependent_number = record.get('employee_dependent_number') if record is not None else ''
        self.employment_effective_date = record.get('employment_effective_date') if record is not None else ''
        self.employment_termination_date = record.get('employment_termination_date') if record is not None else ''
        self.employment_status_code = record.get('employment_status_code') if record is not None else ''
        self.retirement_date = record.get('retirement_date') if record is not None else ''
        self.insurance_carrier_code = record.get('insurance_carrier_code') if record is not None else testaccount_options.insurance_carrier
        self.plan_code = record.get('plan_code') if record is not None else testaccount_options.plan_code
        self.health_plan_coverage_effective_date = record.get('health_plan_coverage_effective_date') if record is not None else ''
        self.health_plan_coverage_termination_date = record.get('health_plan_coverage_termination_date') if record is not None else ''
        self.coverage_tier_code = record.get('coverage_tier_code') if record is not None else testaccount_options.coverage_tier
        self.coverage_tier_effective_date = record.get('coverage_tier_effective_date') if record is not None else ''
        self.pharmacy_plan_code = record.get('pharmacy_plan_code') if record is not None else ''
        self.flag_1 = record.get('flag_1') if record is not None else ''
        self.flag_2 = record.get('flag_2') if record is not None else ''
        self.flag_3 = record.get('flag_3') if record is not None else ''
        self.flag_4 = record.get('flag_4') if record is not None else ''
        self.flag_5 = record.get('flag_5') if record is not None else ''
        self.flag_other = record.get('flag_other') if record is not None else ''
        
    def __repr__(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (self.indicator,self.first_name,self.middle_name,self.last_name,self.ssn,self.date_of_birth,self.gender,self.relationship_code,self.subscriber_ssn,self.address_line_1,self.address_line_2,self.city,self.state,self.zip,self.phone_number,self.email,self.member_number,self.employee_dependent_number,self.employment_effective_date,self.employment_termination_date,self.employment_status_code,self.retirement_date,self.insurance_carrier_code,self.plan_code,self.health_plan_coverage_effective_date,self.health_plan_coverage_termination_date,self.coverage_tier_code,self.coverage_tier_effective_date,self.pharmacy_plan_code,self.flag_1,self.flag_2,self.flag_3,self.flag_4,self.flag_5,self.flag_other)

def usage(error_field):
    print "Required field missing: %s" % error_field
    print "python create_test_accounts.py -e <employer id> -p <plan code> -i <insurance carrier> -c <coverage tier> -m <email address>"
    
def get_max_testaccount_ssn():
    conn = db_utils.get_conn(settings.db_host, settings.db_user, settings.db_password, settings.db_schema)
    cursor = conn.cursor()
    query = "SELECT max(ssn) AS 'ssn' FROM `%s` WHERE `ssn` BETWEEN 999000001 AND 999004718" % (eligible_patient_record_dim.eprd_table_name)
    cursor.execute(query)
    for row in cursor:
#TODO -- handle null results better 
        max_ssn = row['ssn'] if row['ssn'] is not None else ''
    return int(max_ssn) + 1

def set_email(email_entered,relationship):
    ent_email = email_entered.split('@')
    if relationship == 'SP':
        em = ent_email[0] + '_chris@something.com'
    elif relationship == 'CH':
        em = ent_email[0] + '_morgan@something.com' 
    else:
        em = ent_email[0] + '@something.com'
    return em

def set_effective_date():
    year = datetime.datetime.today().year
    return str(year) + "0101"

def set_date_of_birth(relationship):
    if relationship == 'SP':
        dob = '19910101'
    elif relationship == 'CH':
        dob = '19990101'
    else:
        dob = '19900101'
    return dob

def exception_handle(exc,val):
    print "%s: %s" % (exc,val)
            
def set_optional_values(record,optional_vals):
    list_of_optvals = optional_vals.split(',')
    for optval in list_of_optvals:
        rec_index,rec_val = optval.split('=')
        try:
            setattr(record, rec_index, rec_val)
        except Exception, e:
            raise Exception(e)
                    
    return record

def create_record(sub_ssn, ssn, indicator,relationship):
    new_record = TestAccountRecord()
    email = set_email(testaccount_options.email,relationship)
    covg_eff_date = set_effective_date()
    dob = set_date_of_birth(relationship)
    
    new_record.indicator = indicator
    new_record.subscriber_ssn = sub_ssn
    new_record.ssn = ssn
    new_record.email = email
    new_record.health_plan_coverage_effective_date = covg_eff_date
    new_record.date_of_birth = dob
    new_record.relationship_code = relationship
    if testaccount_options.optional_values:
        new_record = set_optional_values(new_record,testaccount_options.optional_values)
    
    return new_record
    
def main():
    new_record = []
    sub_ssn = get_max_testaccount_ssn()
    new_record.append(create_record(sub_ssn, sub_ssn, 'SUB','SE'))
    if testaccount_options.coverage_tier in ('ES','EF'):
        new_record.append(create_record(sub_ssn,sub_ssn+1,'DEP','SP'))
    if testaccount_options.coverage_tier in ('EC','EF'):
        new_record.append(create_record(sub_ssn,sub_ssn+2,'DEP','CH'))
        
    print new_record[0]
    if len(new_record)>1:
        print new_record[1] 
    if len(new_record)>2:
        print new_record[2]
            
if __name__ == "__main__":
    if  '@' not in testaccount_options.email:
        error = "email address"
        usage(error)
        sys.exit(0)
    elif not testaccount_options.employer_id:
        error = "employer id"
        usage(error)
        sys.exit(0)
    elif not testaccount_options.insurance_carrier:
        error = "insurance carrier"
        usage(error)
        sys.exit(0)
    elif not testaccount_options.coverage_tier or (testaccount_options.coverage_tier not in ('EO','ES','EC','EF')):
        error = "coverage_tier (valid values: EO/ES/EC/EF)"
        usage(error)
        sys.exit(0)
    elif not testaccount_options.plan_code:
        error = "plan code"
        usage(error)
        sys.exit(0)
    else:
        main()
