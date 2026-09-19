import type { KnowledgeSource, ProjectDetail, StatusTone } from '../types'

interface DisplayedKnowledgeSource {
  id: string
  name: 'Dati del progetto' | 'Company KB' | 'General KB'
  tone: StatusTone
  itemCount: number
}

function sourceCountLabel(name: DisplayedKnowledgeSource['name'], count: number) {
  if (name === 'Dati del progetto') {
    return count === 1 ? '1 dato estratto' : `${count} dati estratti`
  }
  return count === 1 ? '1 documento' : `${count} documenti`
}

function findSource(
  sources: KnowledgeSource[],
  names: string[],
): KnowledgeSource | undefined {
  return sources.find((source) => names.includes(source.name))
}

function displayedSources(project: ProjectDetail): DisplayedKnowledgeSource[] {
  const callFacts = findSource(project.knowledge_sources, [
    'Call Facts',
    'Dati estratti dal bando',
    'Dati del progetto',
  ])
  const company = findSource(project.knowledge_sources, ['Company KB'])
  const general = findSource(project.knowledge_sources, ['General KB'])

  return [
    {
      id: 'call-facts',
      name: 'Dati del progetto',
      tone: 'info',
      itemCount: callFacts?.name === 'Dati del progetto' ? callFacts.item_count : project.call_fact_count,
    },
    {
      id: 'company-kb',
      name: 'Company KB',
      tone: company?.tone ?? 'info',
      itemCount: company?.item_count ?? 0,
    },
    {
      id: 'general-kb',
      name: 'General KB',
      tone: general?.tone ?? 'info',
      itemCount: general?.item_count ?? 0,
    },
  ]
}

export function ProjectKnowledgeSummary({ project }: { project: ProjectDetail }) {
  return (
    <section
      className="project-knowledge-summary"
      aria-labelledby="project-knowledge-summary-title"
    >
      <h2 id="project-knowledge-summary-title">Conoscenza utilizzata</h2>
      <div className="project-knowledge-summary-list">
        {displayedSources(project).map((source) => (
          <div className="project-knowledge-summary-item" key={source.id}>
            <span className={`source-dot source-dot--${source.tone}`} aria-hidden="true" />
            <strong>{source.name}</strong>
            <span>{sourceCountLabel(source.name, source.itemCount)}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
