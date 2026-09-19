import type { DocumentCompilation } from '../types'

export function documentCompilationFixture(projectId = 'docx-test', id = 'run-1'): DocumentCompilation {
  return {
    id, project_id: projectId, template_name: 'domanda-partecipazione.docx',
    created_at: '2026-09-15T13:10:21Z', status: 'needs_review',
    downloads: { docx: '', report: '', template: '' },
    report: {
      schema_version: 1, project_id: projectId, created_at: '2026-09-15T13:10:21Z',
      status: 'needs_review', ready_for_submission: false, model: 'test-model',
      prompt_version: 'docx-fields-v1', template_sha256: 'abc', output_sha256: 'def',
      total_tokens: 100, instructions: 'Partecipazione singola. Non compilare le firme.',
      written_field_count: 1, unresolved_field_count: 2,
      source_coverage: { total_chunks: 80, selected_chunks: 60, total_characters: 50000,
        selected_characters: 40000, partial: true, strategy: 'bounded_spread_by_scope' },
      warnings: ['Dati simulati, utilizzabili solo per demo.', 'Contesto parziale: verificare anche le fonti non selezionate.'],
      unclassified_cells: ['t2.r0.c0', 't2.r0.c1'],
      fields: [
        { cell_id: 't0.r0.c1', label: 'Ragione sociale', entity: 'company', kind: 'data',
          status: 'proposed', value: 'Mapi Ingegneria S.r.l.', written_value: 'Mapi Ingegneria S.r.l.',
          reason: 'Denominazione presente nella visura simulata.', validation_notes: [],
          evidence: [{ source_id: 'company:1', document_id: 1, source_name: 'visura-simulata.pdf',
            scope: 'company', fragment: 2, page: null, quote: 'Denominazione: Mapi Ingegneria S.r.l.', content_sha256: '123' }],
        },
        { cell_id: 't0.r1.c1', label: 'Codice fiscale del firmatario', entity: 'person', kind: 'data',
          status: 'missing', value: null, written_value: null, reason: 'Non presente nelle evidenze fornite.',
          validation_notes: [], evidence: [],
        },
        { cell_id: 't0.r2.c1', label: 'Qualifica del firmatario', entity: 'person', kind: 'data',
          status: 'needs_review', value: 'Legale rappresentante', written_value: null,
          reason: 'Ruolo da confermare.', validation_notes: ['Il valore non compare letteralmente nelle evidenze citate'], evidence: [],
        },
        { cell_id: 't0.r3.c1', label: 'Mandanti del raggruppamento', entity: 'company', kind: 'choice',
          status: 'not_applicable', value: null, written_value: null,
          reason: 'Partecipazione singola indicata esplicitamente.', validation_notes: [], evidence: [],
        },
      ],
    },
  }
}
