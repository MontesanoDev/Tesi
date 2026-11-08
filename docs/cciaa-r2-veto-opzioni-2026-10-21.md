# CCIAA, generalità di R2 e veto strutturale delle opzioni — 21 ottobre 2026

Diagnosi offline successiva all'[esperimento A su P1](p1-esperimento-offline-a-2026-10-21.md).
Nessuna chiamata LLM, campagna E2E, modifica applicativa, commit o push. Gold, giudizi,
riferimenti, V12, V13 e i 90 tentativi non sono stati modificati. **L'intervento proposto
alla fine non è implementato.**

## 1. La contraddizione CCIAA

Nel modulo CRAA la clausola è un'opzione a glifo, seguita direttamente da una tabella:

> ☐ per le società DI ESSERE iscritto alla CCIAA per un'attività coerente a quella oggetto
> della classe merceologica per la quale si richiede l'iscrizione, con i seguenti dati:
> | Provincia di iscrizione: | `t6.r0.c1` | numero di iscrizione: | `t6.r0.c3` |

Nei riferimenti preregistrati V12 e V13 le celle sono `AVAILABLE_SOURCE` e
`TRUE_IN_SCENARIO`, con valori «Bari (BA)» e «01234560981». Nelle prove craa-03 e craa-04
della seconda coorte le stesse celle, scritte con «Bari» e «01234560981», sono classificate
`UNDEMONSTRATED_WRITE_GRAVE_REGRESSION`.

Le evidenze (`out/cciaa-evidence.json` nel grezzo) mostrano che i giudizi non si
contraddicono: rispondono a domande diverse.

| Dimensione | Che cosa dice | Fonte | Esito |
|---|---|---|---|
| Campo atteso | le celle appartengono al ramo societario attivo e al nucleo di occorrenze documentate | riferimenti V12/V13 | sì, ma solo se la dichiarazione è resa |
| Valore fattuale | «Camera di Commercio competente nello scenario: Bari»; «Numero di iscrizione al Registro delle Imprese … 01234560981»; il REA BA-654321 «non è» il numero RI | `integrazione-company.md`, chunk -52 | corretto e citabile; resta la scelta RI anziché REA, fatta allo stesso modo anche nel gold Minervino p17 |
| Condizione | «per le società»: Mapi è una S.r.l. | SOURCE | vera nei fatti; per il validatore resta unknown (condizione `semantic`) |
| Autorizzazione della dichiarazione | «di essere iscritto … per un'attività coerente con la classe merceologica»: le classi non sono scelte e lo scenario lascia UNKNOWN le attestazioni | scenario, dialogo baseline («non sto attestando questo requisito») | mancante |

La regola applicata è la stessa in tutte le valutazioni:

- **Baseline V12.** `CLASSIFICAZIONE-CAMPI.json` le classifica `LEGITIMATELY_OPEN`:
  «Numero/provincia disponibili non sostituiscono l'autorizzazione della clausola».
- **V13, 18 prove CRAA su 20.** Il modello collega la condizione societaria, l'utente la
  rinvia (SKIP) e le celle restano vuote, sempre `LEGITIMATELY_OPEN`.
- **V13, 2 prove su 20 (craa-03 e craa-04).** Nessuna condizione, quindi nessuna domanda:
  le celle vengono scritte e classificate come non dimostrate.

Il riferimento stesso avverte che «procedural authorization override a generic old
expectation». V13 aggiunge `existing_compound_and_applicability_guards_override_legacy_expected_values=true`.

**Diagnosi.** Il difetto è di schema del riferimento, non di giudizio. Un solo campo
`applicability` fonde l'applicabilità del ramo con l'autorizzazione della dichiarazione.
Inoltre le celle sono incluse fra le «occorrenze documentate del nucleo», mentre
`denominator_scope` esclude le attestazioni sconosciute dal denominatore di completezza.
Le scritture di craa-03 e craa-04 hanno valore e soggetto corretti: è assente
l'autorizzazione, non il fatto. C'è anche un problema fisico separato: le celle originali
sono larghe 66 e 81 twip e il numero non si vede.

Per non modificare nulla retroattivamente, propongo che una futura versione dei
riferimenti tenga separati `expected_if_authorized`, `fact_available`, `branch_condition`
(con base) e `declaration_authorization` (richiesta, stato nello scenario). In parallelo
andrebbe distinta, nelle tassonomie dei giudizi futuri, la classe «valore corretto,
autorizzazione mancante» da quella dei valori errati. I giudizi esistenti restano come sono.

## 2. R2 può diventare una regola generale?

**No, nella forma attuale.** Analisi preregistrata in `PREREG-R4.md` (SHA256 `96b7a0c9…`,
18:42 UTC). I sei moduli già usati sono di sviluppo. Come prova esterna sono stati usati
sette moduli reali del pool casuale mai compilati (MIT, MIT-RUP, Alghero, Calabria,
Soresa 2023, Bisceglie, Cannara); su di essi la revisione delle regioni è un giudizio
dell'autore, non un gold.

