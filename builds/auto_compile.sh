#!/bin/sh

#TODO better job control(may python?)

set -m # Enable Job Control

coffee -wc --output pub/js static/js & ##rember to use 'ps aux | grep coffee' to kill the process XD

autoless static/less/ pub/css &
