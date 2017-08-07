#!/usr/bin/python

base = 'http://search.worldbank.org/api/v2/projects?format=json&rows=20000&prodline_exact=GU^PE&status_exact=Active^Closed'
url1 = base + '&fl=countrycode,boardapprovaldate,totalamt&countrycode_exact=%s&frmYear=1947&toYear=2015' % ('PE')

print url1

url2 = base + '&fl=countrycode,boardapprovaldate,totalamt&%s=%s&frmYear=1947&toYear=2015' % ('mjsectorcode_exact', 'EX')
print url2

