# Legame persona/ruolo nella proposta unica — 11 ottobre 2026

**Miglioramento circoscritto di sicurezza, copertura generale regredita.**
Il backend sperimentale impedisce il salto amministratore → firmatario. Nelle
ultime tre prove reali riconosce il legame letterale dei quattro dati direttore,
incluso **5739**; l'applicabilità del ramo rimane sconosciuta e blocca il campo.
Nessun RESOLVED, scrittura, sessione o attivazione nella chat.

## Causa concreta e cambiamento

Nel precedente V6b run 3 `t2.r0.c1` proponeva Paolo Conti come sottoscrittore,
citando «Amministratore unico: Paolo Conti.». Nome presente, proprietà del fatto
inventata come «nome del sottoscrittore»: il vecchio grounding accettava la
presenza del nome, senza prova di quel ruolo. L'esito era comunque soggetto a
revisione semantica, non un valore scrivibile.

Contratto V7: `bindings` condivisi (massimo 128), con ruolo richiesto nel FORM,
ruolo attestato nella SOURCE e prove; `binding_id` necessario dal backend per
assegnazioni `value` da fatti person. Il backend rilegge gli estratti, controlla
contesto strutturale e uguaglianza letterale dei ruoli (NFC/case/spazi). Richiede
«ruolo: persona» all'inizio di una clausola del chunk SOURCE reale, con il subject
del fatto, nello stesso chunk di ogni prova del valore. Una quote ritagliata da
«non è ruolo: persona» non basta. Nessuna lista di cariche, nomi o campi hardcoded.

Contesto del ruolo: riga/header Word esplicito, ultimo paragrafo del corpo prima
del blocco o ultima sezione outline. Il requisito del campo conserva il distinto
gate locale. Binding mancante/invalido => REVIEW_REQUIRED senza valore scelto;
precedenti REJECTED restano tali. Prove di ruolo/valore e proposta grezza restano
nell'audit. Il gate non calcola applicabilità né promuove a RESOLVED.

## Protocollo e tutte le iterazioni

Nove chiamate reali `deepseek-flash`: tre per commit congelato, nessuna modifica
nel corso delle serie. Stessi Word/fonti/gold della fixture sintetica
[Labirinto V1](../demo-documents/benchmark-compilazione/v1/README.md), 55 candidate,
sette SOURCE ammesse; configurazione provider reale del profilo `prova`.
**Non è un test E2E della chat o della KB locale Mapi.** Gold escluso dal prompt,
nessun caricamento nel DB, USER, retry, reviewer o chiamata per campo. Temperatura
0,1, thinking off, timeout 300 s, massimo 49.152 token output. Catalogo V3,
SOURCE e budget invariati; cambiano contratto/prompt rispetto a V6b.

| Misura, tre run per colonna | V6b precedente | V7 `97d84fb` | V7b `c2b30b0` | V7c finale `5962cb6` |
|---|---|---|---|---|
| Valori/booleani e ID SOURCE attesi su 22 | 22/17/22 | 17/16/13 | 17/16/17 | **17/17/17** |
| Di questi grounded | 16/11/16 | 11/11/11 | 11/11/11 | **11/11/11** |
| Valori impropri grounded | 0/0/1 | 0/0/0 | 0/0/0 | **0/0/0** |
| Dati direttore con literal_match del ruolo | Non previsto | 0/0/0 | 0/0/0 | **4/4/4** |
| Alternative recapiti/polizza conservate | 2/2/2 | 2/2/2 | 2/2/2 | **2/2/2** |
| Omissioni/non valutati | 13/35/9 | 32/21/38 | 35/35/31 | 35/33/32 |
| Rifiuti locali | 23/6/26 | 9/21/4 | 7/7/11 | 7/7/7 |
| Secondi AI | 15,32/10,59/16,44 | 13,07/15,44/10,63 | 10,71/11,17/12,11 | **12,02/12,37/12,80** |
| Token totali | 20.072/18.034/20.439 | 19.157/20.295/18.601 | 18.822/18.999/19.291 | **19.064/19.247/19.372** |

