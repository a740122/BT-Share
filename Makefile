INDEX_LESS = ./static/less/index.less
INDEX_CSS = ./pub/css/index.css
DETAIL_LESS = ./static/less/detail.less 
DETAIL_CSS = ./pub/css/detail.css
DATE=$(shell date +%I:%M%p)
CHECK=\033[32m✔\033[39m
HR=\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#


#
# BUILD DOCS
#

build:
	@echo "Running recess on css...             ${CHECK} Done"
	@./node_modules/.bin/recess --compile ${INDEX_LESS} > ${INDEX_CSS}
	@./node_modules/.bin/recess --compile ${DETAIL_LESS} > ${DETAIL_CSS}
	@echo "Compiling LESS with Recess...               ${CHECK} Done"
