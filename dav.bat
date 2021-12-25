@echo off
set INPUT_PARAM=%1
winscp /console /command "option batch continue" "open dav://user:password@dav.xxx.com/dav/" %INPUT_PARAM:?= % "exit" 
exit
