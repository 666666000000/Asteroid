@echo off
set INPUT_PARAM=%1
start "" winscp /console /command "option batch continue" "open ftp://user:password@ip:port" %INPUT_PARAM:?= % "exit" 

EXIT

