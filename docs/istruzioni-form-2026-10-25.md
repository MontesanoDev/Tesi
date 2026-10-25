# Istruzioni condizionali del FORM: seconda correzione offline

25 ottobre 2026. Revisione autoriale (Claude), non indipendente. Prosegue il lavoro sui
tredici controesempi residui ([ambiti-form-2026-10-25.md](ambiti-form-2026-10-25.md)): restavano
sei casi nelle schede dei componenti RT. Zero inferenze; nessuna modifica all'app ordinaria.

## Esito dei replay

Rigioco deterministico dei gate sugli output registrati, come nel lavoro precedente.

| Misura | Base `9cb3129` | Revisione 1 (`ddb8cb7`) | Revisione 2 |
|---|---:|---:|---:|
| Errori ammissibili, guardia d'ambito simulata SUPPORTED | 13/25 | 6/25 | **0/25** |
| Errori ammissibili, sole ricevute registrate | 7/25 | 4/25 | **0/25** |
| Corrette consentite, ricevute simulate | 245/245 | 245/245 | 243/245 |
| Corrette consentite, sole ricevute registrate | 211/245 | 211/245 | 211/245 |
| Positive estese (sprint, incrementale), ricevute simulate | 236/240 | 236/240 | 236/240 |

**Insiemi:**
- **congelato:** rev 2 e rev 3 corretta, lo stesso di `ambiti-form-20261025-01`;
- **positive estese:** 240 scritture giudicate DIMOSTRATA nelle campagne sprint e incrementale,
  riportate separatamente.

Le 4 corrette escluse nelle positive estese lo erano già nella base.

**I 2 nuovi rifiuti, `p31.s0`** nei due tentativi rev 2 So.Re.Sa., sono descritti più sotto.
Il giudizio storico resta invariato. Nessun benchmark è riscritto.

## Diagnosi dei sei casi

Sei dati veri dell'impresa singola sono scritti nelle schede dei componenti di un RT non
costituito:
- **soresa2023-1:** `p44.s0` e `p44.s1`;
- **soresa2023-2:** `p43.s8`, `p43.s9`, `p44.s0` e `p44.s1`.

Il paragrafo 19, in grassetto, dice «(da compilare nel caso di partecipazione in forma di RT,
Consorzio Ordinario o GEIE non ancora costituito)». Governa quattro schede ripetute separate da
«***» e da note in grassetto tra parentesi, fino al titolo «CHIEDE/CHIEDONO» (paragrafo 64).

In quattro casi il modello non aveva indicato alcuna condizione, quindi nessun controllo di
applicabilità scattava. La struttura locale delle opzioni della revisione 1 qui non esiste.

## Comportamento introdotto (revisione 2)

**Istruzione condizionale:** un paragrafo del corpo che:
- non ha destinazioni né controlli;
- è interamente in grassetto;
- dopo la normalizzazione, eventualmente tra parentesi, inizia con «da compilare in/nel caso
  di» seguito da testo.

I marcatori sono quelli già usati dal controllo delle tabelle condizionali.

