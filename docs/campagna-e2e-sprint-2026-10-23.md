# Campagna E2E dopo lo sprint (23 ottobre 2026)

**Esito preregistrato: favorevole.**
- 6/6 tentativi eseguiti e 6 DOCX;
- 139 scritture riviste, 0 non dimostrate;
- 0 aggiramenti di sospensioni o revisioni;
- 0 scritture e 0 proposte nelle 25 destinazioni storiche della rev 2;
- 2.559.649 token su un tetto di 2.900.000.

È una verifica esplorativa, non una certificazione:
- la revisione delle scritture è **autoriale (Claude) e non indipendente**;
- un 6/6 non dimostra una superiorità generale sulla monolitica.

La candidata non è adottata, l'app live è invariata, la baseline V12 non è toccata e non c'è stato
alcun push.

**Riferimenti:**
- **Preregistrazione con addendum:** `PREREG-SPRINT-E2E.md`, congelata alle 17:27:05 UTC prima della
  prima chiamata.
- **Casi storici:** `CONTROESEMPI-REV2-25.json`.
- **Grezzo:** `backend/data/compilation-audit/sprint-e2e-20261023-01/`, con
  `e2e/EVENTI-CAMPAGNA.md` e `HARNESS-FREEZE.json`.
- **Risultati:** `benchmark ufficiale/sprint-e2e-20261023-01/`:
  - `ANALISI-SEZIONI.json`, `RIEPILOGO-SEZIONI.json`;
  - `REVISIONE-AUTORIALE.json`, `MISURE-SPRINT.json`;
  - `CONFRONTO.json`.

## Candidata e controlli prima delle inferenze

**Codice congelato:**
- **Commit:** `a9bd928`.
- **Digest del codice:** `ed349787…`, 130 file.
- **Digest dei prompt:** `9ae0e014…`.
- **Verifica:** il server osservato controlla gli hash a ogni chiamata.

**Profilo, 9 flag:**
- V14 e K3;
- stato derivato;
- dialogo P3;
- `generation_revision 3`;
- recupero del narratore;
- R1 (`branch_scope_revision 1`);
- revisione mirata delle sospensioni (`hold_rereview_revision 1`).

**Correzione ordinaria della bozza esplicita:** è su un branch separato
(`fix/2026-10-23-bozza-esplicita`, `c7c3492`) e **non** è inclusa. La candidata chiude la stessa
lacuna per la rev 3 con il proprio codice.

**Controlli:**
- suite 3.740 PASS e Ruff PASS sul codice congelato;
- corpora identici alle SOURCE congelate;
- richieste di segmento attese con prompt, istruzioni e partizione identici alla candidata
  precedente;
- preflight superato.

**Interruzione:** il PC si è riavviato prima della prima chiamata. Le verifiche sono state rifatte
(codice uguale al manifest, runtime e corpora integri) e la campagna è partita solo dopo il nuovo
congelamento. Nessuna chiamata era avvenuta prima.

## Risultati per tentativo

| Tentativo | DOCX | Scritture (gemello) | Non dimostrate | Copertura (gemello) | Token | Tempo | Retry |
|---|---|---|---|---|---|---|---|
| soresa2023-1 | sì | 3 (8) | 0 | 13% (47%) | 123.634 | 138 s | 0 |
| minervino-1 | sì | 46 (56) | 0 | 77% (93%) | 570.965 | 290 s | 0 |
| catanzaro-1 | sì | 19 (22) | 0 | 35% (45%) | 579.709 | 244 s | 0 |
| soresa2023-2 | sì | 7 (8) | 0 | 47% (47%) | 135.756 | 206 s | 0 |
| minervino-2 | sì | 51 (30) | 0 | 85% (50%) | 529.558 | 318 s | 0 |
| catanzaro-2 | sì | 13 (18) | 0 | 42% (32%) | 620.027 | 209 s | 0 |

**Totali:**
- **Costo:** circa 0,38 USD (candidata precedente circa 0,40).
- **Tempo:** 1.406 s, contro 1.570 della candidata precedente.

**Criteri preregistrati, tutti soddisfatti:**
- **(a)** 0 scritture non dimostrate o con applicabilità errata;
- **(b)** 0 aggiramenti;
- **(c)** nessuna di queste violazioni:
  - scrittura SOURCE in destinazioni non verificate;
  - scrittura in regioni d'opzione senza autorizzazione;
  - risposta 409;
- **(d)** 6/6 DOCX.

Nessun arresto.

## Misure richieste

**Errori nei rami:** nessuna ricomparsa. 0 scritture e 0 proposte valide nelle 25 destinazioni
storiche (Minervino `p37.*`, Catanzaro `t19.*`, So.Re.Sa. `p127.*`/`p43`/`p44`), come nella
candidata precedente (rev 2: 25 scritte).

**R1:** esercitato nei due tentativi Minervino, con 7 condizioni estese ciascuno:
- **Rami non applicabili** (studio associato, RTP, consorzio): condizioni rimaste aperte (SKIP o
  UNKNOWN); nessuna destinazione scritta.
- **Ramo società:** condizione confermata con ricevuta d'ambito; destinazioni scritte.
- **Falsi rifiuti dovuti a R1:** nessuno.

