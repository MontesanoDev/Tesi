# Completezza dei valori V12 — fixture congelata

`response.txt` e `state.json` sono l'output reale e lo stato della prova UI
`table-form-links-20261020-01`, senza correzioni MODEL. Il manifest contiene
SHA256 e riferimenti all'originale DOCX e all'input SOURCE già conservati nella
fixture `../form-applicability-v1/`. Le SOURCE della chiamata globale coincidono;
nessuna chiave, database o configurazione privata è inclusa.

Il test riproduce `t25.r3.c1`: numero SOURCE vero, data assente nel valore,
condizione societaria confermata. Il controllo di completezza deve vietare la
scrittura senza alterare fatto, appartenenza del soggetto o condizione MODEL.
`Bari` in `t25.r2.c0` resta scrivibile; la sede operativa non applicabile resta
vuota. Gli altri test costruiscono documenti e SOURCE sintetici temporanei.
