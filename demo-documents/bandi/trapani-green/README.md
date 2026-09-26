# Terzo caso: Trapani Green

Caso aggiunto il 23 settembre 2026. **Simulazione didattica con dati aziendali
inventati, non una candidatura reale o una verifica di ammissibilita'.**

## Documenti ufficiali

Il [Comune di Trapani](https://comune.trapani.it/novita/progetto-trapani-green-nuovo-avviso-per-laffidamento-dellincarico-professionale-di-progettazione-esecuzione-dei-lavori/)
ha pubblicato il 28 febbraio 2023 il nuovo avviso Trapani Green, relativo a
progettazione, direzione lavori e sicurezza per interventi di adattamento
climatico urbano. Si usa l'Allegato A, non l'intera pratica.

- [Avviso PDF](originali/avviso.pdf): fonte da caricare nel progetto.
- [Schema di disciplinare PDF](originali/disciplinare.pdf): altra fonte del progetto.
- [Allegato A DOCX](originali/manifestazione-interesse.docx): da caricare in Template.
- [Provenienza e hash](fonti.json): download originali, senza conversioni o modifiche.
- [Indicazioni della prova](istruzioni.txt): scelte della simulazione, fissate prima del test.
- [Generalita' Mapi simulate](../../generalita-mapi.md): fonte aziendale, non prova di requisiti reali.

E' un procedimento storico: i dati simulati del 2026 non attestano requisiti
posseduti nel 2023. Non si preparano firme o invii. Gli altri allegati ufficiali
non sono inclusi in questa prova circoscritta.

## Come provarlo nell'applicazione

1. Aprire un progetto dedicato **Trapani Green - Progettazione e sicurezza**.
2. Nel contesto del progetto caricare solo avviso e disciplinare PDF di questa cartella.
3. Usare la scheda Mapi ampliata nella Company KB, evitando copie contraddittorie.
4. Aprire **Template > Word (.docx)** e scegliere `manifestazione-interesse.docx`.
5. Inserire le indicazioni di `istruzioni.txt` e premere **Compila Word**.
6. Scaricare e controllare bozza e report. Non serve estrarre prima i facts.

Il DOCX e' il modello da compilare, non una fonte della KB. Le indicazioni
costituiscono scelte utente esplicite: ometterle e' una prova diversa, non una
ripetizione delle stesse condizioni.

## Criteri fissati prima della chiamata AI

1. Il sottoscrittore scelto e' Luca Ferri. Non inventare i suoi dati personali.
2. La sezione societa' di ingegneria puo' ricevere ragione sociale, sede e recapiti
   presenti nella scheda. La PEC del Comune non e' quella del concorrente.
3. Altri rami e tabelle dei professionisti associati devono restare vuoti.
4. La tabella dei servizi pregressi resta vuota: descrivere attivita' aziendali
   non prova contratti, CIG, importi o incarichi precedenti.
5. Iscrizioni, dichiarazioni, requisiti, firma e luogo/data restano da revisionare.
   Non usare il numero d'albo di Elisa Romano per Luca Ferri o per altre professioni.
6. I dati mancanti, compreso il CIG dell'avviso lasciato vuoto nell'originale,
   non devono essere completati per deduzione.
7. Il testo prestampato e le opzioni non pertinenti non vengono cancellati dal
   compilatore attuale: il Word non e' pronto per l'invio neppure se i dati sono corretti.

## Compatibilita' preliminare

Con il parser corrente il modello originale contiene **115 posizioni candidate**:
54 celle e 61 segnaposti, senza paragrafi segnalati come non supportati. Sono
posizioni tecniche, non 115 informazioni necessarie o campi da riempire.
Il documento mette alla prova rami alternativi, paragrafi e tabelle ripetute.

Prima di scegliere Trapani e' stato esaminato anche il modulo di Bovolone per
la caserma dei Carabinieri. L'anagrafica usa tabulazioni senza segnaposti, non
riconosciute dal parser: non e' stato modificato ne' usato per una prova live.
Questa e' una selezione per compatibilita' strutturale, non un campione casuale
o una dimostrazione di supporto a qualsiasi modulo.

## Ripetizione isolata

Dalla cartella `backend`, usando la configurazione API gia' presente:

```bash
.venv/bin/python -m scripts.compile_docx_demo --case trapani --live \
  --company-file ../demo-documents/generalita-mapi.md
```

Il comando esegue vere chiamate API a consumo, passando per ingestion e API
FastAPI con un database temporaneo. Non modifica i progetti o le KB dell'app.
Conserva input, prompt, risposte, errori eventuali, originale, bozza e report
in una nuova directory sotto `backend/data/docx-demo/`, esclusa da Git.
Non sovrascrive prove precedenti e non rilancia un'intera compilazione per
scegliere il risultato migliore.

La prova e' esplorativa: un file prodotto e scaricabile non equivale a una
compilazione semanticamente corretta. La prima esecuzione ha prodotto il Word
in 32,91 secondi, con 12 scritture: nove coerenti con il perimetro e tre fuori
posto. [Resoconto completo e file della prova](verifica.md).

Nell'app locale il progetto **Trapani Green - Progettazione e sicurezza** e'
gia' presente con i due PDF indicizzati. Lo storico della prova isolata non e'
stato trasferito nel database dell'app; il DOCX si seleziona dalla schermata
Template. Non sono state modificate le fonti globali o gli altri progetti.
