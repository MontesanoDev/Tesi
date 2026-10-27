# Integrazione delle checkbox testuali — 26–27 ottobre 2026

## Risultato e perimetro

L'app ordinaria usa automaticamente la compilazione per sezioni con profilo
`sezioni-2026-10-25`, tutte le protezioni FORM del 25 ottobre e, per le **nuove**
sessioni, `text_checkbox_revision=1`. Le vecchie sessioni conservano i flag e il
catalogo originari; nessuna migrazione. Il DOCX rimane una bozza da revisionare.

Il supporto riguarda un solo marcatore ASCII iniziale `[]`, `[ ]`, `[x]`, `[X]`
seguito da testo, in paragrafi semplici del corpo o di celle. Il gruppo FORM,
l'applicabilità e la scelta USER verificata autorizzano la selezione `[X]`;
SOURCE da sola non basta. Caselle non selezionate restano vuote. Simboli,
contenuti complessi, marcatori ambigui e controlli nativi seguono i percorsi
precedenti: non è un supporto universale alle checkbox Word.

Il port di `55fcd0e` esclude deliberatamente la sua aggiunta al prompt.
`compilation_global.py`, narratore, retrieval e segmentazione sono identici alla
base pubblicata. Nessun selettore UI. Conservato anche il recente fix UI che
mostra il recupero messaggio solo dopo errori.

## Git e working tree

Base: `aaaaa44b58af5996d017bec1d91a3d1dcf408247`, già pubblicata e contenente
l'adozione `a152d7f`. Branch: `integrazione/2026-10-26-checkbox-testuali`.
I commit locali `1785357` e `55fcd0e` **non sono antenati** del branch pubblico:
sono state applicate selettivamente le sole modifiche di codice/test necessarie.
Gli snapshot privati rimangono nei rispettivi rami e backup locali.

