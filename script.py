import sys
import MySQLdb
import os
import re

# Returns all files of the correct format whose version is higher than the database's.
def get_later_files(sql_directory, db_version):
	filename_matcher = re.compile("^[0-9\s]+\.?[A-z\s]+\.sql")
	file_version_matcher = re.compile("^[0-9\s]+")

	files = []

	for root, dirs, files in os.walk(sql_directory):
		for file in files:
			if filename_matcher.match(file):
				match = file_version_matcher.match(file)
				file_version = match.group(1)
				
				file_version = file_version.replace(" ", "")
				file_version = Int(file_version)

				if Int(file_version) > db_version:
					files.add((file_version, file))

	sorted_files = sorted(files, key=lambda tup: tup[0])
	filenames_only = [x[1] for x in sorted_files]

	latest_version = sorted_files[-1][0]

	return filenames_only, latest_version


# Main method.
def main(sql_directory, db_username, db_host, db_name, db_password):
	conn = MySQLdb.connect(host=db_host, user=db_username, passwd=db_password, db=db_name)
	cursor = conn.cursor()

	cursor.execute('SELECT version FROM versionTable')
	version = cursor.fetchone()

	files, latest_version = get_later_files(sql_directory, Int(version))

	for file in files:
		cursor.execute('INSERT INTO testTable VALUES("{}")'.format(file))
		cursor.commit()

	cursor.execute('UPDATE versionTable SET version={}'.format(latest_version))
	cursor.commit()

	cursor.close()


# Check inputs and call main method
if __name__ == "__main__":
	if(len(sys.argv) != 6):
		print("Incorrect arguments supplied.")
		print("Arguments of the form: python script.py directory-with-sql-scripts username-for-the-db db-host db-name db-password")
		sys.exit()

	else:
		main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])