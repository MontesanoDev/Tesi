# Preregistrazione — valutazione finale del candidato (22 ottobre 2026)

Scritta e congelata prima di qualunque inferenza della valutazione. Applica senza modifiche i
**criteri di conclusione v1** (`docs/criteri-conclusione-2026-10-21.md`, SHA256 `f3ec66be…`,
congelati il 21 ottobre alle 19:27:10 UTC): soglie e denominatori invariati. Durante le prove non
si modificano codice, prompt, configurazioni o criteri; non si introducono correzioni.

## 1. Profilo candidato

- V14 (autorizzazione delle clausole d'opzione) + K3 (organizzazione nell'attestazione di ruolo);
- dialogo P3 corretto, attivato **esplicitamente** nel runtime sperimentale
  (`MAPI_DIALOGUE_REVISION=1`);
- generazione monolitica; generazione per sezioni disattivata (`MAPI_GENERATION_REVISION` assente);
- modello e parametri del runtime seme V12 (deepseek-flash, ragionamento basso, limite 49.152 per la
  chiamata globale, 2.048 per il narratore).

L'app live ordinaria non cambia (profilo V14 + K3, dialogo P3 spento). La baseline ufficiale V12
resta congelata. Codice applicativo: hash di `backend/app` e `frontend/src` nel protocollo
(`PROTOCOLLO-FINALE.json`); il server di osservazione blocca ogni chiamata se cambiano.
Riproducibilità del profilo verificata prima delle prove (`out/profilo-riproducibilita.json`):
flag delle sessioni nuove, richieste globali identiche costruite due volte e identiche a quelle
della verifica del narratore per i quattro moduli in comune.

## 2. Moduli

| Modulo | Tipo | Posizioni | SOURCE | Variante USER | Denominatore del nucleo |
|---|---|---:|---|---|---:|
| Minervino | storico | 267 | storica | minervino-controllo | 60 |
| Cesano | storico | 88 | storica | cesano-esteso | 4 |
| CRAA | storico | 51 | storica | craa-ramo | 8 (2 CCIAA fuori: autorizzazione rinviata) |
| Catanzaro | storico | 307 | storica | catanzaro-controllo | 31 |
| Bella | storico | 67 | storica | generico | 8 |
| Trapani | storico | 115 | storica | generico | 17 |
| So.Re.Sa. 2023 | **nuovo** | 81 | **nuova (scheda tabellare PDF)** | generico | 15 |

- Storici: tutti i sei moduli con scenario e riferimento congelati (nessuna selezione dei migliori).
- Nuovo: estrazione con seme fisso dal pool congelato dei bandi casuali
  (`out/estrazione-modulo-nuovo.json`). Sono esclusi i moduli già studiati e i due modelli per
  professionista singolo, incompatibili con lo scenario societario fisso. Ordine estratto:
  cannara, soresa2023, calabria.
  **Cannara è fuori ambito** per la condizione 4: 0 su 27 destinazioni del nucleo sono riconosciute
  (`input/riferimenti-v3/cannara-fuori-ambito.json`), quindi non conta come fallimento. So.Re.Sa.,
  il successivo, è compatibile.
- Compatibilità (criteri, condizioni 1-4) prima di ogni inferenza: `out/compatibilita-1-3.json` e la
  condizione 4 nei riferimenti v3. Tutti i sette moduli valutati sono compatibili.
- Varianti: coerenti con lo scenario base. Le attestazioni restano non decise (CRAA: la
  dichiarazione CCIAA viene rinviata), la partecipazione è decisa (Cesano: autorizzazione della
  partecipazione). `generico` è un alias, identico per comportamento a `minervino-controllo`.

## 3. SOURCE

- **Storica:** 22 frammenti (due Markdown aziendali, una visura PDF, un TXT generale), identica a
  quella delle campagne precedenti. Runtime `storico`.
- **Nuova** (requisito di generalizzazione): `scheda-dati-operatore-mapi.pdf`, una scheda
  tabellare DOCX convertita in PDF con LibreOffice locale.
  - Consolida senza aggiunte né correzioni i fatti del corpus aziendale storico; i 104 valori sono
    letterali nel testo estratto.
  - È stata costruita **prima** dell'estrazione del modulo nuovo.
  - Runtime `nuova-source`: i tre documenti aziendali globali sono sostituiti dalla scheda e il
    TXT generale resta (14 frammenti).
- Limite dichiarato: per So.Re.Sa. modulo nuovo e SOURCE nuova coincidono, quindi gli effetti
  non sono separabili.

## 4. Tentativi

- 5 tentativi indipendenti per modulo, 35 in totale. Ogni tentativo ha un progetto isolato nuovo,
  una sessione nuova, una sola chiamata globale e un export richiesto dal percorso ordinario della
  UI con download.
- Ordine per turni (turno r: tutti i moduli), al massimo 4 contesti browser in parallelo.
- Nessuna sostituzione, ripetizione o selezione: tutti i tentativi contano, falliti compresi.
- Limiti per tentativo: 60 chiamate, 4 turni di risposta (politica USER deterministica congelata,
  `input/user_policy_finale.cjs`), un export, 1000 s per messaggio UI.
