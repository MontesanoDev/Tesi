# V12: conflitti tipografici, decisioni USER ed export parziale

18 ottobre 2026. Intervento circoscritto ai residui richiesti. Le precedenti
correzioni delle revisioni e delle citazioni non sono state rifatte.

**Tutti i 42 valori precedentemente scritti sono conservati, con lo stesso
contenuto e nelle stesse posizioni. Il DOCX è identico anche come file.**
Nessuna nuova scrittura indebita osservata, nessuna casella selezionata.
I miglioramenti riguardano due falsi conflitti e la disponibilità delle domande
sulle decisioni della pratica; non un aumento artificiale dei campi compilati.

[Misure](benchmarks/2026-10-18-v12-residui.json),
[controlli](benchmarks/2026-10-18-v12-residui-checks.json),
[Word parziale](../nuovi%20dati/domanda-iscrizione.V12-RESIDUI-20261018.docx),
[report di export](../nuovi%20dati/domanda-iscrizione.V12-RESIDUI-20261018.report.json),
[cinque domande complete](../nuovi%20dati/domanda-iscrizione.V12-RESIDUI-20261018.domande.md).

## Confronto osservato

Stessa risposta globale della precedente UI V12: 55 fatti, 60 assegnazioni,
stesso FORM B0 e medesime 56 SOURCE. Nessuna nuova chiamata LLM. Le ricevute
USER della sessione originale rimangono immutate.

| Misura | Prima, replay del codice conservato | Dopo, medesime ricevute USER |
|---|---:|---:|
| Assegnazioni SOURCE proposte | 60 | 60 |
| Proposte grounded | 44 | 46 |
| Proposte revisionate nel replay | 44 | 46 |
| Grounded con applicabilità ancora UNKNOWN | 3 | 4 |
| Proposte SOURCE applicabili | 41 | 42 |
| SOURCE effettivamente scritte | 41 | 41 |
| Valori USER scritti | 1 | 1 |
| Totale fisicamente scritto | 42 | 42 |
| Valori precedenti persi/modificati | — | 0 |
| Nuove scritture indebite osservate | — | 0 |
| Soci nel DOCX | 24 | 24 |
| Nuove spunte | 0 | 0 |
| Decisioni residue disponibili nel pool | 0 | 5 |

Il valore USER della qualifica resta USER nel replay storico: non si riscrive
retroattivamente la sua provenienza. La proposta SOURCE ora valida per la stessa
destinazione non sostituisce quella ricevuta.

Un secondo replay parte dallo snapshot reale **precedente alla risposta sulla
qualifica**, conservando le due ricevute già registrate: società confermata e
direttore tecnico rinviato. Produce gli stessi 42 valori, questa volta
**42 SOURCE e zero valori USER**, con tutti i 24 campi dei soci da SOURCE.
Non richiede la scelta fra «Ingegnere» e «ingegnere». Non è un benchmark senza
USER: la conferma di partecipazione e il rinvio del direttore restano presenti.

Le quattro proposte grounded UNKNOWN dopo la correzione sono `p51.s0`,
`p52.s0`, `p53.s0`, `p53.s1`. La quarta è la qualifica prima bloccata dal falso
conflitto. Nessuna diventa applicabile grazie alla sola equivalenza tipografica.
Le altre 14 assegnazioni non grounded restano tali: due REJECTED e dodici
REVIEW_REQUIRED con errori; non sono state recuperate aggirando i controlli.

## Equivalenza dei valori, senza unione delle persone

In `compilation_global.py` il rilevamento delle alternative usa una chiave
separata per il valore: Unicode NFC, spazi non significativi normalizzati e
minuscole. L'identità proposta resta verificata su soggetto, entità, dimensione
e proprietà con le regole preesistenti. Non si modifica il confronto dei nomi,
non si uniscono record e non si trasferiscono ruoli o poteri.

Il valore originale e le citazioni restano intatti. Per Elisa:

