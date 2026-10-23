# Attribuzione SOURCE: input reale Cesano congelato

`cesano-real.json` conserva senza correzioni gli otto fatti e le otto proposte
della nuova chiamata reale dell'esperimento FORMTEXT del 19 ottobre 2026,
con le stesse SOURCE disponibili. Non è un GOLD e non entra nei prompt o nella KB.

Originale DOCX riusato da `../formtext-v1/cesano/original.docx`.
Acquisizione originaria: `backend/data/compilation-audit/formtext-chiusura-20261019-01/cesano/artifacts/`.
Diagnosi di riferimento: `docs/regressione-formtext-e2e-2026-10-19.md`.

Aspettativa del nuovo test: conservare i fatti societari come tali e la
proposta della denominazione aziendale; respingere il loro trasferimento nei
sette campi dello studio/PIVA/recapiti del sottoscrittore, non dimostrato dalle
fonti. Il test non inventa un firmatario e non risolve l'applicabilità.

`catanzaro-real.json` conserva le SOURCE e la risposta globale effettiva della
prova casuale `source-attribuzione-20261019-01`, senza cambiare i record originali.
Il FORM è `../formtext-v1/catanzaro/original.docx`.
I test tabellari creano copie con quattro assegnazioni deliberatamente errate:
sono controesempi controllati sul FORM reale, non errori prodotti dal modello
nella sessione storica. La risposta originale resta conservata e separata.
