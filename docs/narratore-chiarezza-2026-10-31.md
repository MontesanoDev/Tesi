# Chiarezza di domande e riepiloghi del narratore (31 ottobre 2026)

Commit `de2f5de` sul branch `narratore-chiarezza/2026-10-31`, dalla versione demo R2
(`ca58972`, codice `demo-default-r2-20261031`). La demo congelata e l'app ordinaria non sono state toccate.
Nessuna chiamata DeepSeek, nessun push o merge.

## Correzioni (solo presentazione)

| Formulazione reale | Ora |
|---|---|
| «Confermi che si applica al vostro caso quanto indicato nel modulo: «Il sottoscritto , nato a il , residente»» e «Confermato: Il sottoscritto , nato a il , residente.» | Una riga FORM da compilare, riconosciuta dai suoi spazi vuoti, è una parte da compilare: «Confermi che la parte del modulo «Il sottoscritto …, nato a … il …, residente» va compilata (riguarda: …)?»; «Confermato: la parte del modulo «…».» |
| «(riguarda: Carica documentata, Operatore economico, …)» | «Carica di Leonardo Montemurro: amministratore unico e rappresentante legale», solo negli elenchi mostrati; nelle verifiche «Carica di Leonardo Montemurro «…»» |
| «(riguarda: A, B, C, D, E, F e altri 43)» | «(riguarda: 49 dati del modulo, tra cui A, B, C, D, E e F)»; nelle estensioni «(8 dati, tra cui …)»; negli avvisi della bozza «(tra cui A, B, C)» |
| «Confermato: La manifestazione … (riguarda: Denominazione dell'operatore economico, Comune sede lega.» | Il riepilogo nomina l'enunciato confermato senza ripetere l'elenco, e taglia sempre a parola intera con «…» |
| Due «Chi designi per questo incarico?» di fila | «Chi designi come professionisti esecutori?» e «Chi designi come professionista incaricato dell'integrazione?» |

**Non cambiati:**
- condizioni, ricevute e prove d'ambito;
- il marcatore «(riguarda:», da cui dipende `destinations_shown` letto dalla guardia;
- autorizzazioni, guardia, validatori, compilazione DOCX;
- le chiavi delle decisioni, che derivano solo dal materiale FORM;
- l'etichetta dell'audit «Carica documentata», perché entra nel digest d'ambito: cambiarla
  invaliderebbe le ricevute;
- il testo salvato nelle risposte (`confirmed_text`);
- `PRESENTATION_VERSION`, perché incrementarla farebbe rinarrare le sessioni alla ripresa.

Una domanda che il backend prima non sapeva formulare (marcatori tecnici) resta non formulata.

## Verifiche

- **Test nuovi:** 6 in `test_narrator_clarity.py`, sui casi reali.
  - Sul codice della demo falliscono (helper assente). Dopo la modifica passano.
  - Coprono anche: un solo elenco per domanda, `destinations_shown` invariato, chiavi delle
    designazioni distinte, nessuna nuova domanda per clausole con marcatori.
- **Test esistente aggiornato:** `test_signatory_order_and_extension.py` attendeva la vecchia
  formulazione della domanda di estensione su «Il sottoscritto ____, nato a». L'invariante
  resta: la domanda nomina la clausola confermata.
- **Suite e Ruff:** su `de2f5de`, 4.290 passati e 8 saltati; Ruff PASS.
- **Rollback:** albero uguale al genitore; test nuovo in errore sul revert; versione del
  genitore del test modificato: 4 passati.
- **Replay offline sulle trascrizioni reali:**
  - 90 run delle campagne `omissioni-20261030` e `strutturale-20261030`, con artefatti del
    narratore registrati;
  - domande e riepiloghi rigenerati col codice della demo e col nuovo;
  - fedeltà: 110 domande del backend e 193 riepiloghi riprodotti esattamente dal codice
    della demo;
  - 11 riepiloghi esclusi perché il contesto salvato non contiene la clausola dello slot, o la
    sintesi era degradata.

  | Difetto | Prima | Dopo |
  |---|---|---|
  | «e altri N» nelle domande | 114 | 0 |
  | «Carica documentata» nelle domande | 22 | 0 |
  | Designazioni con domanda identica (run) | 20 | 0 |
  | Riga FORM chiesta come condizione | 2 | 0 |
  | Elenco «riguarda» ripetuto nel riepilogo | 55 | 0 |
  | Riepilogo tagliato a metà parola | 27 | 0 |
  | Riga FORM nel riepilogo | 1 | 0 |

Script e risultati: `backend/data/compilation-audit/narratore-chiarezza-20261031/` (esclusa da
Git).

## Da segnalare, non fatto perché cambierebbe la logica

- **La condizione su «Il sottoscritto, nato a» esiste** perché il modello ancora l'identità del
  firmatario alla riga anagrafica. Ora è detta in modo leggibile. Sostituirla con la scelta del
  firmatario, o non crearla, è logica delle condizioni.
- **Le risposte date prima di questa modifica** conservano il testo salvato senza spazi
  («Il sottoscritto , nato a il , residente»), che riappare nel loro riepilogo. Correggerlo
  richiederebbe modificare le ricevute.
- **La guardia legge il testo delle domande.** Le nuove formulazioni mantengono gli stessi
  contenuti e marcatori, ma il loro effetto sul verdetto del modello reale non è verificabile
  senza chiamate DeepSeek.
