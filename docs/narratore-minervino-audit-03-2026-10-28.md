# Audit E2E del narratore su Minervino — tentativo 03 (28 ottobre 2026)

**Esito: compilazione completata senza guasti, DOCX scaricato, 0 valori scritti.**
- **DOCX:** è l'originale con il solo banner «BOZZA NON VERIFICATA».
- **Analisi:** ha proposto 56 dei 58 valori del replay offline, tutti uguali.
- **Dove si perdono:** nel dialogo e nelle conferme.
- **Revisione:** autoriale, non indipendente. Un solo tentativo, nessuna ripetizione.

## Ambiente

- **Codice:**
  - compilatore `7b31d25`;
  - harness `89d1e2e` più `d508b64`, che legge dal config il limite di 3.000.000 invece del
    default di 900.000.
- **Isolamento:** runtime nuovo da seed; porte 18080 e 15173.
- **Budget:** riserva di 800.000; controllo offline del budget superato
  (`COMPATIBILITA-BUDGET.json`).
- **Input:** FORM, SOURCE, catalogo, profilo e policy USER con gli hash preregistrati.
  - Protocollo: cambiano solo i percorsi.
  - Driver: cambia solo la costante `BUDGET`.
- **Integrità dopo la prova:** 164/164 file congelati invariati; grezzi del 02 invariati.
- **Grezzi privati:** `backend/data/compilation-audit/narratore-minervino-20261028-03/`.
- **Backup verificato:** `/home/montesano/tesi-backups/narratore-minervino-20261028-03/`, senza
  credenziali.

## Cronologia (UTC)

| Turno | Ora | Domande poste dal narratore | Risposta USER (policy) | Ricevute | Token | Durata |
|---|---|---|---|---|---:|---:|
| T0 | 20:41:41 | 1. ramo «legale rappresentante di società»; 2. «dell'operatore economico»; 3. categorie e fasce | — | — | 378.024 | 217 s (analisi) |
| R1 | 20:45:20 | 1. dichiarazioni e attestazioni; 2. professionisti esecutori; 3. professionista integratore | 1 = testo «date» (regola `dates`), 2 e 3 = rinvio | 3 SKIP | 58.365 | 9 s |
| R2 | 20:45:29 | luogo e data | 3 rinvii | 3 SKIP | 21.178 | 4 s |
| R3 | 20:45:34 | nessuna; offre una copia senza valori | rinvio | 1 SKIP | 18.108 | 3 s |
| Export | 20:45:39 | — | richiesta di bozza parziale | — | 6.657 | 2 s |

**Comportamento del dialogo:**
- 7 domande, nessuna ripetuta;
- nessuna ricevuta persa;
- 0 sospensioni del narratore;
- nessun HTTP ≥ 400 e nessun `generation_status=failed`.

**Chiamate:** 16, per 482.332 token (0 ignoti), circa 0,054 USD in stima.

| Chiamate | Token |
|---|---:|
| Segmenti | 363.490 (75%) |
| Guardia (una chiamata) | 36.693 |
| Narratore (4 chiamate) | 47.628 |
| Routing | 33.729 |

**Concorrenza:** i segmenti 2-4 sono andati in parallelo, con attesa di budget nulla.

## Campi documentati rimasti vuoti (58 del replay)

| Causa | Campi |
|---|---:|
| Ramo «società» (`s2_c_soc`): chiesto, ma la policy ha risposto con il testo sulle date (gli `field_ids` contengono le date dei professionisti, e la regola `dates` precede `corporate`) | 28 |
| Ramo «operatore economico» (`s1_c_op`): chiesto, ma la policy rinvia gli slot `applicability`, che non riconosce | 9 |
| Sottoscrittore (nome, nascita, residenza, codice fiscale, carica): binding di ruolo respinto («Ruolo richiesto assente nell'estratto FORM»); condizione `s1_c_firmatario` mai chiesta | 7 |
| Direttore tecnico: binding respinto («Ruolo attestato assente nell'estratto SOURCE»); condizione `s2_c_dt` mai chiesta | 6 |
| Respinti dal validatore: province (solo marker) e nomi dei soci (fatto SOURCE rifiutato) | 6 |
| Non proposti: sezione del direttore tecnico e checkbox del ramo società | 2 |

**Valori proposti per i campi sorvegliati, tutti corretti:**
- **nome e carica del sottoscrittore:** corretti, ma non scrivibili e mai chiesti;
- **date di iscrizione:** attribuite al professionista della stessa riga SOURCE;
- **checkbox del ramo società:** non proposta.

## Problemi principali (dettaglio nel rapporto all'utente)

1. **Nome e ruolo del sottoscrittore:** la convalida di ruolo blocca il sottoscrittore e la
   domanda non viene mai posta.
2. **Policy USER congelata incompatibile con gli slot reali** (`applicability`, `decision`).
3. **Messaggio del narratore sostituito:** la sintesi iniziale, informativa, è stata sostituita
   da un testo generico dal filtro anti-assenza (parole come «non», «nessun»).