Prima serie: ruolo completo «Direttore tecnico della società di ingegneria»
contro ruolo SOURCE «direttore tecnico», quindi controllo conservativamente
negativo. Due valori ordine inglobano il numero e il terzo omette l'albo; nessun
cambiamento del gold. Seconda iterazione chiarisce ruolo funzionale/contesto,
ma il modello omette tutti i binding in 3/3. Non sono risultati soddisfacenti.

Ultima iterazione: istruzioni compatte con un solo esempio JSON di riferimenti,
interamente segnaposto. Schema/validator non cambiano dopo il primo commit.
Il modello conserva il contesto FORM completo e collega quattro proprietà
atomiche al medesimo ruolo letterale; nessun sinonimo o gate allentato. Tutte
le prove, incluse quelle regredite, rimangono recuperabili.

## Casi concreti dell'ultima serie

| Campo | Valore/prova | Esito sperimentale |
|---|---|---|
| Denominazione | Orione Tecnica S.r.l., SOURCE -1 | Proposta grounded 3/3 |
| Forma giuridica | società a responsabilità limitata, SOURCE -1 | Proposta grounded 3/3 |
| Sede legale | Via delle Querce 18, 60121 Ancona (AN), SOURCE -1 | Proposta grounded 3/3 |
| CF e P.IVA | 01234567897, SOURCE -1, due proprietà distinte | Proposte grounded 3/3 |
| Direttore: nome | Giulia Serra, SOURCE -2 | Ruolo literal_match 3/3; campo bloccato da applicabilità |
| Direttore: qualifica | Ingegnere, SOURCE -2 | Stesso esito, fatto atomico distinto |
| Direttore: ordine | Ordine degli Ingegneri di Ancona, SOURCE -2 | Stesso esito, nessuna concatenazione con albo |
| Direttore: albo | **5739**, SOURCE -2 | Stesso esito, distinto dal numero documento 8821 |
| Firmatario/carica | Paolo Conti / Amministratore unico proposti nel run 2/3 | **REVIEW_REQUIRED, value=null**, manca ruolo pertinente |
| Recapito/polizza | Due fatti distinti per proprietà, SOURCE -3 / -4 e -5 | Review senza scelta 3/3 |
| Checkbox tipologia | Cinque posizioni omesse | Non valutate, NON false/NA verificate |
| Sede operativa coincidente | Proposta di valore nei run 1/2, NA nel run 3 | Valore bloccato; NA grounded solo 1/3 |
| ISO mancante | NA impropria nel run 3 | Rifiutata, nessun valore inventato |

SOURCE sono fittizie e autoriali: non dati societari reali. Nei run 2/3 il
modello continua a inferire firmatario/carica: è il backend a impedire la
promozione. Nel run 1 li omette; omissione non significa MISSING verificato.
Nella prima serie un ID SOURCE inventato (-201) è rifiutato; nessun valore
vietato/di altro progetto viene accettato. Le due alternative restano review
in tutte le nove chiamate, senza scegliere o concatenare.

Esempio reale del binding finale: origine FORM paragraph:63, quote completa
«Direttore tecnico della società di ingegneria»; required_role «Direttore tecnico»;
source_role «direttore tecnico»; SOURCE -2, quote «Orione Tecnica S.r.l. — direttore
tecnico: Giulia Serra.». I candidate t6.r0.c1–t6.r3.c1 condividono questo binding,
ma ognuno mantiene il proprio fatto, valore e prove. `literal_match` non elimina
la condizione di ramo unknown e non autorizza scritture.

Replay offline distinto: la vecchia risposta V6b run 3 è invariata e validata
identicamente; una nuova copia controfattuale con version=7/bindings vuoto
blocca il firmatario prima grounded. Non è una nuova risposta del provider.

