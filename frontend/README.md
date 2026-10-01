# Frontend Mapi RAG

Interfaccia React/TypeScript per progetti, fonti, chat, impostazioni AI e
compilazioni Word o testuali. Il progetto usa Vite, Vitest e Playwright.

Dalla directory `frontend/`:

```bash
npm ci
npm run dev
```

Vite espone l'app sulla porta 5173 e inoltra `/api` al backend su
`http://127.0.0.1:8000`. Per avviare entrambi i processi usare `./start.sh`
dalla radice del repository. `VITE_API_URL` permette di configurare un diverso
indirizzo API durante l'avvio o la build del frontend.

```bash
npm test
npm run lint
npm run build
```

`npm test` esegue i test di componenti, hook e client HTTP; `npm run build`
include il controllo TypeScript e produce `dist/`.

**Prove browser**

Con Vite in esecuzione e i browser Playwright installati (`npx playwright install chromium`),
questi scenari usano API simulate e non richiedono il backend:

```bash
npm run test:e2e -- e2e/composer-model-menu.spec.ts e2e/document-review.spec.ts
```

Per usare una porta diversa:

```bash
PLAYWRIGHT_BASE_URL=http://127.0.0.1:5175 npm run test:e2e -- e2e/document-review.spec.ts
```

La configurazione esegue ogni scenario su desktop e mobile. Screenshot e trace
sono salvati in `artifacts/`. La suite E2E completa comprende anche prove con
backend reale, che creano o modificano dati: usare un ambiente di test dedicato.

La pagina `/demo/candidatura` è una demo autonoma. La vecchia pagina
`/projects/:projectId/review` mostra un esempio di revisione; le compilazioni
effettive e i loro report sono nel Template del progetto.

Configurazione della ricerca e API: [README backend](../backend/README.md).
