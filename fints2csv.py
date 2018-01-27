#!/usr/bin/env python3

import logging
from datetime import date
from fints.client import FinTS3PinTanClient
import csv
import sys
import argparse
from datetime import datetime, date

# parse command line arguments
parser = argparse.ArgumentParser(description='FINTS to CSV.')
parser.add_argument('BLZ', help='Bankleitzahl')
parser.add_argument('KNR', help='Account number')
parser.add_argument('PIN', help='PIN of the account')
parser.add_argument('startDate', help='starting date')
parser.add_argument('endDate', help='end date')
parser.add_argument('-v', '--verbose', help='increase output verbosity', action="store_true")
parser.add_argument('-t', '--testrun', help='disables writing to file', action="store_true")
args = parser.parse_args()

# connect to bank via FINTS
f = FinTS3PinTanClient(args.BLZ, args.KNR, args.PIN, 'https://hbci-pintan.gad.de/cgi-bin/hbciservlet')
accounts = f.get_sepa_accounts()

# get a series of transactions in a specific time frame
startDate = datetime.strptime(args.startDate, "%Y-%m-%d").date()
endDate = date.today() if args.endDate == "today" else datetime.strptime(args.endDate, "%Y-%m-%d").date()
statement = f.get_statement(accounts[0], startDate, endDate);

# not all transactions have all fields, collect them first
header = set()
for st in statement:
    header |= statement[0].data.keys() # set update operator

if args.verbose:
    print('Header: %s' % header)

with open('transfers.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(header)
    for i,st in enumerate(statement):
        row = []
        for key in header:
            if key not in st.data.keys():
                row.append(None)
            elif key == "amount":
                row.append(st.data[key].amount)
            else:
                row.append(st.data[key])

        if args.verbose:
            print("Statement %i: %s, %s, %s" % (i, st.data['date'], st.data['amount'], st.data['applicant_name']))


        if not args.testrun:
            csvwriter.writerow(row);

print('Wrote %i rows with %i columns each' % (len(statement), len(header)))
