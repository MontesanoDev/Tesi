# Correzione circoscritta delle caselle testuali — piano prima del codice

Base `1785357` (runtime identico ad `a152d7f`), snapshot privato e ripristino
verificati. Lavoro esclusivamente offline nel worktree `tesi-checkbox-20261026`.

## Difetto riprodotto e perimetro

Il FORM sintetico della campagna del 25 ottobre contiene al paragrafo 16
`[] di avvalersi dei requisiti della seguente impresa ausiliaria:`. Sono normali
elementi `w:t`, non controlli `w:checkBox`/`w14:checkbox`, simboli `w:sym` o celle.
La destinazione non entra nel catalogo e il writer nativo non può selezionarla.
Il consenso registrato alla condizione non equivale a una nuova scelta di checkbox:
non verranno reinterpretate o aggiornate automaticamente le sessioni storiche.

Modifica minima prevista:

1. Adapter strutturale per un solo marcatore ASCII iniziale `[]`, `[ ]`, `[x]`
   o `[X]`, seguito da un'etichetta, in un paragrafo semplice del corpo o di una
   cella. Testo ordinario interno, simboli, contenuti complessi e casi ambigui
   restano esclusi. Nessuna regex legata a bandi o aziende.
2. Catalogo e writer condividono la stessa posizione; ID separati da quelli nativi.
   Scrittura esatta del solo marcatore con conservazione dei run e dell'originale.
3. Riutilizzo di gruppi, condizioni e ricevute USER esistenti: nessuna scelta
   ASCII positiva da SOURCE sola o da una risposta USER rivolta ad altro slot.
   L'opzione deve identificare l'intera clausola locale; resta il controllo V14.
4. Profilo esplicito `checkbox-testuali-2026-10-26`, flag persistito nella sessione.
   Default, profili storici e sessioni precedenti invariati. Nessuna adozione live.
5. Conservazione dei controlli delle opzioni FORM: l'aggiunta di controlli ASCII
   non deve far sparire le regioni condizionali riconosciute prima della modifica.

File previsti: adapter testuale dedicato; `compilation_catalog.py`,
`docx_checkboxes.py`, `docx_templates.py`, `compilation_profile.py`,
`compilation_sessions.py`, `compilation_global_sessions.py`,
`compilation_choices.py`, `compilation_form_option_scope.py` e test mirati.
Nessuna nuova orchestrazione, inferenza semantica, retrieval o migrazione.

## Criteri di verifica

- Prima della modifica: test riproducibile di mancata destinazione e scrittura.
- Dopo: selezione autorizzata e deselezione, run spezzati, celle, originale
  immutato; simboli/testo interno non convertiti; ID nativi immutati.
- Negativi: mancata scelta USER, rinvio, condizione falsa/ignota, risposta a
  un altro gruppo, citazione parziale, proposta SOURCE e ramo non applicabile.
- Verifica del DOCX e rendering del caso sintetico, senza inferenze.
- Regressioni di opzioni/istruzioni FORM, V14/K3, gruppi nativi, profilo ordinario
  e storico; suite backend e Ruff.
- Commit dedicato; ritorno al padre e revert verificati in ambiente isolato.
  Nessuna modifica all'app ordinaria; nessun push o merge automatico.

Limiti: soltanto la grammatica locale specificata, non tutte le rappresentazioni
grafiche di caselle. La corretta proposta del gruppo da parte del modello resta
da verificare in una prova reale futura, soggetta ad autorizzazione separata.
Budget inferenze di questo intervento: **zero**.
