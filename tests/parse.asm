x       db 5
y       DB 32h
;blankline, next two lines should not be processed as there is no content
;

navesti lda x
        sta x; komentář, utf8 test: 👤😂🔊🤣
        HLT