**I 21 campi dei soci di Minervino:**
- **minervino-2: 21/21 scritti e dimostrati.** Non per effetto della revisione mirata: in questo
  tentativo il narratore non li ha sospesi. Le sospensioni marcate M sono 0 in tutti i tentativi:
  **il meccanismo non è stato esercitato**.
- **minervino-1: 15/21.** 6 campi (Elisa Romano e Andrea Greco come soci) sono sospesi con blocco
  `source` («la fonte non attesta il ruolo di socio»), citando proprio la riga della tabella dei
  soci: sospensioni non fondate, ma escluse per costruzione dalla revisione mirata, che tocca solo
  l'applicabilità.

**Nuovi falsi rifiuti rispetto ai gemelli** (destinazioni scritte e dimostrate là, non qui): 33 su
142, nessuno dovuto alle modifiche dello sprint (R1, revisione mirata, rivalidazione finale).

| Causa | N | Dove |
|---|---|---|
| Proposta non fatta o respinta dal validatore (variabilità del modello) | 19 | minervino-1 7, catanzaro-1 2, soresa2023-2 1, catanzaro-2 9 (8 caselle della tipologia, nessuna scelta USER in quel tentativo) |
| Sospensione del narratore | 14 | soresa2023-1 5, minervino-1 6, catanzaro-1 3 |

**Nuove scritture corrette rispetto ai gemelli:** 30, di cui 21 in minervino-2.

**Sospensioni del narratore non fondate, fuori dal criterio M:**
- **soresa2023-1:** chiede di nuovo la partecipazione singola, già confermata.
- **catanzaro-1:** cita la tipologia, già scelta dall'USER.
- **minervino-1:** il ruolo di socio è contraddetto dalla citazione.

Le prime due hanno la citazione «ancorata» solo perché il controllo esistente considera l'intera
finestra di revisione, non la singola proposta; la terza ha blocco `source`.

**Sospensioni plausibilmente fondate:** minervino-2, direttore tecnico («il ruolo aziendale non
equivale a una designazione») e data del ruolo del firmatario.

**Retry e riprese:**
- 0 retry (candidata precedente: 2), 0 segmenti falliti, 0 errori del narratore;
- nessuna interruzione durante i tentativi: la ripresa in E2E non è stata esercitata;
- la rivalidazione finale non ha rifiutato nulla, perché le esportazioni sono passate dalla chat.

**Comportamento sicuro osservato:** catanzaro-2 ha chiesto conferma di un firmatario sbagliato
(«Luca Ferri»). L'USER ha risposto di no e il campo non è stato scritto.

## Differenze rispetto alla candidata precedente (6/6)

| | Sprint | Candidata corretta |
|---|---|---|
| DOCX | 6/6 | 6/6 |
| Scritture / non dimostrate | 139 / 0 | 142 / 0 |
| Rami sbagliati (25 destinazioni) | 0 | 0 |
| Copertura mediana Minervino / Catanzaro / So.Re.Sa. | 81% / 39% / 30% | 72% / 39% / 47% |
| Token totali | 2,56 M | 2,57 M |
| Tempo totale | 1.406 s | 1.570 s |
| Retry | 0 | 2 |

**Interpretazione:**
- Le differenze di copertura sono dominate dalla variabilità del modello e del narratore (stessi
  scenari, giorni diversi, n = 2 per modulo), non da un effetto misurato delle correzioni.
- Rispetto alla monolitica della valutazione finale la candidata resta più costosa, in mediane per
  modulo:
  - token 1,4 volte (So.Re.Sa.), 2,6 volte (Minervino), 4,2 volte (Catanzaro);
  - tempo circa 1,4-1,7 volte.

## Obiettivi dello sprint

1. **Rami: raggiunto, con il limite dichiarato.**
   - Offline, R1 chiude 7 dei 25 controesempi in modo deterministico, senza falsi rifiuti.
   - In E2E: 0 scritture nei rami sbagliati e nessuna perdita dovuta a R1.
   - Le altre 18 restano protette solo dal comportamento del modello con il FORM completo.
2. **Narratore: non dimostrato in E2E.**
   - La revisione mirata è verificata offline (21/21 sul caso registrato) ma non è stata esercitata
     (0 casi M).
   - Il recupero dei 21 campi in minervino-2 è dovuto al modello.
   - Emergono altre sospensioni non fondate fuori dal criterio, 14 campi: citazione ancorata solo
     alla finestra, o blocco `source`.
3. **Ripresa: raggiunto offline,** con 10 scenari deterministici. Non esercitata in E2E (nessuna
   interruzione). Nessun aggiramento di autorizzazioni o revisioni.
4. **Monolitica e app ordinaria: raggiunto.**
   - Codice base e sprint identici su 79 stati salvati.
   - App live invariata.
   - La correzione di sicurezza del profilo ordinario è separata e verificata.

## Limiti

- Revisione autoriale non indipendente; un solo modello; SOURCE sintetiche; n = 6.
- Lo zero nei rami sbagliati è osservato, non garantito per 18 dei 25 casi.
- La revisione mirata delle sospensioni e la ripresa non sono state messe alla prova dal vivo.
