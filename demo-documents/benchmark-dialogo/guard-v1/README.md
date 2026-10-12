# Verifica della pertinenza USER V1

Nove proposte preparate prima delle API, con aspettative nel manifest/gold.
La prima riproduce valore, slot ed estratto del raw DeepSeek errato della
baseline Dialogo V1. Le altre introducono assegnazioni errate, corrette o
ambigue: non sono presentate come nuovi output del router.

Il verificatore usa DeepSeek reale; ciascuna proposta ammessa attraversa il
dominio e viene riletta dal DB temporaneo. Prove separate dal confronto dei
43 turni: non sommare i loro punteggi o attribuirli al router.
Il gold non entra nel prompt. La base Word/contesti è Dialogo V1, con gli hash
fissati nel manifest. Nessun dato live modificato, nessuna SOURCE inventata.
Massimo nove chiamate seriali, una per gruppo, nessun retry.
