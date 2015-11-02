import json
import imp
import random
import math
import os

import MySQLdb

from flask import Flask
from flask import render_template
from flask import request
app = Flask(__name__)

@app.route("/")
def hello():
	return render_template('index.html')

@app.route("/video/")
def videos():
	return render_template('video.html')

@app.route("/slides/")
def slides():
	return render_template('slides.html')


###############################
#          Utilities          #
###############################

def getPath(folder):
	APP_ROOT = os.path.dirname(os.path.abspath(__file__))
	APP_STATIC = os.path.join(APP_ROOT, )
	return APP_STATIC


#####################
#   Company Query   #
#####################
@app.route("/company_query/", methods=['POST', 'GET'])
def company_query():

	# Input sanity checks
	search_term = request.args.get('search', '')
	if search_term is None:
		search_term = ""
	search_term = str(search_term)

	# Establish contact with database
	database = MySQLdb.connect(host="localhost", user="root", passwd="mysqldatabaseissomuchfun", db="grandrounds")	
	with database:
		# Get the cursor, which is used to traverse the database, line by line
		cursor = database.cursor()
		# Create the predefined select statement 
		query = """
				SELECT *
				FROM 
				(SELECT recipient_state, 
						physician_profile_id, 
						physician_first_name,
						physician_last_name,
						manufacturer,
						t.total,
					@phy := CASE WHEN @stateclass <> recipient_state THEN 0 ELSE @phy+1 END as rank,
					@stateclass := recipient_state AS clset
				FROM
					(SELECT @phy := -1) s,
					(SELECT @stateclass := -1) c,
					(SELECT recipient_state, 
							physician_profile_id,
							physician_first_name,
							physician_last_name,
							manufacturer,
							SUM(total_amount) as total
					FROM physician_payments
					WHERE manufacturer LIKE '%{}%'
					GROUP BY recipient_state, physician_profile_id, physician_first_name, physician_last_name, manufacturer
					ORDER BY recipient_state, total DESC) t
					) dataframe
				WHERE dataframe.rank <= 19;
				""".format(search_term)
		# Execute
		cursor.execute(query)
		# Get result
		#result = database.use_result()
		rows = cursor.fetchall()
		output = [{} for x in range(len(rows))]
		for i, row in enumerate(rows):
			output[i] = {	'recipient_state': row[0], \
							'physician_id': int(row[1]), \
							'physician_name': row[2] + ' ' + row[3], \
							'total_amount': float(row[5]), \
							'manufacturer': row[4]}
		#for i in range(1):
		#	row = cursor.fetchone()
		
		# Return json string
		return json.dumps(output)
	return json.dumps({})

if __name__ == "__main__":
    app.run(debug=True)
