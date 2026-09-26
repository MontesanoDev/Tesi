# Trapani Green: prima compilazione reale

23 settembre 2026. Una sola esecuzione completa, nessun rilancio per scegliere
un risultato favorevole e nessuna modifica del compilatore per questo modulo.

## Condizioni

- Modulo DOCX originale, avviso e disciplinare ufficiali nella cartella del caso.
- Scheda `generalita-mapi.md` simulata, senza altre fonti globali.
- Indicazioni fissate prima della chiamata in [istruzioni.txt](istruzioni.txt).
- Pipeline corrente `docx-fields-v11-compact-json`; modello restituito `deepseek-flash`.
- Ingestion, compilazione e download attraverso le API FastAPI in un database temporaneo.
- Audit conserva hash del codice e degli input, prompt, risposte e metadati.

Non sono stati estratti prima i facts. La mappa usata sotto per controllare il
risultato non e' stata fornita al modello e non viene letta dal codice di produzione.

## Esito tecnico

| Misura | Risultato |
| --- | ---: |
| Posizioni candidate | 115: 54 celle e 61 segnaposti |
| Posizioni classificate | 115 |
| Scritture effettive | 12 |
| `missing` | 35 |
| `needs_review` | 10 |
| `not_applicable` | 58 |
| Elementi non classificati | 0 |
| Chiamate AI | 4 |
| Correzioni / troncamenti | 0 / 0 |
| Frammenti inviati / disponibili | 55 / 55 |
| Token complessivi dichiarati | 146.609 |
| Durata della richiesta di compilazione | 32,91 secondi |

DOCX e report prodotti e scaricati senza errori API. Questi numeri non sono
misure di accuratezza del modello: i conteggi includono campi non applicabili.

## Controllo del contenuto

Nove inserimenti sono coerenti con il perimetro didattico scelto e con le fonti:

- `p12.s0`: Luca Ferri nel nominativo del sottoscrittore.
- `p75.s0`: Mapi Ingegneria S.r.l. nel ramo societa' di ingegneria.
- `p75.s1`: Via Giovanni Amendola 172/C.
- `p75.s2`: Bari.
- `p75.s3`: 70126.
- `p75.s4`: BA.
- `p75.s5`: IT01234567890, riportato come identificativo fittizio della fonte,
  non certificato come partita IVA formalmente valida.
- `p75.s6`: +39 080 000 2040.
- `p75.s8`: mapi.ingegneria@pec.demo.

Tre scritture sono fuori dal perimetro richiesto:

| Campo | Valore | Problema |
| --- | --- | --- |
| `t0.r1.c0` | Ing. Luca Ferri | Inserito nella tabella dei professionisti associati, pur avendo escluso quel ramo. |
| `t5.r1.c0` | COMUNE DI TRAPANI | Inserito tra le amministrazioni committenti di servizi pregressi. Il bando corrente non prova un incarico precedente svolto da Mapi. |
| `p107.s0` | mapi.ingegneria@pec.demo | Recapito aziendale corretto, ma inserito nella dichiarazione sul canale delle comunicazioni, oltre il perimetro limitato all'anagrafica iniziale e al ramo societario. Non e' un indirizzo inventato. |

Il report contiene anche un avviso che afferma che la tabella riepilogativa non
e' stata compilata, contraddetto dalla scrittura in `t5.r1.c0`. Le motivazioni
del modello non sostituiscono il controllo del Word e di `written_value`.

Nascita, CF personale, residenza, fax, luogo/data, firma e CIG sono rimasti vuoti.
Non sono stati scritti altri contratti o importi pregressi. Il numero d'albo del
direttore tecnico non e' stato trasferito al sottoscrittore.

## Integrita' verificata e limiti

Controllata la corrispondenza tra le 12 scritture del report e il DOCX, la
presenza dell'avviso di bozza, l'invarianza dei paragrafi non modificati e delle
parti ZIP diverse da `word/document.xml`. Gli originali scaricati restano invariati.

**Non verificata la resa visiva in Word, OnlyOffice o LibreOffice.** Non e'
disponibile un renderer Office in questo ambiente. I dati sono simulati e non
provano requisiti del 2023; le opzioni prestampate non sono state cancellate.
Il documento richiede revisione, non e' pronto per firma o invio.

## File della prova, solo locali

- [Word prodotto](../../../backend/data/docx-demo/20260923-trapani-v11-prima-prova/bozza.docx)
- [Report JSON](../../../backend/data/docx-demo/20260923-trapani-v11-prima-prova/report.json)
- [Riepilogo tecnico](../../../backend/data/docx-demo/20260923-trapani-v11-prima-prova/result.json)

I file si trovano in `backend/data/`, gia' esclusa da Git. Gli originali e le
istruzioni del caso sono invece nella cartella demo. Un clone del repository
non contiene l'esecuzione live: il comando nel README permette di ripeterla.

Nell'app locale e' stato creato **Trapani Green - Progettazione e sicurezza**
(`trapani-green-progettazione-e-sicurezza`), con avviso e disciplinare indicizzati:
28 + 17 frammenti. Non sono stati modificati gli altri due progetti o la KB globale.
La prova isolata non e' importata nello storico delle compilazioni dell'app,
per non associare i suoi ID temporanei a fonti diverse del database reale.

Una nuova compilazione dalla UI utilizza anche le fonti globali presenti
nell'applicazione, quindi non replica necessariamente questo contesto isolato.
Per la demo aprire Template, caricare il DOCX e usare le indicazioni del caso.

**Conclusione:** il terzo caso e' utilizzabile per esercitare il flusso, ma
conferma il limite sull'applicabilita' delle sezioni e sull'attribuzione del
soggetto. Un terzo documento non costituisce ancora un benchmark rappresentativo.
