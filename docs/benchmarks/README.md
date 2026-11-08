# Archivio dei benchmark

I benchmark sono dati di progetto da conservare, non output temporanei.
Distinguere prove reali dei provider da test software con risposte simulate.

## Candidata corretta, 23 ottobre 2026

[Rapporto](../candidata-corretta-2026-10-23.md). Rev 3 completa con la guardia corretta, non
adottata. Campagna preregistrata di 6 tentativi in
`benchmark ufficiale/candidata-corretta-20261023-01/`, grezzo in
`backend/data/compilation-audit/candidata-corretta-20261023-01/`.

- **Esiti:**
  - 6/6 DOCX;
  - 0 scritture non dimostrate su 142 (revisione autoriale);
  - 0 scritture nei 25 rami sbagliati della rev 2;
  - 2 segmenti recuperati.
- **Costi:** 2,57 M token su un tetto di 2,8 M.
- **Copertura mediana:** 72% / 39% / 47% (Minervino / Catanzaro / So.Re.Sa.).
- **Esito preregistrato:** favorevole.

## Candidata completa, campagna arrestata, 23 ottobre 2026

[Rapporto](../candidata-completa-2026-10-23.md). Profilo rev 3 completo, non adottato. Campagna in
`benchmark ufficiale/candidata-completa-20261023-01/`, grezzo in
`backend/data/compilation-audit/candidata-completa-20261023-01/`.

- **Eseguiti:** 3 tentativi su 8, 2 DOCX, 0 scritture non dimostrate.
- **Rami sbagliati della rev 2:** vuoti in Minervino e Catanzaro; nessuna proposta in So.Re.Sa.
- **Arresto:** per un difetto della guardia rev 3 (`rationale` oltre 250 caratteri respinta);
  1,18 M token.

## Sezioni resilienti e stato derivato, 22 ottobre 2026

[Rapporto](../sezioni-resilienti-2026-10-22.md). Candidate opt-in, non adottate.
Campagna esplorativa preregistrata in `benchmark ufficiale/sezioni-resilienti-20261022-01/`,
grezzo e script in `backend/data/compilation-audit/sezioni-resilienti-20261022-01/`.

- **409 di minervino-1:** riprodotto deterministicamente e corretto con `derivation_revision 1`.
- **Verifiche offline:**
  - suite 3.560 PASS;
  - 193/193 validazioni registrate identiche;
  - 247/247 sintesi rigiocate identiche.
- **E2E, 8 tentativi:**
  - 7/8 DOCX (1 errore di schema del narratore);
  - 30/30 segmenti analizzati, 0 retry, 0 risposte 409;
  - 1,85 milioni di token, 0,37 USD.
- **25 scritture non dimostrate** (revisione autoriale) in rami non pertinenti, per contesto di
  ramo assente nel segmento: candidata non pronta.

## Valutazione finale del candidato, 22 ottobre 2026

[Rapporto](../valutazione-finale-2026-10-22.md). Criteri v1 invariati; campagna in
`benchmark ufficiale/valutazione-finale-20261022-01/`, grezzo in
`backend/data/compilation-audit/valutazione-finale-20261022-01/`.

- 35 tentativi reali: 6 moduli storici più So.Re.Sa. con SOURCE tabellare; 4,15 milioni di token;
- 32/35 DOCX; copertura mediana ≥ 70% su 5 moduli su 7;
- 19 conferme ridondanti; vuoti con motivo 352/354;
- 0 scritture non dimostrate (revisione autoriale; indipendente non disponibile).

Candidato non adottato. Backup locale escluso da Git in
`backend/data/compilation-audit/valutazione-finale-backup-20261022/`.

## Strategia di generazione, 22 ottobre 2026

[Rapporto](../strategia-generazione-2026-10-22.md). Offline, zero chiamate LLM, in sola lettura:
`backend/data/compilation-audit/strategia-generazione-20261022-01/`.

- 158 chiamate globali registrate (132 monolitiche, 6 moduli);
- 5 troncamenti, tutti nello stesso modulo da 267 posizioni;
- criterio per dimensione respinto; ripiego dopo troncamento proposto, non eseguito.

## Narratore P3 e fallback dell'app live, 22 ottobre 2026

[Rapporto](../narratore-p3-2026-10-22.md). Offline in
`backend/data/compilation-audit/narratore-p3-20261022-01/` (preregistrazione SHA256
`042899fd…`, due addenda); E2E in `benchmark ufficiale/narratore-p3-verifica-20261022-01/`.

Offline, zero chiamate LLM:
- 4 sintesi respinte riprodotte e ora accettate, con le sospensioni conservate;
- replay di 247 sintesi: le 215 legacy sono identiche al pre-P3;
- export finale invariato nelle 12 prove P3 riuscite;
- suite 3.509 PASS, Ruff PASS.

