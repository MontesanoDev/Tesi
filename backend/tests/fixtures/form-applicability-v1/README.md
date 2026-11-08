# Applicabilità FORM V12: controesempi originali

Copie immutate delle risposte reali Catanzaro B0-3 ed E1-3 dello studio
`benchmark ufficiale/diagnosi-architetturale-v12-20261020/`, con originale DOCX,
input canonico e selezione reale del narratore. `manifest.json` conserva gli
hash delle acquisizioni. I file `*-state.json` conservano lo stato registrato
tranne catalogo, audit e vista dei campi, ricostruiti nei test; non creano nuove
ricevute USER o revisioni. I valori attesi non entrano nel prompt.

Entrambe le proposte omettono il predicato di `paragraph:35`: scrivono il valore
SOURCE vero in `t0.r8.c1`, benché la stessa riga FORM richieda una sede diversa
da quella legale. Le SOURCE attestano indirizzi coincidenti dello stesso soggetto.
Il test riesegue le risposte integrali e deve conservare tutte le altre scritture.

I test sono replay deterministici: nessuna chiamata a un provider o SQLite.
