class test(object):
    def __init__(self):
        self.urls=['zhkzyth','perere','asda']

    # def __getitem__(self, x):
    #     return self.urls[x]

page = test()

for i, url in enumerate(page):
    print url, i