**Ambito:**
- comprende i paragrafi del corpo successivi;
- termina alla prima tabella, all'istruzione successiva o a un paragrafo in grassetto senza
  destinazioni che non inizia con «(»;
- sono governate le sole destinazioni di testo.

Nessun nome di bando, ruolo o tipo societario nella regola.

**Inventario sui 7 moduli dei benchmark:** solo So.Re.Sa. ha istruzioni nel corpo.
- Paragrafo 7: partecipazione singola o RT già costituito, 12 destinazioni.
- Paragrafo 19: RT non costituito, 48 destinazioni.

**Condizione valida:** ancorata al paragrafo dell'istruzione, senza errori di validazione, con
citazione normalizzata che:
- coincide con l'istruzione intera, oppure
- è un suo prefisso che contiene il marcatore, arriva almeno al primo «ovvero», «,» o «;» dopo
  il marcatore e termina a un confine di parola (regola A2, sotto).

Frammenti interni, prefissi troppo corti e tagli a metà parola non bastano.

**Effetti:** lo stesso meccanismo della revisione 1.
- La condizione è propagata alle destinazioni governate.
- Senza condizione valida lo stato è NON_ACCERTATA, con il motivo «Applicabilità
  dell'istruzione FORM non accertata».
- Con condizione valida servono una ricevuta USER positiva, verificata per lo stesso ambito e
  attuale, e un risultato non falso.
- Il veto vale per SOURCE e USER ed è ricostruito dall'originale all'export.
- Il backend non inventa condizioni e non genera domande per quelle omesse.
- La revisione 1 delle opzioni resta identica.

**Attivazione, solo candidata:** `MAPI_FORM_OPTION_SCOPE_REVISION=2`, profilo
`sezioni-istruzioni-2026-10-25`, flag `form_option_scope_revision=2`.
- La revisione 2 comprende la 1.
- Il predefinito `sezioni-2026-10-24` e le sessioni esistenti non cambiano.
- Il percorso `storico` ignora l'opt-in.

## Arresto preregistrato e decisione dell'utente

Piano congelato prima del codice: [piano-istruzioni-form-2026-10-25.md](piano-istruzioni-form-2026-10-25.md),
copia e SHA-256 nei grezzi. La regola preregistrata richiedeva la citazione dell'istruzione
intera e ha perso 7 corrette, con 231/240 nelle positive estese.

Il rigioco si è fermato come previsto dal piano (`out/NOTA-ARRESTO.md`) per due cause:
- **5 dati corretti del concorrente** in `sprint/soresa2023-2` (`p8.s7-9`, `p9.s0-1`): la
  condizione del modello citava l'istruzione del paragrafo 7 senza la coda normativa
  «di cui all'art. 66 … D. Lgs n. 36/2023».
- **2 `p31.s0`**: «Leonardo Montemurro» da una risposta USER sul firmatario, collocato dal
  modello nel «Il sottoscritto» della seconda scheda di componente RT.

Due alternative sono state misurate offline senza toccare il codice: A2 (prefisso ancorato fino
alla prima alternativa) e A3 (parte ancorata con il marcatore). Hanno dato gli stessi numeri.
L'utente ha scelto **A2**, la più stretta, e l'emendamento è registrato nel piano. Il codice
riproduce esattamente i numeri misurati per A2.

**Discrepanza dichiarata:** a giudizio autoriale i due `p31.s0` sono dati nel ramo sbagliato,
perché il firmatario della partecipazione singola appartiene alla scheda del paragrafo 8. Il
blocco è quindi ritenuto corretto. Il giudizio storico DIMOSTRATA, basato sulla provenienza
USER, resta invariato nei benchmark congelati: serve una revisione indipendente per chiudere la
discrepanza.

## Verifiche

| Verifica | Esito |
|---|---|
| Test nuovi (`test_compilation_form_instruction_scope.py`) | 39 PASS |
| Revisione 1, 38 test esistenti | PASS invariati |
| Inventario | il codice dell'app coincide con il prototipo preregistrato su tutti i 7 moduli; regioni della revisione 1 invariate |
| 26 casi avversari K3 | identici alla base byte per byte |
| Suite completa | **3937** PASS in 550 s, Ruff PASS |
| Invarianti | 29 sessioni live identiche, 0 dei 1244 file preservati modificati |

I test nuovi coprono:
- riconoscimento e confini: tabella, istruzione successiva, titolo, nota tra parentesi;
- esclusioni: non grassetto, con campo, senza marcatore, prefisso estraneo, istruzione vuota;
- difetti della condizione: assente, estranea, parziale, non valida, non proiettata;
- citazioni equivalenti e regola A2;
- difetti delle ricevute: negativa, rinvio, estranea, su altri campi, solo SOURCE, risultato
  falso;
- revisione 1 invariata e profilo;
- export API: 409 senza condizione, 200 dopo la conferma pertinente, nuovo blocco dopo la
  revoca.

## Commit e rollback

**Fix:** `97110302e9376e68934b3a5e8f35423eb565c774`, che contiene codice, test e piano emendato. Rapporto e continuità sono in un
commit documentale separato.

Rollback del codice, sul branch, in un worktree isolato: `git revert 9711030`. Verificato in
`/home/montesano/tesi-istruzioni-rollback`: revert `fd6254d`, albero identico a `b7b7a29`. La sonda con i test della revisione 2 dà 37 FAIL e 2 PASS (le sole varianti disattivate); l'export API torna a 200 invece di 409 sul dato del componente RT, quindi il difetto è riprodotto. I 38 test della revisione 1 restano PASS.

Il revert non tocca database, sessioni, originali né la revisione 1, e non richiede
migrazioni. Rimuovere la sola variabile d'ambiente disabilita la candidata per le nuove
sessioni; quelle già create con la revisione 2 mantengono il flag.

**Grezzi:** `backend/data/compilation-audit/ambiti-istruzioni-20261025-01/`, esclusi da Git:
- inventario;
- replay preregistrato, diagnostico e A2;
- K3, suite, invarianti e nota d'arresto.

**Backup:** `backend/data/compilation-audit/ambiti-istruzioni-backup-20261025/` e
`D:\Backup-tesi-2026-10-23\ambiti-istruzioni-20261025\`.

## Limiti

**Garanzie:** nessuna nuova misura di qualità LLM, latenza o costo. Il blocco dei sei casi è
dimostrato sul rigioco degli output registrati, non dal vivo; la conservazione delle corrette
vale in questo corpus.

**Copertura della regola:**
- dipende dal grassetto e dal marcatore letterale «da compilare in/nel caso di»: istruzioni
  formulate diversamente restano scoperte;
- le caselle native in quegli ambiti non sono governate;
- una condizione omessa o una citazione che non arriva alla prima alternativa lasciano vuoti
  campi legittimi: è un rischio di omissione, non di scrittura errata, da misurare dal vivo.

**Effetto su So.Re.Sa.:** la regola si applica anche alla scheda del concorrente (paragrafo 7).
Una partecipazione singola richiede quindi che il modello citi quella istruzione e che l'utente
la confermi.

**Verifiche future, da autorizzare:** la prova di due tentativi proposta nel rapporto
precedente (massimo 750.000 token) resta non avviata. Se eseguita con la revisione 2, va
misurato anche il rischio di omissione sulla scheda del concorrente.
