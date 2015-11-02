"""
batch_ingest_physician_payments for Medical Payment Analytics

Usage:

Options:

Examples:

    ./batch_ingest_physician_payments.py

License:

Copyright (c) 2015 Sebastien Dery

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
"""

import csv
import MySQLdb
import logging

def loginfo(app='default',msg=''):
	logging.info("%s >> INFO: %s" % (app, msg))

def logwarning(app='default',msg=''):
	logging.info("%s >> WARNING: %s" % (app, msg))

def logerror(app='default',msg=''):
	logging.info("%s >> ERROR: %s" % (app, msg))

class batch_ingest_physician_payments(object):

	"""
	# Initiate useful variable and constant used in the scope of this demo
	# 
	"""
	def __init__(self, filename):
		self.filename = filename
		
		# Assuming these information are stored and encrypted someplace safe
		self.user = "root"
		self.password = "mysqldatabaseissomuchfun"
		self.host = "localhost"

		# SQL interactions
		self.INSERT_INTO_PHYSICIAN_PAYMENTS = """INSERT INTO physician_payments (record_id, physician_profile_id, physician_first_name, physician_last_name, recipient_state, total_amount, manufacturer) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

		# Useful constant for the scope of this project
		Covered_Recipient_Type_Index = 0
		self.Physician_Profile_ID_Index = 4
		self.Physician_First_Name_Index = 5
		self.Physician_Middle_Name_Index = 6
		self.Physician_Last_Name_Index = 7
		self.Physician_Name_Suffix_Index = 8
		self.Recipient_State_Index = 12
		self.Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_State_Index = 124
		self.Total_Amount_of_Payment_USDollars_Index = 145
		self.Record_ID_Index = 158

		self.appname = "batch_ingest_physician_payments"

		logging.basicConfig(filename='batchprocess.log', level=logging.INFO, \
							format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


	"""
	# Launched the task of ingesting the data from a specified .csv file into
	# the database passed in parameter. The whole step assumes everything is in place
	# and in an adequate format
	#
	"""
	def start(self, database):
		# 
		loginfo(self.appname, "Starting process")
		database = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=database)
		with database:
			loginfo(self.appname, "Connected to the database")
			# Get the cursor, which is used to traverse the database, line by line
			cursor = database.cursor()

			loginfo(self.appname, "Opening raw data file")
			with open(filename,'r') as csvfile:
				# Determine best parsing strategy
				dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=" ;,")
				csvfile.seek(0)
				reader = csv.reader(csvfile, dialect)

				# 
				for i, row in enumerate(reader):

					# Regular commits are made to the database
					if i > 0 and i % 1000 == 0:
						print "Currently parsing row %i" % i
						loginfo(self.appname, "Parsing row %i" % i)
						database.commit()

					Covered_Recipient_Type = str.lower(row[self.Covered_Recipient_Type_Index])
					
					# Assuming the valid category contains the word physician (i.e. not hospitals)
					if Covered_Recipient_Type.find('physician') > 0:
						
						# Assuming all state are correctly writen
						Recipient_State = str.lower(row[self.Recipient_State_Index])
						
						# Assuming the data is already in adequate format for casting
						Total_Amount_of_Payment_USDollars = float(row[self.Total_Amount_of_Payment_USDollars_Index])
						
						# Gather data without any verification under the assumption that everything is great
						record_id = row[self.Record_ID_Index]
						physician_profile = row[self.Physician_Profile_ID_Index]
						physician_first_name = row[self.Physician_First_Name_Index]
						physician_last_name = row[self.Physician_Last_Name_Index]
						recipient_state = row[self.Recipient_State_Index]
						total_amount = row[self.Total_Amount_of_Payment_USDollars_Index]
						manufacturer = row[self.Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_State_Index]
						
						# Insert into database
						cursor.execute(self.INSERT_INTO_PHYSICIAN_PAYMENTS, \
							(record_id, \
							physician_profile, \
							physician_first_name, \
							physician_last_name, \
							recipient_state, \
							total_amount, \
							manufacturer))

			# Final commit
			loginfo(self.appname, "Process final commit to database ")
			database.commit()

		loginfo(self.appname, "Process ended succesfully")


"""
# Currently run manually, the main function needs to be implemented for proper
# calls to be made outside a python context
#
def main(argv):
    
if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
"""


# Test on a smaller dataset and manually verify on the database or make 
# subsequent SELECT call to validate
process = batch_ingest_physician_payments('data.test')
process.start()



