import csv
f = open('answers.csv', 'r')
csvreader = csv.reader(f)

header = next(csvreader)