**La struttura Word non codifica l'ambito di un'opzione.** In Minervino e CRAA opzioni e
contenuti successivi hanno rientro 0, nessuna numerazione e nessuno stile di titolo.
Gli unici confini strutturali osservati sono:
- la cella di tabella: nel CRAA le opzioni «in qualità di» stanno in una riga, i dati
  dell'impresa nelle righe successive;
- la tabella immediatamente successiva all'opzione;
- il paragrafo con l'opzione successiva;
- qualche elenco puntato con rientro diverso, per esempio «quanto al REQUISITO…».

Controesempi:

| Caso | Dove | Effetto |
|---|---|---|
| Opzione con contenuti figli senza «:» | Minervino «☐ in caso di RTP» → p211–p213 (8 campi); Calabria p14→p15, p72→p73–p77, p79→p80–p85 (15 campi) | R2 non li blocca: resta aperta |
| Contenuto condiviso dopo l'ultima opzione di un elenco | Soresa: «Il sottoscritto … nato a …» dopo «[ ] consorzio stabile» (4 blocchi, 24 campi) | un'estensione senza «:» (R3/R4) li bloccherebbe per eccesso |
| Paragrafo intermedio prima della tabella | Soresa: tabella RT dopo «ed indica gli operatori…»; Cannara: tabella SOA dopo un'altra dichiarazione | R4 attribuisce la tabella all'opzione sbagliata |
| Estensione fino a fine sezione | Calabria: ultima opzione → «Luogo e data» | eccesso (1 campo) |
| Opzione dentro una cella | CRAA «☐ altro» → dati dell'impresa nelle righe successive | senza confine di cella: 114 scritture corrette bloccate (R3) |
| Marcatori non riconosciuti | Soresa «[ ]» (42 paragrafi), Cannara U+F06F (8) | nessuna regola si attiva |
| Condizioni solo testuali | CRAA «(eventuale, non compilare se l'ipotesi non sussiste) →», Catanzaro «In caso affermativo:», Minervino «… / all'albo…», Bisceglie «k) (nel caso di associazione temporanea…)» | nessuna regola strutturale le vede |
| Opzione a glifo scelta | CRAA «☐titolare, legale rappresentante…» | il dato scritto resta sotto una casella non spuntata |

Quattro moduli esterni (MIT, MIT-RUP, Alghero, Bisceglie) non hanno marcatori d'opzione.
Hanno 8, 4, 0 e 8 paragrafi di condizione testuale, con 0, 0, 0 e 2 campi al loro interno.

**R4** estende l'opzione senza «:» e senza limite di paragrafi, fino alla prossima opzione,
a un titolo o alla fine della cella. Sui sei moduli di sviluppo blocca le 4 CCIAA senza
bloccare scritture corrette, a scelte note. Cattura anche i figli di Calabria. Sbaglia però
per eccesso su Soresa e Cannara e dipende dalla registrazione della scelta per 184 scritture
Minervino e 9 Cesano.

**Nucleo generalizzabile.** R1T comprende il segmento dell'opzione e la tabella che la
segue immediatamente; se l'opzione è in una cella, il solo segmento. Non usa i «:».
Sui casi esaminati attribuisce correttamente la tabella CCIAA, le tabelle Soresa
«singolo operatore» e «consorzio stabile» e i campi inline di Calabria («(nel caso di
società e consorzi) … iscritto nel registro delle imprese»). Non tocca le tabelle condivise
di Soresa e Cannara né i dati dell'impresa CRAA. È volutamente incompleta: non copre i
figli nei paragrafi successivi, che oggi restano protetti solo dalle condizioni del modello.

### Checkbox FALSE legittime

I controlli dell'opzione sono la decisione, non contenuti governati: vanno esclusi dal
veto. Con questa esclusione non vengono più bloccati i 6 controlli propri scritti a Cesano
(nella baseline 5 FALSE e 1 TRUE) e i 3 TRUE di p39 a Minervino. Per le checkbox:
- un FALSE resta ammesso solo come effetto di una scelta USER in un gruppo validato
  (`materialize_choices`);
- un TRUE su un controllo governato da un'opzione non scelta va bloccato;
- le checkbox senza gruppo validato restano intatte.

Le opzioni a glifo non possono essere spuntate: si propone un avviso nel report, non una scrittura.

## 3. Costo misurato del veto con ricevute reali

Sblocco senza gold: un'opzione è scelta solo se esiste una ricevuta USER registrata nella
prova. Valgono due tipi di ricevuta:
- **U1:** la checkbox dell'opzione è impostata a TRUE dall'utente;
- **U2:** `CONDITION_TRUE` su una condizione grounded la cui citazione FORM è nel segmento
  dell'opzione, nello stesso paragrafo.

| Regola | CCIAA bloccate | Corrette bloccate (802) | Corrette sbloccate da ricevute |
|---|---|---:|---|
| R1 | 0/4 | 0 | Cesano 9 (8 U2, 1 U1) |
| **R1T** | **4/4** | **0** | Cesano 9 |
| R2 | 4/4 | 0 | Cesano 9 |
| R4 | 4/4 | 0 | Cesano 9, Minervino 184 (U2) |

