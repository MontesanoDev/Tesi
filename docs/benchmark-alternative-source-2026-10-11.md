# Alternative SOURCE nella proposta unica — 11 ottobre 2026

**Esito circoscritto positivo:** sei chiamate DeepSeek reali distinguono due
recapiti e due polizze, mantenendo alternative SOURCE separate senza scegliere
né concatenare. **Il compilatore globale non è ancora pronto alla scrittura**:
restano inferenze sul firmatario e applicabilità unknown. Nessun RESOLVED,
modifica di sessione/originale o DOCX generato. V1 e chat rimangono invariate.

## Causa e scelta

Il precedente schema 5 ammetteva solo value/NA. L'AI sceglieva la polizza A
oppure concatenava due indirizzi; una quote letterale non basta a provare che
quel valore sia unico e pertinente. Contratto sperimentale 6: review con 2–4
fatti SOURCE atomici, proprietà/soggetto/entity/aspect dichiarati comuni,
prove individuali, FORM locale e condizioni. Nessun valore scelto o scrivibile.
Il backend verifica grounding, riferimenti e validità per la posizione. Se
un value ha già fatti referenziati della stessa proprietà con valori diversi,
blocca la scelta. Non deduce conflitti semantici da stringhe differenti.

Una seconda chiamata di revisione non è stata aggiunta: stesso budget e una sola
chiamata per prova, zero retry. La seconda iterazione cambia soltanto le istruzioni
iniziali per omettere record senza prove e distinguere soggetto/ruolo richiesto.
Codice congelato `fd016dd` e `a405f3d`, tre prove per commit, nessuna modifica
durante le serie. Contratti storici conservati per replay, schema 6 corrente.

## Misura reale e confronto

Fixture [Labirinto V1](../demo-documents/benchmark-compilazione/v1/README.md):
55 candidate, sette SOURCE. Gold autoriale e SHA invariati, fuori dal prompt;
nessuna ingestion o DB di test live. Profilo locale `prova`, `deepseek-flash`,
temperatura 0,1, thinking off, timeout 300 s, output massimo 49.152 token.

| Misura | V3 precedente, 3 run | V6, 3 run | V6 istruzioni finali, 3 run |
|---|---|---|---|
| Valori/booleani e ID SOURCE attesi | 18/18/18 su 22 | 22/22/22 | 22/17/22 |
| Di questi grounded | 12/12/12 | 16/16/16 | 16/11/16 |
| Alternative grounded da chiarire | 0/0/0 | 2/2/2 | 2/2/2 |
| Valori impropri grounded | 1/1/2 | 0/1/1 | 0/0/1 |
| Valori impropri grezzi | 2/1/3 | 0/7/8 | 7/0/7 |
| NA improprie grezze | 0/0/0 | 12/5/8 | 2/0/6 |
| Secondi AI | 10,17/9,96/10,05 | 18,06/16,06/16,64 | 15,32/10,59/16,44 |
| Token totali | 17.097/16.986/16.972 | 20.583/19.922/20.223 | 20.072/18.034/20.439 |

La seconda prova finale omette i cinque checkbox tipologia; nessuna perdita dei
valori societari o direttore. Nel piccolo campione finale +14,67% token totali
medi e +40,32% tempo vs V3: **nessun risparmio di latenza dimostrato**. Cache varia;
non è E2E, nessun turno USER misurato. Totale nuovo intervento sei chiamate,
119.273 token/93,11 s AI. Conservate entrambe le iterazioni e tutti i fallimenti.

## Casi concreti osservati

| Posizione | Esito nelle sei acquisizioni |
|---|---|
| Denominazione, forma giuridica, sede, CF/PIVA | Valori SOURCE attesi sempre proposti e grounded, mai USER |
| Direttore / qualifica / ordine / albo | Giulia Serra / Ingegnere / Ordine di Ancona / **5739**, sempre corretti grezzi; applicabilità blocca il valore |
| Recapito corrispondenza | Via del Porto 2, Ancona **oppure** Via dei Tigli 7, Jesi; due fatti da SOURCE -3; review, nessuna concatenazione |
| Polizza vigente | RC-OR-2026-A da SOURCE -4 **oppure** RC-OR-2026-B da -5; review, nessuna priorità inventata |
| Sede operativa coincidente | NA grounded in 5/6, ultima serie 3/3; altra proposta bloccata |
| Firmatario | In 3/6 inferito da «Amministratore unico: Paolo Conti.» e grounded; resta NON verificato semanticamente, nessuna scrittura |
| Date/ISO/organigramma mancanti | Nessun valore inventato; qualche NA improprio rifiutato |

La polizza è chiamata ambiguous nei primi due run, conflicting negli altri
quattro; il gold resta CONFLICTING. La distinzione semantica non è certificata,
anche perché le attestazioni non dichiarano esclusività. Il risultato utile è
la conservazione di entrambe le prove senza scegliere. Lo scorer confronta
soltanto tipo review/ID SOURCE, non completezza/entailment. Tutte le proposte
restano `semantic_review_required=true`, `written_value=null`.

## Verifiche e limiti

Finali **264 test mirati**, **1.670 backend completi**, Ruff, fixture check,
CLI help e diff. Regressioni software su prove individuali, proprietà/soggetti
diversi, ID/quote inesistenti, duplicate/limiti, no valore in review, condizioni
unknown, SOURCE vietate/altro progetto e replay V5. Provider simulati dove serve
nelle suite, nessun modello reale nei test software; frontend invariato.

Le identità/proprietà sono proposte dall'AI: uguaglianza dei metadati non prova
che la SOURCE li implichi. Il gate non trova un'alternativa omessa dall'output,
non certifica atomicità, scope/applicabilità o priorità temporali. Firma/ruolo
restano un caso concreto da affrontare prima dell'adapter. Le alternative per
checkbox non sono supportate da questo tipo review. Nessuna migrazione o reindex.

Prossimo punto **da discutere prima del codice**: legame fra valore SOURCE,
soggetto e ruolo FORM e applicabilità del ramo, mantenendo una chiamata e gate
conservativi. Non attivare il prototipo nella chat o rimuovere V1.

## Acquisizioni recuperabili

[Registro completo](../relazioni.md), JSON per tutte le 55 posizioni nelle
[prime tre](benchmarks/2026-10-11-labirinto-alternatives-v6.json) e
[tre finali](benchmarks/2026-10-11-labirinto-alternatives-v6b.json).
[Bundle](benchmarks/2026-10-11-labirinto-alternatives-audit.tar.gz) e
[SHA-256](benchmarks/2026-10-11-labirinto-alternatives-audit.tar.gz.sha256): codice,
Word/fonti/gold congelati, prompt/schema/request, HTTP/raw/usage/validator,
confronti e log, esclusi DB/configurazioni/credenziali. SHA del Word:
`eaa3c2b8e45e147d35766e71f77b90bbb0bdc9a339ee79dd12e6ab007ad9c7ca`.

Grezzi locali `backend/data/compilation-audit/alternatives-v6{,b}-20261011-run{1,2,3}/`,
checks e analysis adiacenti. Il solo push non salva backend/data: usare il bundle
versionato. Commit piccoli autorizzati, nessun push effettuato.