## Costi e verifica

Ultima serie: **57.683 token/37,18 s AI**, media 19.227,67 token/12,39 s;
vs V6b token totali medi −1,47%, input +5,15%, tempo −12,22%. Campione piccolo,
cache diversa e output meno completo: **non dimostra risparmio E2E né maggiore
copertura**. Totale intervento: **172.848 token/110,30 s AI, nove chiamate**.
Non sono stati misurati turni USER, sessioni persistite o rendering.

Verifiche finali: **295 mirati/11,95 s**, **1.701 backend/105,41 s**, Ruff,
fixture `--check`, CLI help e diff. Test software senza modello reale per i
nuovi gate, provider simulati dove serve nelle suite. Regole positive/negative,
assenza binding, altro soggetto, ruolo narrativo/negato, quote ritagliata,
contesto/ramo errato, provenienza/isolamento, same-file rebinding, due proprietà,
applicabilità unknown, alternative e replay storico. Prima failure Ruff (riga
101 caratteri) e aspettativa schema V6 (mirati e prima suite completa) conservate;
corrette prima della prima serie reale. Nessuna verifica frontend: invariato.

## Limiti e punto di ripresa

Il controllo è di **tracciabilità letterale necessaria**, non un verificatore
semantico generale. Entity, proprietà, ruolo funzionale e completezza dei suoi
qualificatori restano proposte dal modello. Un dato di un'altra persona nello
stesso chunk, una negazione complessa o un ruolo ritagliato male richiedono ancora
revisione semantica. Un fatto erroneamente classificato company/other può
sfuggire al controllo personale: resta comunque non RESOLVED/non scrivibile.
Sinonimi, narrativa, ruoli su chunk diversi o titoli intermedi possono essere
falsi negativi. Il gate non stabilisce appartenenza/qualificazione organizzativa.
`semantic_review_required=true` e `written_value=null` restano obbligatori.

Il caso positivo con un firmatario esplicitamente designato è coperto da test
software generici, non da una nuova fixture reale; il positivo reale qui è il
direttore. Applicabilità, checkbox omesse e completezza generale rimangono aperti.
**Non congelare il nuovo compilatore come pronto alla chat/renderer.** Il prossimo
passo va discusso: collegamento delle condizioni al ramo e SOURCE, con controllo
della copertura checkbox prima dell'adapter. Non aggiungere reviewer/batch, non
trasformare literal_match in una certificazione. V1/chat/RAG/parser/renderer
sono invariati, nessuna migrazione/reindicizzazione o dato locale modificato.

## Dati recuperabili

[Registro](../relazioni.md); JSON per tutte le posizioni delle serie
[V7](benchmarks/2026-10-11-labirinto-subject-binding-v7.json),
[V7b](benchmarks/2026-10-11-labirinto-subject-binding-v7b.json) e
[V7c](benchmarks/2026-10-11-labirinto-subject-binding-v7c.json).
[Bundle audit](benchmarks/2026-10-11-labirinto-subject-binding-audit.tar.gz) e
[checksum](benchmarks/2026-10-11-labirinto-subject-binding-audit.tar.gz.sha256):
code snapshot/commit, fixture/fonti/gold congelati, prompt/schema/request,
HTTP/raw/usage, validazioni, quote/provenienza, replay, analisi e log dei test.
Esclusi credenziali, DB e configurazioni locali. Originale SHA-256:
`eaa3c2b8e45e147d35766e71f77b90bbb0bdc9a339ee79dd12e6ab007ad9c7ca`.
Grezzi locali `backend/data/compilation-audit/subject-binding-v7{,b,c}-20261011-run{1,2,3}/`;
checks e analysis adiacenti. Il bundle versionato salva ciò che backend/data
esclude dal solo push. Commit piccoli autorizzati, nessun push effettuato.