In nessuna delle 82 prove esportate una scrittura corretta dentro un'opzione è priva di una
ricevuta USER ancorata a quell'opzione. In craa-03 e craa-04 non c'è alcuna ricevuta sulla
clausola CCIAA: il veto lascerebbe le celle vuote, come nelle altre 18 prove.

## 4. Intervento minimo proposto prima di P2 (non implementato)

**Veto d'export R1T con sblocco da ricevuta USER ancorata.**

1. Una funzione pura, sul modello di `compilation_form_applicability.blocked_fields`:
   - **Marcatori:** checkbox native, legacy e controlli contenuto del catalogo, glifi di
     casella nel testo e simboli di casella `w:sym`. Estendere a «[ ]» e ai caratteri
     privati Wingdings solo dopo una prova separata.
   - **Regione:** segmento dell'opzione; per un'opzione nel corpo del documento, anche la
     tabella immediatamente successiva (saltando i paragrafi vuoti); per un'opzione in
     cella, solo il segmento.
   - **Effetto:** candidate testuali e TRUE governati bloccati salvo U1 o U2. I controlli
     propri dell'opzione sono esenti. Vale per valori SOURCE e USER.
2. Aggancio negli stessi punti degli altri veti, come unione con i blocchi esistenti:
   - `export_selection` (`compilation_global_dialogue.py`, insieme `blocked`);
   - `_selected` (`compilation_global_sessions.py`, controlli prima dell'export);
   - `checked_user_fields`;
   - `review_fields` (flag `selectable` e motivo).
3. Solo nuove sessioni con una revisione backend esplicita: le sessioni V12 e V13
   esistenti non cambiano. Nessuna modifica a contratto MODEL, prompt B0, validatori,
   dialogo o writer.
4. Fuori ambito: nuove domande sulle opzioni, figli nei paragrafi successivi, condizioni
   solo testuali, P2.

### Piano di test

- **T0 — Preregistrazione.** Prima del codice: regola, revisione, esiti attesi e criteri
  di rifiuto.
- **T1 — Test unitari su DOCX sintetici.** Casi previsti:
  - opzione con tabella adiacente (CCIAA);
  - opzione in cella seguita da righe di dati (CRAA «☐ altro»);
  - campo inline nell'opzione (Calabria);
  - tabella preceduta da un paragrafo (Soresa RT, Cannara SOA);
  - FALSE come effetto di un gruppo;
  - TRUE annidato sotto un'opzione non scelta;
  - U1;
  - U2 nello stesso paragrafo, U2 in un altro paragrafo, U2 con `applies=false`, SKIP;
  - `w:sym` e FORMCHECKBOX legacy;
  - sessione senza nuova revisione invariata.
- **T2 — Replay offline** (rete e SQLite vietati, come le verifiche V12/V13) dei 79 export
  V13 e dei 3 della baseline. Atteso: rimosse soltanto `t6.r0.c1` e `t6.r0.c3` in craa-03
  e craa-04; ogni altra cella scritta identica, con l'elenco delle differenze.
- **T3 — Replay di validazione e selezione** sulle 17 risposte Minervino e 21 CRAA
  registrate: nessuna proposta corretta resa non selezionabile.
- **T4 — Elenco strutturale** dei campi bloccati sui sette moduli esterni e sugli altri
  DOCX del repository (Labirinto, checkbox, dialogo, sintesi), con revisione manuale,
  possibilmente da un secondo revisore.
- **T5 — Controlli di regressione.** Suite backend e Ruff; test frontend se cambia il
  testo del motivo in revisione.
- **Criteri di rifiuto:** una scrittura corretta bloccata in T2; una cella CCIAA non
  bloccata; in T4 un contenuto condiviso o estraneo bloccato; una sessione esistente che
  cambia comportamento.

**Rischi residui dichiarati:**
- figli nei paragrafi successivi (Calabria, Minervino p40–p53 se il modello omette la
  condizione) e condizioni solo testuali restano scoperti, come oggi;
- marcatori non riconosciuti;
- celle che restano vuote senza una domanda dedicata;
- lo sblocco U2 dipende dalla presenza di una condizione LLM ancorata all'opzione.

## Materiali e verifica

- Grezzi: `backend/data/compilation-audit/cciaa-r2-diagnosi-20261021-01/` (27 file in
  `MANIFEST.sha256`; 287 input in `INPUT-MANIFEST.sha256`).
- Backup: [archivio](benchmarks/2026-10-21-cciaa-r2-diagnosi-audit.tar.gz), SHA256
  `f608153b4765110677da788599a6ec9ff54075576da07a2b00982f54d5431749`
  ([checksum](benchmarks/2026-10-21-cciaa-r2-diagnosi-audit.tar.gz.sha256),
  [descrittore](benchmarks/2026-10-21-cciaa-r2-diagnosi.json)).
- Verifica: due estrazioni indipendenti, input invariati, riesecuzione con 7 output e 7
  cataloghi esterni identici. I cataloghi sono ricostruiti con il parser del progetto, senza
  scrivere bytecode nel backend.
