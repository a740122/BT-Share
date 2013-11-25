### deploy documents

#### step1:
grap the files from [github][1], and put it on somewhere.Here i choose to save it on `/var/www/bt-share`

```
cd /var/www/
git clone xxxx bt-share
cd bt-share
git submodule init
git submodule update
```
ps: you may want to know [git submodule][3]

#### step2:
cd in every module which are web/mdht/crawler,and edit the config.py file to suit your need.

#### step3:
install the virtualenv,and run:

```
mkvirtualenv bt-share
cd /var/www/bt-share
pip install -r requirements.txt
```

#### step4:
install the supervisor to manage those three process
```
pip install supervisor
```
now, you need to edit the supervisor_pro.conf to suit your system.
After that, we keep on runing below commands.

```
cd /var/www/bt-share/deploy
supervisord -c ./supervisor_pro.conf
supervisorctl -c ./supervisor_pro.conf
```
now, you should see there are three process runing.
You may want to change them, just go and read the supervisor [documents][2]

[1]: https://github.com/zhkzyth/BT-Share
[2]: http://supervisord.org/index.html
[3]: http://joncairns.com/2011/10/how-to-use-git-submodules/
