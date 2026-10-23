# Verifica mirata delle attribuzioni tabellari

Quattro proposte errate controllate su FORM/SOURCE reali: **grounded 4 → 0**.
Nessuna nuova scrittura errata individuata nei DOCX storici; nove audit/export
restano identici. Nessuna nuova chiamata LLM o sessione.

- [Rapporto e limiti esatti](../../docs/attribuzioni-tabellari-2026-10-19.md)
- [Esito e copertura](ESITO.json)
- [Probe prima](probes-before.json) e [dopo](probes-after.json)
- [Nove replay invariati](REGRESSIONE.json)
- [37 scritture tabellari esistenti](SCRITTURE-TABELLARI-ESISTENTI.json)
- [Conservazione dello stato precedente](CONSERVAZIONE.json)
- [Backup](BACKUP.json) e [verifica indipendente](VERIFICA-BACKUP.json)

23 nuovi test permanenti, 347 mirati PASS, 2.744 backend PASS e Ruff PASS.
Il nuovo veto copre righe etichetta–valore riconoscibili, con confini conservativi.
Non è una certificazione universale di record multicolonna o dell'identità
personale. Tra le 35 scritture SOURCE esaminate determina il tipo del soggetto
su 13, non su 22; compatibilità del tipo non prova identità, ruolo o applicabilità.

I probe sono assegnazioni deliberatamente errate create in copie degli input:
non vanno descritti come output prodotti dal provider nella chat storica.
I DOCX in `replay/` sono ricostruzioni offline, non nuove compilazioni reali.
I residui precedenti sono conservati. Nessun commit/push.