E2E reale, 8 prove appaiate al braccio A di P3, 1,01 milioni di token:
- 7 DOCX su 8; l'unico fallimento è un troncamento della chiamata globale monolitica;
- 0 sintesi respinte, 0 scritture non dimostrate (revisione dell'autore).

P3 è opt-in e non adottato. Backup locale, escluso da Git:
`backend/data/compilation-audit/narratore-p3-backup-20261022/narratore-p3-audit-completo.tar.gz`
(SHA256 `aaaff81d96f0612d09a0239fb9fecf6443408c425eb5c0507c0d70f5e9278be2`).

## P3, dialogo e generazione per sezioni, 22 ottobre 2026

[Rapporto](../p3-dialogo-generazione-2026-10-22.md). Diagnosi e preregistrazione in
`backend/data/compilation-audit/p3-20261021-01/`; campagna in
`benchmark ufficiale/p3-verifica-20261022-01/`.

Campagna E2E reale, 16 prove (bracci A e B), 3,62 milioni di token:
- 12 DOCX su 16; i 4 fallimenti vengono dalla validazione del narratore P3;
- B contro A: 0 troncamenti, 25/28 chiamate sotto metà del limite, token 2,7×;
- 0 scritture non dimostrate (revisione dell'autore).

Candidata non adottata. Backup locale, escluso da Git:
`backend/data/compilation-audit/p3-backup-20261022/p3-audit-completo.tar.gz`
(SHA256 `9e4c76f1949312d7de7bbdc4d64cbf92ca9dcd8cca02c2dfa27dfae468e39554`).

## Controllo di attribuzione condiviso, 21 ottobre 2026

[Rapporto](../controllo-attribuzione-2026-10-21.md),
[descrittore](2026-10-21-controllo-attribuzione.json),
[backup](2026-10-21-controllo-attribuzione-audit.tar.gz),
[checksum](2026-10-21-controllo-attribuzione-audit.tar.gz.sha256).
Offline, zero chiamate LLM, preregistrato. Replay su 92 audit: classe del CF (K1) perde 39
corrette e coerenza delle attestazioni (K2) 147, quindi esclusi; organizzazione
nell'attestazione (K3) 0, implementata solo per le nuove sessioni. Equivalenza verificata;
13 test, suite completa e Ruff PASS. Grezzo
`backend/data/compilation-audit/attribution-safety-20261021-01/`.

## P2, attribuzione di ruolo a livello di record, 21 ottobre 2026

[Rapporto](../p2-attribuzione-record-2026-10-21.md),
[descrittore](2026-10-21-p2-record-binding.json),
[backup](2026-10-21-p2-record-binding-audit.tar.gz),
[checksum](2026-10-21-p2-record-binding-audit.tar.gz.sha256).
Offline, zero chiamate LLM, preregistrata. Simulazione: 47 recuperi corretti, 0 errati,
0 regressioni, rifiuti Cesano e amministratore cessato preservati. Seconda serie di
controesempi: 5 negativi su 11 recuperati, gli stessi accettati anche dal gate V12/V14
con citazioni corrette. Regola non implementata; grezzo
`backend/data/compilation-audit/p2-record-binding-20261021-01/`.

## Candidata V14, autorizzazione delle clausole d'opzione, 21 ottobre 2026

[Rapporto](../v14-autorizzazione-clausole-opzione-2026-10-21.md),
[descrittore](2026-10-21-v14-option-authorization.json),
[backup](2026-10-21-v14-option-authorization-audit.tar.gz),
[checksum](2026-10-21-v14-option-authorization-audit.tar.gz.sha256).
Offline, zero chiamate LLM. Ricevuta di solo ramo: CCIAA esportate 21/21 con V13, 0/21
con V14. Replay di 82 DOCX: rimosse 4 CCIAA e 9 `p19.ft0` Cesano (solo selezioni), nessuna
altra modifica. 16 test nuovi, suite 3.380 PASS, Ruff PASS. Candidata non adottata.

## Diagnosi CCIAA, generalità di R2 e veto delle opzioni, 21 ottobre 2026

[Rapporto](../cciaa-r2-veto-opzioni-2026-10-21.md),
[descrittore](2026-10-21-cciaa-r2-diagnosi.json),
[backup](2026-10-21-cciaa-r2-diagnosi-audit.tar.gz),
[checksum](2026-10-21-cciaa-r2-diagnosi-audit.tar.gz.sha256).
Offline, zero chiamate LLM. CCIAA: valore corretto, autorizzazione della dichiarazione
mancante; riferimento senza questa dimensione, giudizi coerenti (18 prove aperte con
SKIP, 2 scritte senza condizione). R2 non generalizza: struttura Word piatta, figli
senza «:», contenuti condivisi, marcatori «[ ]»/U+F06F, condizioni solo testuali.
R1T con sblocco da ricevuta USER: 4/4 CCIAA bloccate, 0 su 802 corrette. Proposta non
implementata; grezzo `backend/data/compilation-audit/cciaa-r2-diagnosi-20261021-01/`.

## Esperimento offline A su P1, 21 ottobre 2026

[Rapporto](../p1-esperimento-offline-a-2026-10-21.md),
[descrittore](2026-10-21-p1-offline-a.json),
[backup](2026-10-21-p1-offline-a-audit.tar.gz),
[checksum](2026-10-21-p1-offline-a-audit.tar.gz.sha256).
Offline, zero chiamate LLM; preregistrazione prima dei risultati. 17 risposte Minervino,
21 CRAA, 806 scritture verificate. Con protocollo corretto il dialogo attuale ottiene
262 scritture contro un tetto oracolo di 268; raggruppare le condizioni LLM per decisione
dà controesempi in 17/17 risposte e non ferma le CCIAA. P1 ridimensionata; grezzo
`backend/data/compilation-audit/p1-offline-a-20261021-01/`.

## Unica prova reale chat V12 dopo gli hold, 19 ottobre 2026

[Rapporto](../prova-chat-v12-hold-2026-10-19.md),
[misure](2026-10-19-v12-holds-chat.json),
[otto tracciati](2026-10-19-v12-holds-chat-trace.json),
[controlli](2026-10-19-v12-holds-chat-checks.json),
[backup](2026-10-19-v12-holds-chat-audit.tar.gz),
[checksum](2026-10-19-v12-holds-chat-audit.tar.gz.sha256),
[descrittore](2026-10-19-v12-holds-chat-archive.json).
Una sola sessione,stessa globale congelata suFORM/56SOURCE/schemaidentici,
router/guard/narratorereali. Stessi3messaggiUSER,nessunaricevutacopiata.
61scritture=60SOURCEtesti+1USERcheckbox,8DTnon sospesi,52precedenti conservati;
DOCXidentico alreplay61,0nuoveindebite osservate.0holdSOURCElegittimi nelcampione;
18negativi offline esistenti passati,5gruppiUSER ancora aperti/4testivuoti.
7chiamate/69815token,0nuoveglobali/1riuso,0retry.9pagine;249filecodice/fixture
immutati. Ripresa stessaUI conPTY perstdin chiuso,non secondasessione oLLMretry.
Bundle indipendente ricostruisceaudit/Word senzadatabase/chiavi;nessuncommit/push.

## Hold del narratore V12, 19 ottobre 2026

[Rapporto](../hold-narratore-v12-2026-10-19.md),
[misure](2026-10-19-v12-narrator-holds.json),
[otto tracciati](2026-10-19-v12-narrator-holds-trace.json),
[controlli](2026-10-19-v12-narrator-holds-checks.json),
[backup](2026-10-19-v12-narrator-holds-audit.tar.gz),
[checksum](2026-10-19-v12-narrator-holds-audit.tar.gz.sha256),
[descrittore](2026-10-19-v12-narrator-holds-archive.json).
Storico:8hold MODEL nuovi nella terza sintesi,8ereditati all'export,motivo non
registrato. Due prove mirate reali dopo esaurimento degli artefatti:
con/senza prova composta entrambe8hold,confermaUSER attuale delruolo ridondante.
Sola esposizione delle prove insufficiente; finale motivi citati e verifica
restrittiva dello stesso requisito già attestato. BMODEL conserva8,backend
respinge8motivi ridondanti. Quattroreplay:53,53,61,53(controllonegativoSOURCE).
Tutti52testi+1casella conservati,8DTrecuperati offline,0nuovi indebiti osservati.
NessunanuovaUI/globali,2sintesireali/22140token.26testnuovi,210mirati,2627suite,
Ruff passati. Bundle ricostruisce4DOCX senzaDB/chiavi/rete con codicearchiviato.
FORM/grounding/writer invariati,nessuncommit/push;5gruppiUSER ancora aperti.

## Direttore e checkbox V12, 19 ottobre 2026

[Rapporto](../rami-v12-direttore-checkbox-2026-10-19.md),
[misure](2026-10-19-v12-branches.json),
[otto tracciati](2026-10-19-v12-branches-trace.json),
[controlli](2026-10-19-v12-branches-checks.json),
[backup](2026-10-19-v12-branches-audit.tar.gz),
[checksum](2026-10-19-v12-branches-audit.tar.gz.sha256),
[descrittore](2026-10-19-v12-branches-archive.json).
Replay prima dellaUI:52→60testi+1casella=61,8DT sbloccati da proveFORM/USER/SOURCE
distinte; stessi52valori precedenti. Gruppo7opzioni validato,cardinalitàUNKNOWN;
sola spunta positiva dalla ricevuta corrispondente,0deselezioni. Nuova chat
isolata conglobale salvata/providerconversazionale reale:52testi+1casella=53,
8DT grounded/applicabili ma sospesi dalnarratore. Hold non forzati o cancellati;
motivo non emesso dallo schema, ipotesi distinta dai fatti.0nuoveglobali,
7chiamate/61977token.34test nuovi,243mirati,2601suite/Ruff passati.9pagine,
0valori precedenti persi,0nuovi indebiti osservati. Verifica bundle senzaDB/chiavi
ricostruisce entrambi iDOCX. FORM/modello/writer immutati,nessun commit/push/E1.

## Copertura SOURCE V12, 18 ottobre 2026

[Rapporto](../copertura-source-v12-2026-10-18.md),
[misure](2026-10-18-v12-source-coverage.json),
[18 tracciati](2026-10-18-v12-source-coverage-trace.json),
[controlli](2026-10-18-v12-source-coverage-checks.json),
[backup](2026-10-18-v12-source-coverage-audit.tar.gz),
[checksum](2026-10-18-v12-source-coverage-audit.tar.gz.sha256),
[descrittore](2026-10-18-v12-source-coverage-archive.json).
Stessa risposta globale e stessi56SOURCE: tutti18vuoti erano proposti con dati
disponibili. Riuso da scelta nominativa USER registrata, prove FORM fisiche e
proprietà di iscrizione collegate solo con identità verificata. Replay42→52:
9generalità/carica firmatario+Comune,0precedenti persi/cambiati,24soci conservati.
46→60grounded/revisionate;8DTUNKNOWN/rinviati restano vuoti;0nuove spunte.
Cinque decisioni USER invariate.51/52conformi al gold,1carica completa attestata
più ampia del gold,0nuove scritture indebite osservate. PDF9pagine prima/dopo.
43casi nuovi,304mirati e2567suite passati,Ruff; fallimenti conservati. Narratore
simulato e rete vietata, grounding/persistenza/export reali; verifica indipendente
senza DB/chiavi. Zero nuove LLM/UI, costi/token provider0. FORM/API/DB/modello/
writer invariati, E1 fermo. Raw v12-source-coverage-20261018-01/.

## Residui V12 e domande USER, 18 ottobre 2026

[Rapporto](../residui-v12-dialogo-2026-10-18.md),
[misure](2026-10-18-v12-residui.json),
[controlli](2026-10-18-v12-residui-checks.json),
[backup](2026-10-18-v12-residui-audit.tar.gz),
[checksum](2026-10-18-v12-residui-audit.tar.gz.sha256),
[descrittore](2026-10-18-v12-residui-archive.json).
Solo residui: valori equivalenti per maiuscole/spazi, cinque decisioni FORM
raggruppate, export parziale a domande aperte. Nessuna nuova LLM/UI o E1.
Replay storico42scritture(41SOURCE+1USER) conservate con stesso hashDOCX;
44→46grounded, due falsi conflitti eliminati, UNKNOWN3→4(non scritto).
Snapshot prima della scelta qualifica:42SOURCE/0valoriUSER, sempre con le
ricevute societàTRUE/DT SKIP. Non benchmark senzaUSER. Zero nuove spunte o
scritture indebite osservate;18vuoti SOURCE e decisioni della pratica restano.
Ricevute raggruppate non autorizzano scrittura automatica.45test nuovi,
221mirati e2524suite finale passati,Ruff. Rete vietata e narratore simulato;
validatori/persistenza/export reali, verifica indipendente bundle senza DB/chiavi.
Sessioni/storage originali invariati, nessun commit/push. Raw
backend/data/compilation-audit/v12-residui-20261018-01/.

## Revisioni e soci V12, 18 ottobre 2026

[Rapporto](../correzione-revisioni-soci-2026-10-18.md),
[misure](2026-10-18-v12-review-soci.json),
[24 tracciati](2026-10-18-v12-review-soci-trace.json),
[controlli](2026-10-18-v12-review-soci-checks.json),
[backup](2026-10-18-v12-review-soci-audit.tar.gz),
[descrittore](2026-10-18-v12-review-soci-archive.json).
Revisioni V12 conservate solo con impronta immutata; finestre40 sulle nuove
proposte, nessuna seconda globale. Prompt titolo+riga, validatori invariati.
Replay vecchio41→54, soci16→24SOURCE; solecitazioni27→43, soci8→24SOURCE.
NuovaUI:stessoinput,44grounded/reviewed,42scritture conformi,24soci nelDOCX
ma23SOURCE+1USER per falso conflitto Ingegnere/ingegnere. TreDT rinviati esclusi.
2479test passati,Ruff.11chiamate/181.776token,globale174,83s,costo stimato0,04563USD.
Nessuna accelerazione/stabilità generale dimostrata. Dialogo preferenze/
designazioni/attestazioni resta separato;FORM/modello/writer immutati,E1nonavviato.

## UI reale Minervino V12, 18 ottobre 2026

[Diagnosi](../diagnosi-e2e-v12-minervino-2026-10-18.md),
[misure](2026-10-18-v12-e2e-minervino.json),
[traccia dei 24 campi soci](2026-10-18-v12-e2e-soci.json),
[controlli](2026-10-18-v12-e2e-checks.json),
[backup](2026-10-18-v12-e2e-audit.tar.gz),
[descrittore](2026-10-18-v12-e2e-archive.json),
[checksum](2026-10-18-v12-e2e-audit.tar.gz.sha256).
UI/provider reali su runtime isolato:60SOURCE proposte,27grounded/revisionate/
scritte,27conformi al gold,33vuotiSOURCE. Soci24proposti corretti,8scritti;
16citazioni binding non letterali, controprova offline titolo+riga recupera16.
Vecchio16:otto revisioni Andrea già presenti perse dopo riuso e finestra40.
Una sola domanda di conferma,poi export;quattro argomenti USER mai chiesti.
Sette chiamate,153.384token,globale142,10s;cinquePOST154,76s. T0 V1 completo
diverso dal precedente compila:confronto non controllato del solo prompt.
Nessuna modifica applicativa o E1. Video completo e trace campionata nel bundle;
trace originale936MiB locale,DB/chiavi esclusi. GrezziHTTP di routeriniziale e
guard non acquisiti;totali conservati e limite documentato.

## Correzioni UI compilato(6), 18 ottobre 2026

[Rapporto](../correzioni-ui-compilato6-2026-10-18.md),
[misure](2026-10-18-ui-compilato6-fix.json).
[Backup](2026-10-18-ui-compilato6-fix-audit.tar.gz),
[descrittore](2026-10-18-ui-compilato6-fix-archive.json),
[checksum](2026-10-18-ui-compilato6-fix-audit.tar.gz.sha256) e
[controlli](2026-10-18-ui-compilato6-fix-checks.json).
Una sola prova globale reale del prompt: soci 24/24 proposti e grounded.
Replay isolati del riuso dopo USER: compilato6 25→33 scritture, B0 manuale
48→56; nuova proposta 41 scritture, 13 grounded non revisionate per limite40.
Narratore simulato nei replay, export e controlli reali. Una discordanza stretta
dal gold per carica più completa e attestata; nessun adattamento del gold.
Zero nuove chiamate per recuperare le generalità. Bari/BA e checkbox restano
irrisolti con causa documentata, controlli non allentati.

## Diagnosi del download UI compilato(6), 17 ottobre 2026

[Rapporto](../analisi-ui-compilato6-2026-10-17.md),
[misure](2026-10-17-ui-compilato6.json),
[controlli](2026-10-17-ui-compilato6-checks.json),
[backup](2026-10-17-ui-compilato6-audit.tar.gz).

Nuovo output reale dell'utente:25scritture24SOURCE+1USER.33omissioni e2rifiutiFORM
su35target SOURCE vuoti. Dati già presenti nell'input; prompt dei binding non
allineato alle nuove capacità del verificatore, scelta USER non ricollegata
agli8dati di Leonardo, soci eCFdirettore omessi dal modello e falsamente detti
assenti dal narratore. Tutte24grounded scritte, limite40 non raggiunto. Nessuna
nuova chiamata o modifica di codice/stato; nessuna misura controllata prima/dopo.

## Attivazione per prova UI, 17 ottobre 2026

[Guida](../prova-ui-compilazione-2026-10-17.md),
[controlli e misure](2026-10-17-ui-binding.json),
[backup](2026-10-17-ui-binding-audit.tar.gz).

Servizi locali avviati sul motore globale corrente con correzioni già presenti.
298 test backend mirati,8 E2E desktop/mobile e lint passati; una vecchia
asserzione E2E corretta dopo il fallimento conservato. Browser live in sola
lettura, nessuna nuova generazione reale.28sessioni invariate, modulo e56SOURCE
identici a B0. Le48review offline non vengono importate nella UI; narratore
con limite40proposte per passo ancora presente. Non è una misura qualitativa LLM.

## B0-03: export parziale verificato, 17 ottobre 2026

[Word](<../../nuovi dati/domanda-iscrizione.B0-03-PARZIALE-VERIFICATO.docx>),
[PDF](<../../nuovi dati/domanda-iscrizione.B0-03-PARZIALE-VERIFICATO.pdf>),
[rapporto](../export-b0-03-verificato-2026-10-17.md),
[misure](2026-10-17-b0-docx-verified.json),
[controlli](2026-10-17-b0-docx-verified-checks.json),
[backup](2026-10-17-b0-docx-verified-audit.tar.gz),
[checksum](2026-10-17-b0-docx-verified-audit.tar.gz.sha256).

Export reale sulla copia della stessa sessione B0-03, nessun nuovo provider:
47 SOURCE +1 nome USER, 26 pendenti riesaminate manualmente. Audit UNKNOWN
invariato e ricevute proprie distinte; limite di ambito c_p39 registrato.
Tre rifiuti conservati, 48 valori fisicamente corretti contro22 nel vecchio
Word (23 inseriti, uno errato). Gold solo dopo export. Tutte9 pagine PDF viste,
5 giunzioni senza spazio registrate; nessun writer corretto. 13 checkbox e
4 tabelle intatte. Non è un nuovo benchmark senzaUSER o di autonomia del modello.

## Applicabilità UNKNOWN: studio offline, 17 ottobre 2026

[Rapporto](../applicabilita-b0-index-2026-10-17.md),
[registro e misure](2026-10-17-applicability.json),
[bundle](2026-10-17-applicability-audit.tar.gz),
[checksum](2026-10-17-applicability-audit.tar.gz.sha256),
[controlli](2026-10-17-applicability-checks.json).

Tre condizioni semantic senza operandi: B0 47, INDEX 9+16 proposte. USER
proprio di B0 già registrato, audit immutabile UNKNOWN e overlay del dialogo
separati. INDEX con USER è test distinto con mapping da INDEX-03. Preflight
47/25 SOURCE e nome USER passati; revisione B0 21 valide/26 nuove da rivedere.
Zero choice_groups: confermare la condizione non spunta la checkbox. Piano
per 47 SOURCE + 1 USER soltanto proposto, nessun DOCX o controllo modificato.
Nessuna nuova chiamata, framework, commit o push; suite precedenti non rieseguite.

## Ultima correzione SOURCE e replay, 17 ottobre 2026

[Rapporto](../correzione-binding-source-finale-2026-10-17.md),
[misure e tracciati](2026-10-17-binding-final.json),
[bundle](2026-10-17-binding-final-audit.tar.gz),
[checksum](2026-10-17-binding-final-audit.tar.gz.sha256),
[controlli](2026-10-17-binding-final-checks.json).

Baseline riprodotta esattamente. Prima quattro prove esatte del binding:
B0 38→42, INDEX 23→23. Poi titoli/date e identità con chiavi concordanti:
finali B0 47 (+9), INDEX 25 (+2), undici recuperi conformi su dieci destinazioni.
Zero nuove grounded non conformi o perse; cinque rifiuti necessari mantenuti.
Identità/ruolo/valore separati, applicabilità ancora unknown, nessuna scrittura,
USER, generazione LLM o export. 57 nuovi casi, 274 mirati/2.431 backend passati,
Ruff. Controesempi red e prove intermedie conservati. Writer, API, FORM B0,
modello/thinking e fixture invariati. Arresto dopo replay, nessun commit/push.

## Diagnosi degli undici SOURCE residui, 17 ottobre 2026

[Rapporto](../diagnosi-undici-source-2026-10-17.md),
[tracciati e misure](2026-10-17-residual-source-diagnosis.json),
[bundle](2026-10-17-residual-source-diagnosis-audit.tar.gz),
[checksum](2026-10-17-residual-source-diagnosis-audit.tar.gz.sha256),
[controlli](2026-10-17-residual-source-diagnosis-checks.json).

Diagnosi senza implementazione, nuovi replay dei validatori o chiamate LLM.
11 occorrenze/10 destinazioni: 4 prove congiunte esatte già nel binding,
3 nomi con onorifico in altro record, 1 data con rappresentazione diversa,
3 collegamenti socio/direttore. Nessun valore o ruolo assente dall'input;
per sette resta una decisione su associazione/equivalenza. Nessuna nuova
accettazione o misura dei falsi positivi. Applicabilità separata e ancora
sconosciuta, nessun USER nei due input, codice/fixture/vecchi raw invariati.

## Comune e contesto FORM, 17 ottobre 2026

[Rapporto](../comune-contesto-form-2026-10-17.md),
[misure](2026-10-17-field-context.json),
[bundle](2026-10-17-field-context-audit.tar.gz),
[checksum](2026-10-17-field-context-audit.tar.gz.sha256),
[controlli](2026-10-17-field-context-checks.json).

KISS SOURCE conservato. Compatibilità fisica del Comune nel validatore condiviso
ed elenco numerato con schede ripetute per il contesto V12; FORM/input invariati.
18 prove FORM sufficienti ora riconosciute: +11 proposte corrette, sette rifiuti
SOURCE mantenuti. Eliminato p41.s1 improprio in entrambe le risposte: B0 27→38
corretti e INDEX 23→23, zero grounded non conformi nei due replay finali. Quote,
condizioni e fatti preservati; nessuna scrittura o nuovo USER/provider/export.
30 nuovi casi, 211 mirati/2.374 backend passati, Ruff. Controesempi intermedi
conservati e risolti prima del replay; nessun commit/push o modifica al writer.

## Correzione binding KISS e replay, 17 ottobre 2026

[Rapporto](../correzione-binding-kiss-2026-10-17.md),
[misure](2026-10-17-binding-kiss.json),
[bundle](2026-10-17-binding-kiss-audit.tar.gz),
[checksum](2026-10-17-binding-kiss-audit.tar.gz.sha256),
[controlli](2026-10-17-binding-kiss-checks.json).

Correzione autorizzata solo del verificatore V12: prova tabellare strutturale
e recupero da record SOURCE del fatto. Nessun join di persone/chunk, nuova
citazione del valore o approvazione di applicabilità. 40 nuovi casi, 133 mirati
e 2.344 backend passati; Ruff. Zero nuove richieste provider o export.
B0-03 recupera 6 valori, INDEX-01 root isolato 5: 11/11 conformi, tutti ancora
condizionati. Nessuna nuova accettazione indebita osservata; persiste l'errore
preesistente p41.s1 in entrambe le risposte. Residui 22+3 distinti per fatto,
contesto FORM e record SOURCE. Originali, gold e audit precedenti invariati.
Fermato dopo replay/rapporto, nessun commit/push. FORM/coverage/thinking invariati.

## Replay INDEX-01, USER e reasoning, 17 ottobre 2026

[Rapporto](../replay-index01-user-reasoning-2026-10-17.md),
[misure](2026-10-17-root-user-reasoning.json),
[bundle](2026-10-17-root-user-reasoning-audit.tar.gz),
[checksum](2026-10-17-root-user-reasoning-audit.tar.gz.sha256),
[controlli](2026-10-17-root-user-reasoning-checks.json).

Nessuna nuova generazione; un GET /models. Quarantena offline dei soli due
metadati root: schema passa, 19 grounded/18 conformi. Export senza conferme
bloccato; copia vuota esplicita e distinto test con due risposte USER archiviate
che scrive 19 SOURCE/18 conformi. Non un nuovo run provider o recupero storico.
Trasporto USER registrati implementato; senza USER input e request identici a B0.
79 mirati/2.304 backend passati, Ruff. B0-03 soci: 23 fatti grounded/una quote errata,
tre binding respinti e nove collegamenti chunk esterni. Thinking A/B solo proposto,
body NOT-SENT. Coverage/FORM/schema/gate/writer invariati, nessun commit/push.

## Diagnosi offline output, 17 ottobre 2026

**Stop compattazione FORM richiesto dall'utente. B0 resta riferimento;
compact-v1 e compact-index-v2 non vanno integrate.** Nessuna nuova chiamata,
modifica di codice/prompt/validatori/writer o commit.

[Rapporto](../diagnosi-contratto-risposta-b0-e1-2026-10-17.md),
[misure](2026-10-17-output-diagnosis.json),
[bundle derivati](2026-10-17-output-diagnosis-audit.tar.gz),
[checksum](2026-10-17-output-diagnosis-audit.tar.gz.sha256),
[verifiche](2026-10-17-output-diagnosis-checks.json).

Nove analisi storiche: rifiuto envelope e troncamento distinti, nessun timeout
nei due INDEX falliti. Output 349.460, reasoning 273.801 (78,35%). Otto JSON
completi, 634 record, zero duplicati esatti o fatti inutilizzati; coverage 210
record / 34,22% caratteri. 540 prove SOURCE presenti nei messaggi realmente inviati;
49 valori conformi bloccati localmente su sette audit, 25 persi al rifiuto globale.
Proposta minima coverage sparsa, senza implementazione o nuovi test LLM.
Archivio di soli derivati e riferimenti/hash ai tre bundle originali invariati.

## E1 indice diretto, 17 ottobre 2026

[Rapporto](../esperimento-e1-index-2026-10-17.md),
[misure](2026-10-17-e1-index.json),
[bundle](2026-10-17-e1-index-audit.tar.gz),
[checksum](2026-10-17-e1-index-audit.tar.gz.sha256),
[archivio](2026-10-17-e1-index-archive.json),
[verifiche finali](2026-10-17-e1-index-checks.json).

compact-index-v2 approvato, implementato nel solo runner e misurato su tre
analisi reali dello stesso Minervino completo. Input -13,31% token B0;
prima risposta rifiutata per chiavi extra, seconda troncata al limite output,
terza accettata. Nessun retry/riparazione; unico Word con 21/60 conformi,
nessun argomento USER chiesto, tutti i soci omessi. N/D per i due Word non
prodotti, nessuna media qualità sui soli successi. Variante non adottata.

137 mirati e 2.279 backend passati, Ruff; iniziale E501 conservato e corretto
prima del congelamento. Nove chiamate totali, 353.942 token, cache/storia
provider non controllate. Scorer identico B0, 267 destinazioni e 110 celle
verificate, visione campionata 1/3/10, cinque SOURCE live identiche.
Bundle 250 file, 3.250.464 byte, SHA-256
e0f586cf03775c9a699be31b7d75d704af5b61609411fbbdb13d74284dda33fc.
DB/credenziali esclusi; nessun commit/push, solo copie E1INDEX-RUN-03 in nuovi dati.
E2 non avviato, prova separata su contratto output/budget reasoning proposta.

## E1 FORM compatto completo, 16 ottobre 2026

[Rapporto](../esperimento-e1-form-compatto-2026-10-16.md),
[misure](2026-10-16-e1-form.json),
[bundle](2026-10-16-e1-form-audit.tar.gz),
[checksum](2026-10-16-e1-form-audit.tar.gz.sha256),
[archivio](2026-10-16-e1-form-archive.json),
[verifiche finali](2026-10-16-e1-form-checks.json).

compact-v1 approvato e implementato soltanto nel banco di prova. Tre analisi
DeepSeek reali, stesso input canonico/fonti di B0, adattamento del solo formato
e istruzioni di lettura. FORM -36,02% caratteri, input -16,09% token reali,
totale medio analisi -15,27%. Word 14/11/23 target conformi su 60 contro
23/17/22 B0; nessun argomento USER chiesto, stop fuori copione nel secondo.
Variante conservata, non adottata nella chat; E2 ancora da avviare.

116 mirati e 2.258 backend passati, Ruff; quattro fallimenti iniziali delle
aspettative dei nuovi test conservati e corretti senza cambiare parser/gold.
267 destinazioni e struttura verificati, tre Word/PDF, visione campionata.
27 chiamate e 413.624 token complessivi, cache non uniforme; nessuna equivalenza
statistica o fattura dedotta. Bundle 386 file, 6.711.650 byte, SHA-256
9cafd05bb2db9d4180aa37d9d47cfb79ad88b9b8bb7bd4a26bdf2215af6516d5.
Nessun DB/credenziale nel bundle, nessun commit/push. Copie per revisione in nuovi dati.

## Baseline B0 Minervino con provider reale, 16 ottobre 2026

[Rapporto](../baseline-minervino-b0-2026-10-16.md),
[misure](2026-10-16-minervino-b0.json),
[bundle](2026-10-16-minervino-b0-audit.tar.gz),
[checksum](2026-10-16-minervino-b0-audit.tar.gz.sha256),
[dettagli archivio](2026-10-16-minervino-b0-archive.json),
[verifiche finali](2026-10-16-minervino-b0-checks.json).

Tre analisi reali DeepSeek flash/thinking sullo stesso input e tre continuazioni
dei servizi isolati fino al Word; non browser/endpoint HTTP o ingestion. Nessun
motore modificato, fixture Minervino V1 e Labirinto invariati. Word con 23/17/22
valori conformi sui 60 target documentati, provenienza SOURCE/USER distinta;
nessuno dei quattro argomenti USER del copione chiesto, checkbox/preferenze
attese non selezionate. Omissioni e rifiuti di binding separati nel rapporto.

30 chiamate, 481.199 token; 75.864 input per analisi, tutte con cache calda;
tempi analisi 146,73–183,85 s. Controlli indipendenti delle 267 destinazioni,
OOXML e rendering LibreOffice campionato. Firma su pagina quasi vuota;
non certificato il layout Microsoft Word. Artefatti e fallimenti diagnostici
conservati, nessun retry per migliorare gli esiti. Bundle 348 file, 6.423.265 byte,
senza DB o credenziali; SHA-256 85d2d441e0edb297a4d4955929eca8c8ca3c61545fef1be6de5f9575c69009ee.
E1/E2 ancora da implementare; nessuna suite applicativa o pubblicazione Git
in questo aggiornamento. Copie Word/PDF per revisione nella cartella nuovi dati.

## Contesto e ruoli, 12 ottobre 2026

[Report](../benchmark-contesto-ruoli-2026-10-12.md),
[JSON completo](2026-10-12-role-context.json),
[bundle delle due serie](2026-10-12-role-context-audit.tar.gz),
[checksum](2026-10-12-role-context-audit.tar.gz.sha256),
[verifiche finali](2026-10-12-role-context-final-checks.json).

Dodici chiamate reali deepseek-flash V10/catalogo V5, due serie congelate: sette
sul contesto/record personali, cinque dopo il solo richiamo TASK alla copertura.
Minervino recupera personali in 3/4, recapiti corretti 4/4. Catanzaro prima omette
cinque dati societari, poi li conserva 3/3; direttore ancora perso per quote FORM
o disposition=value con unknown. Labirinto 18 target letterali in 4/4 ma 17
conservati nella terza iniziale. Checkbox/ambiguous vs conflicting/NA non chiusi.
Tutti gli esiti negativi conservati. 170 ipotesi SOURCE, zero RESOLVED/DOCX/USER/
sessioni, DB e originali invariati. 765.186 token, nessun risparmio input provato.
417 mirati/1.823 backend passati prima della prima serie; dopo il solo TASK
417 mirati e Ruff, non completa/frontend. Bundle 431 file, 3.900.981 byte.

## Destinazioni inline, 12 ottobre 2026

[Report](../benchmark-destinazioni-inline-2026-10-12.md),
[JSON completo](2026-10-12-slot-anchors.json),
[bundle](2026-10-12-slot-anchors-audit.tar.gz),
[checksum](2026-10-12-slot-anchors-audit.tar.gz.sha256) e
[verifiche finali](2026-10-12-slot-anchors-final-checks.json).

Sette chiamate reali deepseek-flash, V9/catalogo V4, una chiamata per prova:
Minervino recapiti corretti 3/3, riga critica sei/tre/sei proposte; Labirinto
18/22 corrispondenze letterali in 3/3; Catanzaro cinque dati societari conservati.
Nessuno slittamento osservato, copertura/ruoli/applicabilità ancora incompleti,
una quote semanticamente debole. 368.132 token, 505,02 s AI sommati, input più
grande. Zero RESOLVED/DOCX/USER/sessioni; intero DB live/originali invariati.
**391 mirati / 18,40 s e 1.797 backend / 119,09 s passati**, Ruff/fixture/diff/replay/body/archive verificati.
Il controllo versione aggiunto dopo le API conserva audit/body identici per tutte
le sette acquisizioni; raw e codice congelato restano quelli realmente usati.

## Tre bandi reali, 12 ottobre 2026

Richiesta esplicita su tutti e tre, nessun sorteggio: Catanzaro, Minervino,
Trapani. [Report completo](../benchmark-tre-bandi-2026-10-12.md),
[JSON di tutti i candidate/esiti](2026-10-12-tre-bandi.json),
[bundle delle acquisizioni](2026-10-12-tre-bandi-audit.tar.gz) e
[checksum](2026-10-12-tre-bandi-audit.tar.gz.sha256).

Dodici chiamate reali deepseek-flash su codice/fonti/body congelati, dieci
risposte complete e due timeout; 597.919 token osservati, usage timeout ignoto.
91 ipotesi conditional, zero RESOLVED/scritture. Catanzaro/Trapani ripetono i
dati societari; Minervino presenta tre destinazioni sbagliate con SOURCE valide.
Affidabilità insufficiente anche rimandando checkbox/ordine; nessun gold o %.
314 test mirati, otto verifiche fixture Catanzaro, Ruff/fixture/replay/archivio
verificati. Codice applicativo invariato, completa/frontend non ripetuti.
Integrità DB parziale: sessioni/corpus/originali invariati, indici/derivati
cambiati durante reload del server live; dettaglio nel report, nessun ripristino.

## Prove occasionali su altri bandi

Affiancano il benchmark fisso senza cambiarne gold/fonti/aspettative. Scelta
casuale registrata, tutti gli esiti conservati; senza gold nessuna accuratezza %.

- [Trapani Green, 11 ottobre 2026](../benchmark-trapani-casuale-2026-10-11.md):
  una chiamata reale deepseek-flash, 115 candidate e 17 SOURCE ammesse; risposta
  vuota, zero proposte, nessuna scrittura. **Esito negativo di copertura**,
  nessuna modifica al motore. [Audit/metriche](2026-10-11-trapani-casuale.json),
  [bundle](2026-10-11-trapani-casuale-audit.tar.gz) e
  [checksum](2026-10-11-trapani-casuale-audit.tar.gz.sha256).
  Replay/manifest/codice/originali/fingerprint/Ruff/fixture check verificati;
  suite software/frontend non ripetute, codice e contratti invariati.

## Modulo labirinto dedicato, 11 ottobre 2026

- [Alternative SOURCE](../benchmark-alternative-source-2026-10-11.md): contratto
  6, una chiamata per prova, sei acquisizioni su due commit congelati. Recapiti
  e polizze separati in 6/6; soggetto/ruolo e applicabilità ancora da verificare.
  [Prima serie](2026-10-11-labirinto-alternatives-v6.json),
  [finale](2026-10-11-labirinto-alternatives-v6b.json),
  [bundle](2026-10-11-labirinto-alternatives-audit.tar.gz) e
  [checksum](2026-10-11-labirinto-alternatives-audit.tar.gz.sha256).
  Finali 264 mirati/1.670 backend, Ruff/check/help/replay/diff. Zero scritture;
  ultima serie +14,67% token medi vs V3, nessun risparmio E2E dimostrato.

- Contesto fisico: [V2](2026-10-11-labirinto-context-v2.json),
  [V3 corrente](2026-10-11-labirinto-context-v3.json),
  [registro](../../relazioni.md). Sei chiamate reali; V3 conserva 18/22 valori
  attesi, cinque societari corretti, sede coincidente NA in 2/3. Beneficio
  semantico parziale, polizza/recapiti ancora impropri e nessuna scrittura.
  [Bundle delle due iterazioni](2026-10-11-labirinto-context-audit.tar.gz) e
  [checksum](2026-10-11-labirinto-context-audit.tar.gz.sha256).
  Finali 230 mirati/1.636 backend, Ruff/check/help/diff; frontend invariato.

- [Fixture V1](../../demo-documents/benchmark-compilazione/v1/README.md): Word
  sintetico con 55 posizioni/11 checkbox, sette SOURCE fittizie, gold autoriale
  escluso dal prompt e manifest. Runner `--fixture`, senza ingestion o corpus DB.
- [Registro permanente](../../relazioni.md) e
  [baseline per candidate](2026-10-11-labirinto-v1-baseline.json).
- Tre chiamate reali DeepSeek su `5e8cecc`, stesso input: 18/22 valori attesi
  proposti, 12 passano i gate; errori semantici variabili, nessuna attivazione
  o scrittura. Tempi 9,49–12,01 s sul corpus piccolo, non una misura E2E.
- [Bundle](2026-10-11-labirinto-v1-audit.tar.gz) e
  [checksum](2026-10-11-labirinto-v1-audit.tar.gz.sha256): tutte le acquisizioni,
  codice e fixture congelati, confronto e controlli; nessuna chiave/DB.
- 209 mirati/1.615 backend passati, Ruff/check/help/diff; frontend invariato.

## Proposte sparse e validazione locale, 11 ottobre 2026

- [Report completo](../benchmark-proposte-sparse-2026-10-11.md) e
  [metriche/annotazioni](2026-10-11-compilation-global-sparse.json).
- Quattro chiamate reali in due coppie congelate: prime due rifiutate, ultime
  due con 9/8 grounded conservati e rifiuti locali, ~20/31 s. Errori semantici
  ancora presenti: nessuna attivazione, RESOLVED o scrittura.
- [Bundle completo](2026-10-11-global-sparse-audit.tar.gz) e
  [checksum](2026-10-11-global-sparse-audit.tar.gz.sha256): tutti i grezzi,
  codice/input/schema/request/HTTP/output, validazioni, manifest, analisi e log.
  Esclusi database, configurazioni private e credenziali.
- Finali 188 test mirati/1.594 backend, Ruff/help/diff; V1/frontend invariati.

## Proposta compatta e origine canonica, 10 ottobre 2026

- [Report completo](../benchmark-proposta-compatta-2026-10-10.md),
  [usage/errori/annotazioni](2026-10-10-compilation-global-compact.json).
- Sei chiamate reali, tre coppie a codice congelato; stesso Word e 51 SOURCE.
  Tutte rifiutate, ultime due ~47 s/~88.700 token. Nessuna attivazione/RESOLVED.
- [Bundle completo](2026-10-10-global-compact-audit.tar.gz) e
  [checksum](2026-10-10-global-compact-audit.tar.gz.sha256): prompt, risposte anche
  fallite, codice congelato, originali, manifest, annotazioni e controlli.
  Niente DB/credenziali. Grezzi locali `global-compact-20261010-*`.
- Finali 148 test mirati/1.544 backend, Ruff/help/diff; V1 e frontend invariati.

## Fatti e condizioni condivisi, 10 ottobre 2026

- [Report del secondo esperimento](../benchmark-condizioni-globali-2026-10-10.md)
  e [riepilogo/annotazioni](2026-10-10-compilation-global-conditions.json).
- Due proposte complete senza condizioni estratte; confronto con thinking low
  troncato/rifiutato. Nessun miglioramento semantico o token dimostrato.
- Cinque valori aziendali ancora supportati, ma fatti compositi e rami non
  verificati: nessuna promozione a RESOLVED o attivazione nella chat.
- [Bundle completo](2026-10-10-global-conditions-audit.tar.gz) e
  [checksum](2026-10-10-global-conditions-audit.tar.gz.sha256): prompt, risposte,
  errori, usage, codice, controlli e annotazioni senza database o credenziali.
- 110 test mirati/1.506 backend completi, Ruff, help e diff; originali invariati.

## Proposta globale reale, 10 ottobre 2026

- [Report, limiti e decisione](../benchmark-proposta-globale-2026-10-10.md).
- [Riepilogo JSON e annotazioni semantiche](2026-10-10-compilation-global.json)
  e [prima prova](2026-10-10-compilation-global-run1.json).
- Tre chiamate DeepSeek reali, intero catalogo 307 posizioni, corpus completo
  piccolo di 51 SOURCE. Stesso originale della baseline V1, zero USER.
- Grezzi permanenti `backend/data/compilation-audit/global-20261010-run1/`,
  `global-20261010-run2/`, `global-20261010-run3/`, con manifest e codice congelato.
- Nessuna modifica di sessioni/renderer/chat: grounded non significa RESOLVED.
  Un JSON è rifiutato; rilevati falsi positivi di applicabilità, conservati nel report.
- [Bundle grezzi versionato](2026-10-10-global-proposal-audit.tar.gz) e
  [checksum SHA-256](2026-10-10-global-proposal-audit.tar.gz.sha256): 78 file,
  tre prove, replay, log software e cataloghi strutturali precedenti. Confrontato
  byte per byte con le acquisizioni locali; escluse credenziali/configurazioni
  private/database. Sarà trasferibile con Git, senza dipendere da `backend/data/`.

## Catalogo strutturale, 10 ottobre 2026

- [Contratto, limiti e comando di ripetizione](../catalogo-compilazione.md).
- [Misure JSON](2026-10-10-compilation-catalog.json): candidate testo/checkbox,
  dimensioni e tempi dell'estrazione deterministica, originali verificati.
- Grezzi permanenti: `backend/data/compilation-audit/catalog-20261010/`, con
  cataloghi delle fixture Catanzaro/Minervino, misure e log dei controlli.
- Zero chiamate AI: non è una valutazione semantica del modello né una nuova
  misura della latenza di compilazione. Dati grezzi locali esclusi da Git.

## Latenza compilazione, 10 ottobre 2026

- [Report e confronto Gemma/DeepSeek](../diagnosi-latenza-compilazione-2026-10-10.md).
- [Riepilogo JSON](2026-10-10-compilation-latency.json): configurazioni pubbliche,
  tempi, token, riepiloghi di stato, valori/quote SOURCE dei primi 12 candidate
  e controlli. Questo file e il report sono versionabili insieme al codice.
- [Bundle Gemma/DeepSeek per il checkpoint Git](2026-10-10-latency-audit.tar.gz),
  con [checksum](2026-10-10-latency-audit.tar.gz.sha256): conserva anche i grezzi
  dei due benchmark isolati senza credenziali, database o snapshot delle sessioni
  storiche dell'utente. Aggiunto su richiesta di salvare il lavoro su GitHub
  prima di iniziare il nuovo motore. I manifest interni verificano i singoli file.
- Acquisizioni locali permanenti, nella radice del repository:
  `backend/data/compilation-audit/latency-20261010-gemma/`,
  `latency-20261010-deepseek/` e `latency-20261010-historical/`.
  Ogni cartella contiene un manifest SHA-256; le cartelle storiche sono letture
  di sessioni precedenti, non prove appena eseguite.
- Archivio trasportabile delle tre cartelle:
  `backend/data/compilation-audit/latency-20261010.tar.gz`, con checksum nel
  file `.tar.gz.sha256` adiacente. Anche questo archivio è locale.

`backend/data/` è esclusa da Git: **un push non salva i dati grezzi su GitHub**.
Il bundle esplicitamente versionato sopra è l'eccezione per i due benchmark
isolati; i dati storici e gli altri audit restano locali. Per spostarli o
conservarli altrove copiare l'archivio locale con il suo checksum.
Non aggiungere credenziali, file `.ai-key`, header Authorization o database
contenenti impostazioni riservate al repository o ai bundle diagnostici.

Il bundle DeepSeek contiene prompt/schema e body realmente inviati, risposte
del provider, tempi/token, query ed evidenze SOURCE, risultati delle fasi,
snapshot della sessione dopo ogni passo, CSV completo, revisioni e verifiche.
Il bundle Gemma conserva quanto acquisito originariamente: i suoi prompt
non furono registrati. Non vengono spacciate ricostruzioni per tracce reali.
I database e gli indici di lavoro sono temporanei; lo stato esportato è durevole.

## Ripetere la misura

Dalla directory `backend`, con profili/KB locali già configurati:

```bash
PYTHONPATH=. uv run --locked python scripts/benchmark_compilation_latency.py \
  --project minervino-di-lecce-elenco-sia --form-id 153 \
  --profile-project prova \
  --output data/compilation-audit/latency-deepseek-NUOVA-PROVA \
  --max-steps 6 --max-seconds 420 \
  --stop-candidate-id t0.r5.c1 --stop-candidate-id t0.r6.c1 \
  --stop-candidate-id t0.r7.c1 --stop-candidate-id t0.r9.c1 \
  --stop-candidate-id t0.r10.c1
```

ID e progetto sono gli input di questa misura, non condizioni hardcoded nel
motore. Per un altro documento scegliere gli ID reali e il profilo desiderato.
La directory di output deve essere nuova: lo script rifiuta di sovrascriverla.
Il runner copia SQLite/storage/indice Qdrant locale e delega alle funzioni reali
di creazione/resolve con provider reale; non modifica profili o sessioni live.
Non supporta un indice Qdrant remoto per questa prova isolata.
Il budget massimo accettato è 36 passi/600 s, default sei passi/420 s; ogni passo
mantiene il timeout applicativo. Niente input USER o generazione DOCX implicita.
La strumentazione non sostituisce le risposte AI e non alleggerisce i validator.

È una misura del percorso automatico backend, non del routing/browser completo.
Non copre la gestione degli errori aggiuntiva della route HTTP. In caso di
failure registra gli artefatti e si ferma, senza correggere il codice in corsa.

## Copertura testuale e rinvii locali, 13 ottobre 2026

[Report](../compilazione-copertura-2026-10-13.md),
[protocollo](2026-10-13-text-coverage-protocol.json),
[metriche](2026-10-13-text-coverage.json),
[bundle](2026-10-13-text-coverage-audit.tar.gz),
[manifest](2026-10-13-text-coverage-manifest.json).
Due serie DeepSeek con stesso Minervino/SOURCE; quattro dati professionali
proposti in sei analisi, copertura aziendale finale18/19/19. Due HTTP nuovi
scrivono quattro/zero testi in base a conferme/rinvii, non prova di compilazione
completa. Labirinto undici testi in entrambe.43 checkpoint42/43, limite noto
export-no.87 chiamate/8 analisi,934.320 token.2146 backend finali,1440 mutazioni
fuzz più boundary HTTP; tutti i fallimenti conservati. Nessun push/migrazione.

## Integrazione Minervino: diagnosi offline, 16 ottobre 2026

[Report](../minervino-integrazione-2026-10-16.md),
[misure](2026-10-16-minervino-integrazione.json),
[bundle](2026-10-16-minervino-integrazione-audit.tar.gz) e
[checksum](2026-10-16-minervino-integrazione-audit.tar.gz.sha256).

Prova dell'utente del 15 ottobre, analisi 211598d4: cinque chunk dell'integrazione
nei 56 inviati, 27 proposte e 21 grounded; 22 valori scritti inclusa una risposta
USER. Omissioni dei soci, mancato uso dell'anagrafica dopo la scelta del firmatario,
quattro rifiuti di attribuzione personale, due di ancoraggio FORM e gruppo checkbox
respinto. Pool 3→1→0. Input/audit ricostruiti identici; testo Word uguale ai valori
del report e altre 15 parti ZIP preservate. Nessuna nuova API, modifica al motore
o sessione live; nessun gold completo, percentuale di accuratezza o rendering visuale.

## Revisione del gold Minervino, 16 ottobre 2026

[Report](../minervino-gold-review-2026-10-16.md),
[confronto di 52 occorrenze](2026-10-16-minervino-gold-review.json),
[bundle](2026-10-16-minervino-gold-review-audit.tar.gz) e
[checksum](2026-10-16-minervino-gold-review-audit.tar.gz.sha256).

Candidato dell'utente, non congelato. Valori anagrafici/societari e dei soci
coerenti con KB; tre paragrafi del direttore cancellati, con otto destinazioni
da ripristinare. Sei X e tre checkbox native true coerenti; scelte della pratica
da formalizzare come USER. Nessuna nuova analisi LLM, modifica al gold o KB,
validazione formale degli identificativi o revisione visuale dell'impaginazione.

## Word gold Minervino revisione 1, 16 ottobre 2026

[Word](<../../nuovi dati/domanda-iscrizione.GOLD-SINTETICO-REVISIONE-1.docx>),
[scenario](<../../nuovi dati/SCENARIO_GOLD_MINERVINO.md>),
[controlli](2026-10-16-minervino-gold-revision-1.json),
[backup](2026-10-16-minervino-gold-revision-1-audit.tar.gz) e
[checksum](2026-10-16-minervino-gold-revision-1-audit.tar.gz.sha256).

Ripristinati direttore ed etichette originali, conservati dati e scelte
dell'utente. 60 occorrenze testuali verificate, tabelle e controlli invariati;
solo document.xml modificato. Nessun writer applicativo, LLM o aggiornamento
KB. Non congelato: controllo visuale e OK dell'utente ancora attesi.

## Verifica del verdetto Minervino, 16 ottobre 2026

[Report](../minervino-verifica-verdetto-2026-10-16.md),
[controlli](2026-10-16-minervino-verdetto.json),
[ultima pagina MuPDF](2026-10-16-minervino-verdetto-last-page-mupdf.png),
[bundle](2026-10-16-minervino-verdetto-audit.tar.gz) e
[checksum](2026-10-16-minervino-verdetto-audit.tar.gz.sha256).

Numerazione alfabetica originale preservata nell'XML, assegnazioni già nello
scenario, due spiegazioni nelle aree compilabili confermate. Firma isolata
a pagina 10 non verificata: MuPDF produce 15 pagine e mantiene dicitura e linea
insieme nell'ultima; non certifica la paginazione Word. Word e scenario invariati,
nessun congelamento o nuova prova LLM. Checkpoint e annotazioni ancora da completare.

## Base Minervino V1 congelata, 16 ottobre 2026

[Fixture](../../demo-documents/benchmark-minervino/v1/README.md),
[rapporto](../minervino-base-v1-2026-10-16.md),
[misure](2026-10-16-minervino-freeze.json),
[bundle](2026-10-16-minervino-freeze-audit.tar.gz) e
[checksum](2026-10-16-minervino-freeze-audit.tar.gz.sha256).

Congelamento autorizzato dall'utente con tag/push. Word finale ricostruito
dall'originale, note fuori dai campi e firma unita; scenario e copione separati
dalla KB. 267 destinazioni annotate, 60 testi SOURCE e quattro USER, 123 vuoti,
sei X e tre checkbox true. Controlli indipendenti passati e nove pagine PDF
LibreOffice ispezionate; numerazione alfabetica confermata. MuPDF reimpagina
e separa la firma: limite conservato nei raw, non riferimento di layout.
Nessuna nuova prova LLM, istanza integrata, modifica al motore o KB live.
Tag: baseline-minervino-v1-20261016; Labirinto V1 invariato.

## Preflight dell'input B0, 16 ottobre 2026

[Report](../b0-preflight-2026-10-16.md),
[misure](2026-10-16-b0-preflight.json),
[bundle](2026-10-16-b0-preflight-audit.tar.gz) e
[checksum](2026-10-16-b0-preflight-audit.tar.gz.sha256).

Input attuale ricostruito offline: 240.276 caratteri JSON, 24.675 system,
cinque fonti/56 chunk e 267 destinazioni. Materiali backend corrispondenti
alla fixture. Analisi globale DeepSeek forza thinking anche con preferenza
progetto disattivata; prima ipotesi corretta e conservata nei raw. Zero
chiamate provider: nessuna misura di token, qualità, dialogo o generazione Word.
