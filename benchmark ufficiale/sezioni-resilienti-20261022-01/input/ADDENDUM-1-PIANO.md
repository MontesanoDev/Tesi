# Addendum 1 al piano — scostamenti emersi dalle verifiche offline (22 ottobre 2026)

Il piano `PIANO-SEZIONI-RESILIENTI.md` resta congelato (sha256 nel file `.sha256`). Questo addendum
registra, prima di qualunque inferenza reale, le modifiche fatte dopo il congelamento. Sono tutte
dentro le funzioni dell'elenco chiuso (sezione 1) e nascono da test offline, misure sui cataloghi
reali o difetti trovati. Nessuna modifica a parser, writer, retrieval, narratore, V14 o K3.

## Difetti corretti (trovati dai test T3/T8 e dalle misure)

1. **Ordine di documento.** `dependency_units` ordinava le candidate per chiave del catalogo, che è
   lessicografica (`p1`, `p10`, `p100`…), non per posizione. Le sezioni risultavano non contigue e
   il taglio sulle intestazioni non funzionava. Ora l'ordine è (blocco, paragrafo, offset).
2. **Clausola della regione d'opzione nel contesto.** Il paragrafo della clausola V14 («☐ per le
   società…») non è fra i paragrafi d'ancoraggio delle celle della tabella che governa: il segmento
   proprietario non lo riceveva. Ora il contesto include, per ogni destinazione:
   - il paragrafo della sua regione d'opzione;
   - i paragrafi su cui il validatore estende lo scope delle condizioni (`_condition_bindings`,
     sovrainsieme degli ancoraggi);
   - il paragrafo d'avvio di una continuazione (`continuation_origin_paragraph_id`).

   Misura sui 7 moduli della valutazione finale: 0 destinazioni con paragrafi di clausola fuori
   contesto (`out/segment-sizes-*.json`, controllo in `outside.py` della sessione).
3. **Vista pubblica.** Le destinazioni non analizzate erano state unite al veto di applicabilità
   FORM di `review_fields`, che nella vista pubblica bloccava anche i valori USER. Ora sono un
   motivo separato: niente scrittura SOURCE, nessun verdetto FORM, valore USER ammesso.

## Riduzione delle duplicazioni (punto F), misurata prima delle inferenze

4. **Prefisso cacheabile.** `reading_plan.source_property_lines` (16 205 caratteri su Catanzaro,
   uguali per tutti i segmenti) seguiva le `units` variabili e restava fuori dal prefisso comune.
   `segment_input` mette ora prima le parti invarianti del piano. Prefisso comune: da circa
   68 600 a circa 85 000 caratteri.
5. **Sezioni minuscole.** Un pacchetto con meno di target/4 posizioni si unisce al precedente se
   l'unione resta entro il target (unità intere, ordine invariato). Effetti:
   - Catanzaro: da 7 a 6 segmenti (eliminato un segmento da 2 posizioni, circa 27 000 token di
     input);
   - So.Re.Sa.: da 3 a 2 segmenti.

## Completamenti coerenti con il piano

6. **Riferimenti espliciti degli input.** Ogni voce di cache e ogni segmento del report registrano
   gli hash di SOURCE, contesto USER, valori USER e FORM del segmento, oltre a versione del contratto
   e data di riferimento. Il digest della richiesta resta la chiave di riuso (I9).
7. **Stati di applicabilità solo per le scritture.** `applicability_states` valuta solo proposte
   grounded, riusi SOURCE e valori USER. Una proposta REJECTED non è una scrittura e non riceve uno
   stato.
8. **Paragrafi incerti.** La sezione 4 elenca i paragrafi locali dichiarati incerti fra le cause
   di CONDIZIONATA.
   - Verifica: il validatore V12 rifiuta già la proposta del modello sotto un inventario locale
     incerto.
   - Non la rifiuta invece per un riuso SOURCE aggiunto dopo la validazione.
   - Nel rev 2 queste destinazioni sono quindi escluse dall'export SOURCE e dal veto finale
     (`unverified_fields`). Il valore USER resta ammesso.
   - Impatto misurato sulle 35 prove della valutazione finale: nessuna prova usa
     `uncertain_paragraph_ids`.

## Esito diverso dal criterio scritto (T5), dichiarato

9. **Condizione riconoscibile omessa dal record del campo.**
   - Il criterio prevedeva «CONDIZIONATA, non esportata».
   - Il comportamento reale del validatore V12 invariato è più severo: la condizione viene
     collegata al campo, ma un valore incondizionato (`disposition: value`) con condizione ignota
     viene **rifiutato** («Condizione sconosciuta: applicabilità da chiarire»).
   - Non esportato in entrambi i casi. Il test documenta il comportamento reale.