- `p45.s1` conserva «Ingegnere», citato nella riga dei soci, chunk `-54`;
- `p52.s0` conserva «ingegnere», citato nel record del direttore, chunk `-55`.

Il binding di ciascuna destinazione viene comunque verificato separatamente.
L'applicabilità del direttore è ancora UNKNOWN e il suo rinvio USER è conservato.

Abbreviazioni, numeri, punteggiatura e accenti non vengono equiparati. Si usa
`lower()`, non l'espansione di `casefold()`: anche «Straße» e «Strasse» restano
distinti. Una proposta esplicitamente REVIEW contenente soltanto alternative
tipograficamente equivalenti viene respinta come lista ridondante, senza una
falsa domanda di scelta; non viene promossa automaticamente a VALUE perché
quel record non ha selezionato un fatto. Fatti e citazioni restano nell'audit.

## Informazioni che richiedono davvero una decisione USER

Il nuovo helper `compilation_user_decisions.py` riconosce soltanto istruzioni
esplicite nel catalogo FORM esistente. Non modifica il catalogo inviato al modello
e non trasforma `coverage.manual_input` o `source_not_found` in autorizzazioni.
Le affermazioni del modello sull'assenza delle fonti non bastano a creare domande.

| Decisione | Richiesta concreta | Destinazioni considerate |
|---|---|---|
| Preferenze | Categorie, servizi e fasce scelti per questa domanda, rispettando l'istruzione «max. 6 tipologie» | 67 celle delle quattro tabelle, una sola domanda |
| Dichiarazioni e attestazioni | Quali dichiarazioni elencate nel modulo l'utente conferma espressamente | `p217.cb0`, mostrando anche tutte le clausole successive fino alla casella seguente |
| Esecutori | Chi viene designato per l'esecuzione dell'eventuale incarico | `p228.cb0`, `p229.s0`, `p230.s0` |
| Integrazione | Chi viene designato per integrare le prestazioni specialistiche | `p232.s0`, `p233.s0`, `p234.s0`, una sola domanda |
| Luogo e data | Quali luogo e data indicare sulla domanda | `p242.s0` |

Le 67 celle sono **opzioni**, non 67 informazioni obbligatorie mancanti. Il GOLD
congelato ne seleziona sei dopo le risposte del copione, che qui non sono state
somministrate. Le tre righe dell'integrazione sono spazio per una decisione,
non tre professionisti da inventare. Il GOLD usa solo la prima di quelle righe.

Le domande conservano i riferimenti FORM e il testo completo pertinente.
L'attestazione non viene abbreviata in un assenso generico. Per le preferenze,
titoli e fasce sono mostrati una volta per tabella, evitando la ripetizione di
67 domande. La voce sulle reti di telecomunicazioni, ripetuta nell'originale,
rimane distinta: nessuna fusione arbitraria di righe.

Il pool esclude i campi con proposta SOURCE, i valori già acquisiti, le domande
già attive e le decisioni già risposte o rinviate. UNKNOWN/FALSE non vengono
promosse a TRUE. Il nome della decisione è legato a template, destinazioni e
prove FORM: risolvere una singola cella non crea una nuova domanda duplicata.
Solo V12 usa questa agenda; nessun aggiornamento implicito delle vecchie sessioni.

Il narratore può scegliere fino a tre domande per turno. Se restituisce una
lista vuota mentre esistono decisioni esplicite disponibili, il backend propone
fino a tre di quelle domande; le rimanenti restano nel pool. Il testo delle
decisioni viene conservato dal backend, senza reimpiegarlo come prova SOURCE.

**Limite deliberato:** una risposta raggruppata registra una ricevuta letterale
USER con `write_authorized=false` e, per VALUE, verifica della destinazione
ancora pendente. Non crea `user_values`, condizioni vere, fatti SOURCE,
choice group o spunte. Non è stato introdotto un nuovo interprete delle scelte
né un meccanismo per distribuire liberamente i nomi nei campi. La conferma delle
singole destinazioni resta necessaria prima di scriverle; questo intervento
rende disponibili le domande, non completa automaticamente quella fase futura.

