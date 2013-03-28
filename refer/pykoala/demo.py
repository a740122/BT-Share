import Koala

entryFilter = dict()
entryFilter['Type'] = 'allow'
entryFilter['List'] = [r'news\.163\.com', ]

yieldFilter = dict()
yieldFilter['Type'] = 'allow'
yieldFilter['List'] = [r'\.jpe?g$', r'\.png$']

koalaBaby = Koala.Koala("http://www.163.com", entryFilter, yieldFilter, enableStatusSupport=True)

for url in koalaBaby.go():
    print url
