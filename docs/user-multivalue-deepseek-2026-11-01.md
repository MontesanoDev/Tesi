# Fix multivalore: suite finale, commit e verifica reale — 1 novembre 2026

**Promozione ancora sospesa: verifica reale incompleta per credito DeepSeek insufficiente.**
Il percorso verificato salva ed esporta correttamente i sette dati USER. Non è ancora
dimostrato l'export completo di codice fiscale e carica, né il caso negativo reale.
Nessun ulteriore fix, push, merge o modifica alla demo.

**Commit isolato:** `930aeef9aa6b354e267c19dcbd5fa3d9c065bdaa`, branch
`narratore-chiarezza/2026-10-31`, nel worktree
`/home/montesano/tesi-narratore-chiarezza-20261031`. Contiene soltanto gli otto file
applicativi e i due file di test del fix. Profilo `sezioni-2026-10-30-r2`, revisione
USER 1. La documentazione locale precedente è rimasta fuori dal commit.

## Test sul codice finale

- Suite backend completa **dopo** la modifica sui nomi con apostrofo:
  **4.329 PASS, 8 SKIP, 464,31 secondi**. Nessuna modifica applicativa successiva.
- Ruff e `git diff --check` PASS. Hash di tutti i file Python applicativi e di test
  verificati invariati rispetto alla suite e al commit.
- Frontend invariato; non è stata ripetuta la sua suite. Il rollback offline già
  verificato è documentato nel [rapporto del fix](user-multivalue-2026-11-01.md).

## Prova DeepSeek reale

Riutilizzati FORM, 56 frammenti SOURCE, audit dell'analisi e prima domanda della
sessione manuale `d9be7d34947145f69892bfc0bf535bad`. Due copie private di database e
storage, separate dall'istanza live, con profili/credenziali rimossi. Nessuna nuova
analisi del modulo e nessuna modifica di SOURCE o gold.

Router e guardia sono **reali**, modello `deepseek-flash`. La risposta iniziale è
quella acquisita nella prova manuale, compresi il rinvio all'albo e gli altri punti.
Le successive due risposte di conferma sono messaggi USER **di prova espliciti**,
conservati nel protocollo: non vengono attribuiti alla conversazione storica.
L'ordine delle domande successive è scelto dal runner tra gli slot già posseduti dal
backend; testo e destinazioni sono renderizzati dalle funzioni applicative. Nessuna
ricevuta, conferma o revisione SOURCE è stata costruita per aggirare i controlli.
È un replay d'integrazione con export HTTP, non una nuova prova manuale nella UI.

1. Il router reale propone di nuovo una risposta anagrafica composta. Il fix separa
   sette valori. La guardia accetta nome e ciascuna delle sei destinazioni aggiuntive
   con `SUPPORTED/SUPPORTED`, in due gruppi oltre al controllo iniziale.
2. Le **sette ricevute USER sono valide**. Prima della conferma d'identità, nessuno
   dei nove campi personali è esportabile: l'estrazione non autorizza la scrittura.
3. Le due conferme di prova, su identità del sottoscrittore e operatore/carica, passano
   router e guardia. Sono valide le ricevute di `s1_c_firmatario`,
   `s1_c_partecipante` e `s2_c_part` per le rispettive destinazioni.
4. Il riuso SOURCE individua `MNTLRD82S14E506X` e
   «amministratore unico e rappresentante legale». Sono proposte selezionabili ma
   ancora prive della revisione del narratore richiesta per esportarle.
5. Entrambi i tentativi previsti dal recupero della sintesi ricevono **HTTP 402,
   `Insufficient Balance`**. Il runner viene fermato prima del caso negativo;
   nessuna ripetizione della prova per cercare un esito migliore.
6. Con rete vietata, l'endpoint ordinario di export produce una bozza parziale:
   verifica sul report e sul testo effettivo del DOCX, con i risultati sotto indicati.

| Dati | Nel DOCX |
|---|---|
| Leonardo Montemurro | Presente |
| Lecce, LE, 14/11/1982 | Presenti |
| Bari, BA, via Amedeo 24 | Presenti |
| Codice fiscale | Vuoto: revisione SOURCE non completata a causa del 402 |
| Carica | Vuota: stesso blocco |
| Checkbox | Nessuna selezionata |

Il file contiene **sette scritture**, tutte USER, con conferme valide. Non si dichiara
superata la verifica dei nove campi: il confronto con l'export storico R2 restituisce
correttamente `passed=false`. Non sono stati rimossi i blocchi per ottenere il DOCX.
Il rinvio all'albo è nuovamente respinto per ambito incoerente; è il limite già
documentato, separato dai sette dati personali correttamente acquisiti.

**Consumo osservato:** 8 richieste al modello, 6 riuscite e 2 respinte con 402;
131.112 token dichiarati nelle risposte riuscite, 15,97 secondi di attesa complessiva
del provider. Il limite preventivo era 14 richieste. Dopo «riprendi», una sola
[lettura del saldo](https://api-docs.deepseek.com/api/get-user-balance/) restituisce
HTTP 200 e `is_available=false` (1 novembre, 16:58 UTC); nessun'altra chiamata al modello.

**Caso negativo reale:** preparato con «nato a Lecce oppure Bari», ma non avviato.
Resta coperto dai test offline; questi non sostituiscono la verifica richiesta con
DeepSeek. Per completare la valutazione servono credito disponibile, la revisione
delle proposte SOURCE già acquisite e una sola prova negativa sul checkpoint pronto.
Non occorre ripetere analisi, prima risposta o conferme già verificate.

## Conservazione e ripresa

App ordinaria: database e stato Git coincidono con la baseline; tag demo sempre
`3a8de0b`. Le due sessioni storiche restano alla versione 15: stato, originali,
112 frammenti SOURCE e 114 artefatti verificati invariati; anche i 138 file della
precedente acquisizione coincidono con il manifesto.

Non si dichiara identico l'intero database live candidato: sono cambiati gli ID di
quattro frammenti di `project-facts.md` (artefatti, non SOURCE), con aggiornamenti
degli indici FTS. Il backend è avviato con `--reload`; il runner inizialmente salvato
come `.py` può provocarne il riavvio. È stato rinominato `.py.txt`. I dati delle prove
e i frammenti SOURCE oggetto del confronto sono invariati; il delta è conservato.

Grezzi in `backend/data/compilation-audit/user-multivalue-deepseek-20261101/`:
protocollo, prompt/schema, risposte HTTP e output reali, tempi/token, ricevute,
stati, DOCX/report parziale, confronti d'integrità e runner. Il checkpoint positivo
contiene le conferme riuscite; quello negativo è ancora iniziale. Copie SQLite
senza profili/login AI, ricompattate; scansione delle credenziali in chiaro negativa.
Backup separato in `/home/montesano/tesi-backups/user-multivalue-deepseek-20261101/`,
con manifesto e checksum. Gli artefatti ignorati da Git richiedono questo backup.