## Cosa non va chiesto di nuovo e cosa resta incompleto

La scelta di partecipare soltanto come società di ingegneria è già registrata;
non viene chiesta di nuovo come se la KB non attestasse la natura societaria.
La natura giuridica dell'operatore, la modalità di partecipazione e i poteri
del firmatario rimangono informazioni distinte. La condizione sul direttore è
stata rinviata: non si chiede ripetutamente la stessa conferma e non si deduce
una nuova nomina dal ruolo aziendale.

La sezione del giovane professionista appartiene al ramo RTP del modulo, che
non è il ramo scelto in questa sessione. Non si richiede un nome per riempirla
e non si imposta automaticamente alcuna sua condizione come FALSE.
La firma digitale non è una domanda di dato testuale e non viene inserita.

Restano **18 campi SOURCE attesi ma non scritti**, invariati rispetto al Word
precedente:

- Nove del firmatario: `p12.s0`–`p12.s3`, `p13.s0`–`p13.s3`, `p14.s0`.
  Sono nome, nascita, residenza, CF e carica; le proposte hanno binding respinto.
  La scelta nominativa presente nel contesto/condizione non attiva qui la
  ricevuta VALUE del nome per il riuso locale. Non sono nuovi dati da chiedere
  all'utente come se fossero assenti dalla KB; il difetto resta fuori intervento.
- Comune iniziale `p15.s0`: citazione FORM composta dal solo marker, respinta.
  Non è un'assenza di Bari nella SOURCE; BA iniziale e Bari/BA societari restano
  scritti. Nessuna modifica ai controlli già corretti.
- Otto del direttore: `p51.s0`, `p52.s0`, `p52.s1`, `p53.s0`–`p53.s4`.
  Quattro sono grounded ma rinviati/UNKNOWN; il CF ha citazione FORM invalida;
  provincia, data e numero d'iscrizione conservano i tre rifiuti di attribuzione
  SOURCE. Una conferma USER non li validerebbe automaticamente tutti.

Restano inoltre quattro testi USER previsti dal GOLD: esecutori sulle due righe,
integrazione sulla prima riga, luogo/data. Le altre righe non vanno riempite
soltanto perché disponibili. Preferenze e due caselle su attestazioni/esecutori
attendono decisioni reali mai fornite. La casella societaria, invece, ha già una
decisione pertinente ma manca ancora il gruppo di scelta validato nell'output:
è un limite tecnico distinto da una risposta USER mancante. Rimane non spuntata.

Le note FORM sulle dichiarazioni personali dei soggetti societari e sugli
allegati restano una verifica separata. Non si attribuisce a ogni socio un
potere di rappresentanza, né si presume che una conferma generale produca le
dichiarazioni personali o gli allegati richiesti. La bozza non è pronta all'invio.

## Export parziale e consenso

L'offerta di bozza parziale compare anche mentre ci sono domande aperte.
UNKNOWN, SKIP e REFUSE registrano soltanto il rinvio della decisione, senza
negare condizioni o modificare campi già acquisiti. Un comando esplicito di
generazione/termine può esportare i valori sicuri senza prima rispondere a tutto.

Se non esistono valori esportabili, il dialogo chiarisce che verrà generata una
copia senza valori e conserva `empty_export_offered`. Solo dopo quell'avviso,
oppure nella preesistente domanda di generazione, l'export vuoto è consentito.
Restano il consenso esplicito, il gate READY, l'arresto sugli errori e tutti i
controlli SOURCE/USER. Un comando generico davanti a un vecchio checkpoint con
zero dati e senza quell'avviso non forza una copia vuota.

