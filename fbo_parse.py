# FBO_Parser - FBO.gov
# Ron Egli
# Used to pull the latest opportunitis from FBO.gov
# Version 1

import requests, re, json
from bs4 import BeautifulSoup

days = "today" # How many days to go back ['today', 2,3,7,14,21,30,90,180,265]
results_per_page = 10 # 100 is max
results = {} # Used later

# Put the codes you wish to pull here
codes = [541519, 541690, 54111, 541512, 541513]

def fetchResults(days, code, results_per_page):
	global results
	url = "https://www.fbo.gov/index.php"
	querystring = {"s":"opportunity","mode":"list","tab":"list","pp":results_per_page}
	payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_class_values[procurement_notice][_posted_date]\"\r\n\r\n" + str(days) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_class_values[procurement_notice][set_aside][]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_class_values[procurement_notice][zipstate]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_class_values[procurement_notice][procurement_type][]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_class_values[procurement_notice][keywords]\"\r\n\r\n" + str(code) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"autocomplete_input_dnf_class_values[procurement_notice][agency]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_class_values[procurement_notice][agency]\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"so_form_prefix\"\r\n\r\ndnf_\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_opt_action\"\r\n\r\nsearch\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_opt_template\"\r\n\r\nvendor_procurement_notice_filter\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_opt_mode\"\r\n\r\nupdate\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_opt_finalize\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_opt_target\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_opt_validate\"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"dnf_class_values[procurement_notice][dnf_class_name]\"\r\n\r\nprocurement_notice\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"clear_filters_from_home\"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
	headers = {
	    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
	    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
	    }

	response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

	responsebody = response.text.replace('\n', '')

	match = "" # Avoiding errors

	# search for the table of opportunities on the page
	regex = r"<table class=\"list\" summary(.*)</table>"
	matches = re.finditer(regex, responsebody, re.MULTILINE | re.IGNORECASE)
	for matchNum, match in enumerate(matches):
	    match = ("{match}".format(match = match.group()))

	# Search for each individual table row in the table
	regex = r"(<tr.*?</tr>)+"
	matches = re.finditer(regex, match, re.MULTILINE | re.IGNORECASE)

	# For each table row, pull out more crucial information
	for matchNum, match in enumerate(matches):
	    matchNum = matchNum + 1
	    
	    if matchNum != 1: # Skip the first row as its just a header
	    	# Get the basic html of the row
		    tr_match = ("{match}".format(match = match.group()))
		    # Get the link from the first td
		    link_regex = r"(<a href=\"(.*?)\")+"
		    link_matches = re.finditer(link_regex, tr_match, re.MULTILINE | re.IGNORECASE)
		    for matchNum, match in enumerate(link_matches):
		    	#tr_link = ("{match}".format(match = match.group()))
		    	for groupNum in range(0, len(match.groups())):
		    		tr_link = ("{group}".format(group = match.group(groupNum))).replace('<a href=\"',"").replace('\"','')
		    # Pull the opportunity id from the link
		    id_regex = r"&id=(.*?)&+"
		    id_matches = re.finditer(id_regex, tr_link, re.MULTILINE | re.IGNORECASE)
		    for matchNum, match in enumerate(id_matches):
		    	#tr_id = ("{match}".format(match = match.group()))
		    	for groupNum in range(0, len(match.groups())):
		    		tr_id = ("{group}".format(group = match.group(groupNum))).replace("&id=","").replace("&",'')

		    # Generate JSON output
		    result_id = len(results)

		    results[result_id] = {}
		    results[result_id]['id'] = tr_id
		    results[result_id]['body'] = tr_match
		    results[result_id]['link'] = tr_link
		    results[result_id]['parsed'] = {}
		    # Parse the HTML of the tr into json the best we can
		    results[result_id]['parsed'] = [[cell.text for cell in row("td")] for row in BeautifulSoup(tr_match,"html.parser",from_encoding='utf-8')("tr")]
		    results[result_id]['code'] = code

for code in codes:
	print "Fetching results for code: " + str(code)
	fetchResults(days, code, results_per_page)


print json.dumps(results)  