- Budget complessivo: 6 milioni di token, con blocco automatico. Un tentativo non eseguito per
  budget conta come fallito e viene dichiarato.

## 5. Riferimenti di valutazione (v3)

`input/riferimenti-v3/*.json`, conformi ai criteri. Per ogni destinazione del nucleo:
`fact_available`, `branch_condition` (con base), `declaration_authorization` (regioni d'opzione V14
più lo stato nella variante) ed `expected_if_authorized`.

- **Storici:** derivati meccanicamente dai riferimenti congelati v1/v2, con valori invariati
  (hash di origine registrati).
- **So.Re.Sa.:** nucleo autoriale scritto prima di ogni inferenza.
- **Denominatore:** destinazioni riconosciute con fatto disponibile, ramo vero e autorizzazione non
  richiesta oppure concessa nello scenario.
- **Equivalenze ammesse:** maiuscole e spazi, prefisso di titolo, date equivalenti (`gg/mm/aaaa` e
  mese in lettere), valori in `accepted_values`.
  - Contenimento come nelle campagne precedenti, riportato a parte come «corrispondenza parziale».
  - Per `match = all_of` servono tutte le parti.

## 6. Misure e classificazioni

1. **Affidabilità dell'export:** DOCX prodotto e scaricato dalla UI / tentativi, per modulo e sul
   totale.
2. **Copertura del nucleo**, per tentativo esportato: scritture corrette nel denominatore /
   denominatore; mediana per modulo sui DOCX esportati. I valori errati non contano.
3. **Scritture non dimostrate.** Ogni valore scritto e distinto viene giudicato su prova del
   valore, soggetto, applicabilità e autorizzazione procedurale.
   - Primo passaggio automatico: valori uguali o equivalenti al riferimento → dimostrati.
   - Tutte le altre scritte, comprese caselle e scritture fuori riferimento, passano alla revisione
     documentale su FORM, SOURCE e scenario.
4. **Condizioni e decisioni USER:** ricevute registrate e azioni; caselle attese da scelte USER
   (`USER_decisions_expected`) scritte o no; scritture in regioni d'opzione senza autorizzazione
   accettata (attese 0); CCIAA di CRAA vuote.
5. **Dialogo:** conferme ridondanti, cioè richieste di riconfermare una decisione USER già
   acquisita in modo univoco. Si misurano dalle trascrizioni e dalle regole della politica, con
   controllo sulle ricevute già registrate. Le richieste di autorizzazione delle dichiarazioni sono
   lecite e conteggiate a parte. Si contano anche domande identiche ripetute e interventi della
   guardia sui cicli.
6. **Vuoti:** per ogni destinazione pertinente (nel denominatore o fra i campi attivi irrisolti del
   riferimento) rimasta vuota nel DOCX, si verifica che esista un motivo tracciato nell'audit
   (copertura con stato e motivo, proposta respinta, sospensione, condizione o risposta, gate
   procedurale o di completezza) o nel report di export. Si riporta la percentuale con motivo.
7. **Visibilità:** ogni valore presente nel DOCX ma non visibile nel PDF reso con il renderer V12
   congelato genera un warning, non un giudizio di correttezza.
8. **Token, costo, latenza:** usage del provider per chiamata; costo stimato con
   `pricing.json` (tariffa di punta o fuori punta secondo l'ora UTC); tempo per tentativo e per
   chiamata globale.
9. **Classi di fallimento**, tenute separate:
   - **MODEL:** la chiamata globale tronca, restituisce JSON non valido, errore del provider o
     timeout;
   - **NARRATORE:** sintesi respinta, in errore o in timeout;
   - **BACKEND:** validazione o gate in errore, risposta 4xx/5xx, sessione FAILED per cause non
     del modello;
   - **EXPORT:** export rifiutato, DOCX non valido, download mancante;
   - **DRIVER:** timeout dell'interfaccia senza causa nei livelli precedenti.

## 7. Revisione

**Una revisione indipendente non è disponibile.** Nessun revisore esterno allo sviluppo è stato
designato e chi esegue la valutazione ha sviluppato il sistema.

- La revisione delle scritture è **autoriale**, affiancata dal confronto automatico con i
  riferimenti v3. Non viene presentata come indipendente.
- Il criterio di sicurezza («zero scritture non dimostrate nella revisione indipendente») è quindi
  riportato come **non verificabile nella forma richiesta**, insieme all'esito autoriale.
- Per una revisione futura si prepara un pacchetto cieco: per ogni scritta FORM, contesto, SOURCE e
  scenario, senza valori attesi.

## 8. Giudizio

- Si applicano le soglie v1 per modulo e sul totale; i benchmark storici e il modulo nuovo sono
  riportati separatamente.
- Le percentuali non sono accuratezza universale.
- Il confronto con le campagne precedenti (V12, V13, V14, P3, narratore) è prudente: scenari,
  varianti e denominatori v3 possono differire e vengono dichiarati.
- Nessuna adozione automatica, nessun commit o push.