`PRESENTATION_VERSION=3` aggiorna il dialogo su nuove sintesi o ripresa esplicita;
nessuna migrazione dei dati. Il writer e il report di export esistenti sono riusati.

## Verifiche e limiti della misura

45 nuovi casi generici, incluse prove negative su differenze reali, proprietà e
soggetti distinti, citazioni inesistenti, alternative ridondanti, condizioni false,
decisioni duplicate, campo già risolto, ricevute UNKNOWN/SKIP/REFUSE, tentativi di
usare decisioni come applicabilità/scelta e generazione con domande ancora aperte.
Percorsi API/persistenza su FTS5 e Qdrant, con trasporti simulati.

**221 test mirati passati in 29,69s; suite completa finale 2524 passati in 181,97s;
Ruff passato.** La prima suite completa aveva individuato una regressione
sull'export vuoto; corretta con l'avviso tracciato, mantenendo il test precedente.
Nessuna aspettativa di sicurezza preesistente è stata rimossa o rilassata.

La prima acquisizione red aveva anche un errore nel contesto della fixture
generica; corretta la fixture, la riproduzione sul codice originale conservato
restituisce 33 fail/12 pass. I fallimenti, le verifiche intermedie e il primo
errore di import dello script di verifica del bundle sono tutti conservati.
Non sono tentativi di ottenere una risposta migliore dal provider.

Replay su copie separate di DB/storage, socket e HTTP vietati. Baseline ottenuta
eseguendo le preimmagini dei moduli solo nel processo di replay. Persistenza,
rivalidazione SOURCE e generazione DOCX reali; trasporto del narratore simulato
senza hold aggiuntivi. Le revisioni già valide sono conservate e le due nuove
proposte vengono riesaminate. Non è una nuova misura di qualità del narratore,
una nuova prova UI o una promessa sul comportamento di una futura chiamata reale.

XML, CRC ZIP, posizioni, contenuti e report confrontati. Quattro tabelle e
tredici controlli nativi intatti. FORM/template e DOCX precedenti rispettivamente:

```text
FORM SHA256 25ab2b0655b696fb8ccb4218ae10f5b5450da38279675b136e323ed7c282344c
DOCX SHA256 4a29f7d306a6664b88208f8ba88bff5738123310a84853ff4e770f69dae126c8
```

Il controllo indipendente `verify_bundle.py` ricostruisce audit e DOCX dal bundle
senza DB privato, chiavi o provider e ottiene lo stesso hash. Nessuna nuova
renderizzazione PDF: il file Word è byte per byte identico a quello già esaminato.
Zero token e zero costo provider aggiuntivo; tempi delle future compilazioni non
misurati. L'eliminazione del chiarimento non necessario non dimostra un tempo
globale più breve. I cinque nuovi argomenti possono richiedere ulteriori turni.

## Conservazione e punto di arresto

Raw: `backend/data/compilation-audit/v12-residui-20261018-01/`.
Confronti definitivi in `baseline/`, `corrected-verified/`,
`pre-qualification-verified/`; le iterazioni precedenti restano distinte.

Backup pubblicabile:
[bundle](benchmarks/2026-10-18-v12-residui-audit.tar.gz),
[checksum](benchmarks/2026-10-18-v12-residui-audit.tar.gz.sha256),
[descrittore](benchmarks/2026-10-18-v12-residui-archive.json).
Include input/prompt/schema/output originali, stati/ricevute, preimmagini,
script, log dei test, DOCX/report e verifiche; esclude DB e chiavi privati.

FORM B0, modello, thinking, prompt globale, contratti API/DB, catalogo e writer
invariati. Le funzioni dei binding SOURCE e i validatori dei valori non sono
stati modificati. Restano le precedenti modifiche locali, comprese le eliminazioni
dell'utente. Nessun commit/push, nuovo framework o esperimento E1. Sessioni e
storage originali verificati nei controlli collegati. Arresto dopo replay e rapporto.
