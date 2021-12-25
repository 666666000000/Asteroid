@echo off
robocopy %1 %2 /MIR /DCOPY:T /COPY:DAT /A-:SH /V /XD "System Volume Information" $RECYCLE.BIN /R:3 /W:3
