# Comandi conversazionali V1

28 turni preparati prima delle API: rinvii locali, pause globali, messaggi misti,
negazioni, ripresa ed export. Word e checkpoint copiati dal Dialogo V1 congelato;
scenari nuovi, gold separato. Nessuna modifica al gold dei 43 casi originari.

Regola corrente mantenuta: PAUSE/FINISH prevalgono sui dati nello stesso turno.
Un rinvio locale non mette in pausa la sessione; UNKNOWN non significa SKIP.
Il consenso breve autorizza export soltanto alla domanda di generazione.
Le richieste esplicite di bozza fuori da quel checkpoint sono FINISH.

Gold escluso dal prompt. Prove BEFORE e AFTER sul medesimo scenario, con
DeepSeek reale, DB/storage temporanei e servizi di scrittura reali. Nessuna
nuova analisi SOURCE o misura di completezza del modulo. Non cambiare le
aspettative dopo aver visto il risultato. Un errore è conservato nel report.

Runner: backend/scripts/benchmark_compilation_dialogue.py --fixture questo
percorso --project un-progetto-DeepSeek --output una-directory-nuova.