| Commit | Scopo |
|---|---|
| [`e47b817`](https://github.com/MontesanoDev/Tesi/commit/e47b817538868092cbb89c4e52973cca93ca8c3d) | Port del fix UI già ordinario; solo due file frontend |
| [`f5f6bd5`](https://github.com/MontesanoDev/Tesi/commit/f5f6bd52fd5a0f32a900591d208717524bdcbab5) | Supporto checkbox, validatori e test; nessun cambio al prompt |
| [`59a2dcd`](https://github.com/MontesanoDev/Tesi/commit/59a2dcd110b3d9838f5a640dd1bb4a6adc23fadf) | Attivazione nel profilo ordinario e compatibilità delle sessioni |
| commit documentale successivo | README, STATUS, relazioni e questo rapporto |

Il working tree ordinario resta su `prune-backend` con il lavoro preesistente
non committato. Applicata soltanto la patch backend, dopo confronto con la base
attesa. Tutti i **376 file runtime tracciati** coincidono con `59a2dcd` (incluso
il frontend già corretto). Non è stato fatto un commit indiscriminato del
working tree e non sono stati ripuliti worktree.

## Verifiche eseguite

| Verifica | Esito |
|---|---|
| Backend prima, working tree ordinario | **3940 PASS**, nessun fallimento preesistente rilevato |
| Backend integrato, worktree isolato con runtime poi confrontato byte per byte | **3989 PASS**, nessuno SKIP |
| Ruff finale | PASS |
| Checkbox e profilo ordinario | **70 PASS**, compresi export FTS5/Qdrant, rinvio, altro slot, condizione falsa/ignota, veto selezione esplicita |
| Frontend | **154 PASS**, lint e build PASS |
| Rollback della sola attivazione | **130 PASS**, profilo precedente con controlli FORM preservati |
| Rollback completo e selettivo del fix | **177 PASS**, albero esattamente `e47b817` |
| Prova API preparatoria e nel processo reale | **4 PASS** in ciascuna, database temporanei, trasporti del modello simulati |
| DOCX/PDF | `[X]` e `[]` verificati in XML/testo PDF e visivamente |

Le suite includono V14, K3, R1, istruzioni FORM, veto API e percorsi monolitici e
segmentati. Non sono state ripetute sull'ordinario dopo il port: è stato
verificato che tutti i file runtime siano esattamente quelli della suite,
poi esercitato l'export nel processo ordinario reale.

Incidenti degli strumenti, distinti da regressioni: due test intenzionalmente
fallenti prima dell'attivazione; due rilievi Ruff corretti; prima esecuzione del
probe con percorso Python errato (caricava il backend precedente), poi corretta;
LibreOffice con librerie in ordine errato terminava prima di aprire il DOCX,
risolto anteponendo le librerie del suo `program`. Tutti i log sono conservati.

## Replay FORM

Rigioco senza inferenze delle risposte storiche, con le stesse fonti e giudizi.

| Misura | Base precedente | Catalogo con caselle testuali |
|---|---:|---:|
| Errori storici ammessi, ricevute registrate | 0/25 | **0/25** |
| Errori ammessi, guardia d'ambito SUPPORTED simulata | 0/25 | **0/25** |
| Positivi congelati con guardia simulata | 243/245 | **243/245** |
| Positivi estesi con guardia simulata | 236/240 | **236/240** |
| Positivi congelati con sole vecchie ricevute | 211/245 | 197/245 |
| Positivi estesi con sole vecchie ricevute | 236/240 | 226/240 |

Il lato base è il replay precedente conservato; il lato integrato è stato
rieseguito qui. Le vecchie ricevute non sono trasferibili automaticamente a un
catalogo ampliato: è precisamente il motivo per non aggiornare le sessioni
precedenti. I due casi controversi nel corpus da 245 restano aperti.
Questi dati non misurano come il modello risponderà nelle nuove compilazioni.

## Prova del processo effettivamente avviato

Avvio tramite `./start.sh`. Frontend 5173, backend 8000 e proxy `/api/health`
rispondono HTTP 200. Un hook locale temporaneo, escluso da Git e senza nuove
route, ha eseguito quattro prove attraverso le API ASGI **nel worker reale**,
prima dell'apertura al traffico. PID e hash dei moduli caricati sono registrati.

Le prove creano nuove sessioni esclusivamente in database temporanei, verificano
il profilo ordinario e scaricano DOCX effettivamente prodotti dall'export.
Scelta USER autorizzata: `[X]`; rinvio ed export esplicito della bozza vuota:
`[]`. L'ID forzato senza decisione riceve 409/422. Sono esercitati FTS5 e Qdrant,
con interpretazioni del modello e della risposta USER simulate. Il blocco
locale della rete ha registrato **zero tentativi di connessione esterna**.

I DOCX scaricati dal worker sono stati convertiti con LibreOffice locale:
marcatori presenti e visibili nei PDF. Nessuna prova con Microsoft Word desktop;
nessuna nuova chiamata LLM o campagna E2E. Un riavvio normale con `./start.sh`
non necessita dell'hook diagnostico o di variabili sperimentali.

## Integrità e limite preesistente del riavvio

Verificati sullo stato attuale: **29 sessioni, 474 revisioni, 200 turni, 273 file
uploads e 290 file storage complessivi**. Stati, originali, versioni e profili
delle sessioni e tutti i file risultano identici. Documenti e benchmark storici
non sono stati modificati. SQLite integrity_check OK, nessuna violazione FK.

Il file SQLite non è identico byte per byte dopo l'avvio. È stata identificata
una routine preesistente (`seed_markdown_artifacts` → `_replace_chunks`) che
rigenera 82 frammenti di quattro artefatti Markdown a ogni avvio, cambiandone ID
e timestamp senza cambiare contenuto. Il fenomeno è stato riprodotto sul codice
precedente in una copia isolata: non è una regressione delle checkbox.

Per non lasciare cambiati gli identificatori storici, è stato provato su copia
e poi applicato un ripristino transazionale dei soli 82 ID/timestamp e del
contatore correlato, mediante UPDATE, senza cancellare righe né riscrivere
contenuti. Tutte le tabelle logiche, incluso il contenuto FTS, sono confrontate
col backup; nel confronto le credenziali vengono oscurate in memoria allo stesso
modo. Le sole differenze residue sono nei quattro contenitori fisici FTS
`*_data` / `*_idx`. Lo schema è identico. La routine di avvio resta invariata:
un prossimo riavvio può rigenerare nuovamente gli ID degli artefatti. Non è stata
aperta una modifica del retrieval o del sistema di inizializzazione.

## Backup e pubblicazione

Verificati manifest e hash dello snapshot precedente; creato backup incrementale
aggiornato in `/home/montesano/tesi-backups/integrazione-checkbox-20261026-01/`,
con seconda copia verificata in `D:\Backup-tesi-2026-10-23\integrazione-checkbox-20261026-01\`.
Database copiato coerentemente e oscurato, storage archiviato e verificato,
delta del workspace rispetto allo snapshot precedente. Le chiavi devono essere
reinserite se si ripristina il database oscurato.

La base pubblica è stata scandita lungo la cronologia raggiungibile: 4301
oggetti, 2809 blob, 61 archivi; nessuna corrispondenza ai pattern di credenziali,
nessun database o file di chiavi trovato. Si aggiunge il controllo dei nuovi
commit: soltanto codice, test e documentazione. La scansione a pattern non è una
certificazione universale di riservatezza. Nessun nuovo backup, database,
DOCX/PDF di prova o audit grezzo entra nei commit. I benchmark già pubblicati
non vengono riscritti. Push normale del solo branch, nessun merge in main,
nessuna modifica di tag o force push. Pubblicazione completata e SHA remoto
confrontato con HEAD; `main` remoto invariato. Esito conservato in
`publication-verified.json`. [Branch pubblicato](https://github.com/MontesanoDev/Tesi/tree/integrazione/2026-10-26-checkbox-testuali).

## Rollback verificato

Sul branch di integrazione, per disattivare soltanto nelle **nuove** sessioni:

```bash
git revert 59a2dcd
```

Mantiene il supporto necessario a leggere/esportare le sessioni già create con
le nuove caselle. Nessuna modifica di dipendenze, database o DOCX salvati.

Per togliere anche il codice del fix, preservando sezioni, FORM e correzione UI:

```bash
git revert 59a2dcd f5f6bd5
```

Verificato in worktree isolato con `--no-commit`: albero identico a `e47b817`.
Le sessioni con caselle testuali restano conservate; senza il relativo codice
potrebbero non essere riesportabili. Perciò il rollback della sola attivazione
è preferibile. I DOCX già salvati restano disponibili.

Nel working tree ordinario, a servizi arrestati, non usare reset o checkout:

```bash
# Solo attivazione; poi riavviare con ./start.sh
git apply --reverse --check backend/data/compilation-audit/integrazione-checkbox-20261026-01/adozione-default.patch
git apply --reverse backend/data/compilation-audit/integrazione-checkbox-20261026-01/adozione-default.patch
```

In alternativa, **in luogo** della patch precedente, rollback completo:

```bash
git apply --reverse --check backend/data/compilation-audit/integrazione-checkbox-20261026-01/integrazione-backend.patch
git apply --reverse backend/data/compilation-audit/integrazione-checkbox-20261026-01/integrazione-backend.patch
```

Entrambe le prove a secco passano sul codice adottato; le inverse sono state
esercitate nel worktree di rollback. Nessun ripristino dei dati richiesto.

## Evidenze e limiti finali

Grezzi in `backend/data/compilation-audit/integrazione-checkbox-20261026-01/`:
log delle suite e dei replay, inventari prima/dopo, prova di processo,
`runtime-render/`, riproduzione dell'avvio, rollback e controllo pubblicazione.
Revisione autoriale, non indipendente. Nessuna misura nuova di copertura o
qualità del modello; l'autorizzazione semantica reale resta un limite. Nessun
altro sprint o esperimento avviato.
