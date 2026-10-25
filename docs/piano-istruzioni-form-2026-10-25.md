# Piano: istruzioni condizionali del FORM e schede governate (25 ottobre 2026)

Preregistrato prima di modificare il codice. Lavoro autorizzato dall'utente («opzione A»)
sui sei controesempi residui dopo `ddb8cb7`. Zero inferenze, nessuna modifica all'app
ordinaria, nessun push. Revisione autoriale (Claude), non indipendente.

## Casi

Sei scritture storiche della rev 2, tutte So.Re.Sa.:
- **soresa2023-1:** `p44.s0`, `p44.s1`;
- **soresa2023-2:** `p43.s8`, `p43.s9`, `p44.s0`, `p44.s1`.

Sono dati veri dell'impresa singola scritti nelle schede dei componenti di un RT non
costituito. In 4 casi il modello non ha indicato alcuna condizione, quindi passano anche con
le sole ricevute registrate.

Il paragrafo 19, in grassetto, dice «(da compilare nel caso di partecipazione in forma di RT,
Consorzio Ordinario o GEIE non ancora costituito)» e governa quattro schede ripetute fino al
titolo «CHIEDE/CHIEDONO» (paragrafo 64). Tra le schede ci sono separatori «***» e note in
grassetto tra parentesi.

## Regola

**Istruzione condizionale:** un paragrafo del corpo (non in tabella) che:
- non ha destinazioni né controlli;
- è interamente in grassetto;
- dopo la normalizzazione, eventualmente tra parentesi, inizia con «da compilare in caso di »
  o «da compilare nel caso di » seguito da testo.

I marcatori sono gli stessi già usati da `compilation_table_scope`; il prefisso ammesso
(numerazione o parentesi) è lo stesso.

**Ambito:** i paragrafi del corpo successivi, fino al primo di questi eventi, escluso:
- una tabella;
- un'altra istruzione condizionale;
- un paragrafo in grassetto senza destinazioni né controlli che non inizia con «(».

Sono governate soltanto le destinazioni di tipo testo dei paragrafi nell'ambito. Nessun nome
di bando, ruolo o tipo societario nella regola.

**Condizione valida:**
- la sua citazione FORM è ancorata al paragrafo dell'istruzione;
- è uguale all'istruzione intera dopo normalizzazione, togliendo le parentesi esterne e la
  punteggiatura finale;
- non ha errori di validazione.

Una citazione parziale non basta.

**Effetti:** stesso meccanismo della revisione 1 (`compilation_form_option_scope`).
- La condizione è propagata alle destinazioni governate.
- Senza condizione valida lo stato è NON_ACCERTATA, con motivo leggibile.
- Con condizione valida servono una ricevuta USER positiva, valida per lo stesso ambito e
  attuale, e un risultato non falso.
- Il veto vale per SOURCE e USER ed è ricostruito dall'originale anche all'export.
- Il backend non inventa condizioni e non genera domande per quelle omesse.

**Attivazione:** `form_option_scope_revision = 2`, che comprende la revisione 1 invariata.
- Variabile `MAPI_FORM_OPTION_SCOPE_REVISION=2`, profilo `sezioni-istruzioni-2026-10-25`.
- Il predefinito `sezioni-2026-10-24`, la revisione 1 e le sessioni esistenti non cambiano.

## Inventario strutturale, eseguito prima del codice

Prototipo `ambiti-istruzioni-20261025-01/prototipo_regola.py` sui 7 moduli dei benchmark,
cataloghi ricostruiti dagli originali con il codice attuale:
- **So.Re.Sa.:**
  - paragrafo 7, partecipazione singola o RT già costituito: 12 destinazioni di testo, fino
    all'istruzione del paragrafo 19;
  - paragrafo 19, RT non costituito: 48 destinazioni, fino al paragrafo 64.
- **Cesano, CRAA, Minervino, Catanzaro, Bella, Trapani:** nessuna istruzione nel corpo.

**Citazioni del modello negli stati So.Re.Sa.** delle campagne rev 2, rev 3 corretta, sprint
e incrementale:
- paragrafo 19: intere 11/11;
- paragrafo 7: intere 6/8;
- nei paragrafi governati dal 7 non c'è alcuna proposta fondata.

## Criteri di accettazione

1. **Rigioco congelato** (rev 2 e rev 3 corretta, come `ambiti-form-20261025-01`):
   - errori esportabili da 6 a 0 con guardia simulata e da 4 a 0 con le ricevute registrate;
   - corrette 245/245 (simulate) e 211/245 (registrate), invariate;
   - 0 nuovi falsi rifiuti.

   Un risultato diverso si riporta così com'è.
2. **Positive estese**, separate dal confronto congelato: rigioco anche delle campagne sprint e
   incrementale, senza nuovi falsi rifiuti rispetto alla revisione 1.
3. **Revisione 1 identica:** 38 test esistenti PASS e rigioco della revisione 1 invariato.
4. **K3:** 26 casi avversari identici alla base.
5. **Test sintetici nuovi:**
   - riconoscimento e confini (tabella, nuova istruzione, titolo, nota tra parentesi);
   - esclusioni: non grassetto, con campi, senza marcatore;
   - campo governato senza condizione, con condizione intera e conferma, con conferma
     negativa, con citazione parziale e con condizione su un altro paragrafo;
   - campo dopo il titolo non governato;
   - export API 409/200;
   - profilo persistito.
6. **Suite completa e Ruff.**
7. **Rollback** con `git revert` in un worktree isolato, con albero identico al commit di
   partenza.
8. **Invarianti:** sessioni live e file preservati identici prima e dopo.

## Arresto e limiti dichiarati

**Arresto:** se il criterio 1 o il 2 perde scritture corrette, non si rilassa la regola in
silenzio; si documenta e si chiede.

**Rischi noti:**
- una citazione parziale (2 casi su 8 per il paragrafo 7) lascerebbe vuoti campi legittimi:
  rischio di omissione, non di scrittura errata;
- la regola dipende da grassetto e marcatore letterale, quindi altre formulazioni restano
  scoperte;
- le caselle native in quegli ambiti non sono governate da questa regola.

Nessuna nuova misura di qualità LLM.

## Emendamento dopo l'arresto (decisione dell'utente, 25 ottobre 2026)

Il rigioco della regola preregistrata ha perso 7 scritture corrette: arresto e diagnosi in
`ambiti-istruzioni-20261025-01/out/NOTA-ARRESTO.md`. L'utente ha scelto la variante **A2**,
misurata offline prima della decisione.

**Regola della citazione A2**, solo per le istruzioni. Una condizione copre l'istruzione se è
ancorata al suo paragrafo e la citazione normalizzata:
- coincide con l'istruzione intera, oppure
- è un suo prefisso che contiene il marcatore, arriva almeno al primo «ovvero», «,» o «;»
  successivo al marcatore e termina a un confine di parola.

Le citazioni di parti interne o troppo corte restano insufficienti. La revisione 1 delle
opzioni non cambia.

**I 2 casi `p31.s0`:** «Leonardo Montemurro» da una risposta USER, scritto nella scheda del
secondo componente RT. Sono considerati blocchi corretti, con giudizio autoriale non
indipendente. Il giudizio storico DIMOSTRATA resta invariato nei benchmark congelati e la
discrepanza è dichiarata nel rapporto.

**Accettazione:**
- il codice deve riprodurre i numeri misurati per A2: congelato 0/0 errori, 243/245 corrette;
  esteso 236/240;
- restano validi gli altri criteri del piano.
