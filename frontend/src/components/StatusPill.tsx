import type { StatusTone } from '../types'

interface StatusPillProps {
  children: React.ReactNode
  tone?: StatusTone
}

export function StatusPill({ children, tone = 'info' }: StatusPillProps) {
  return <span className={`status-pill status-pill--${tone}`}>{children}</span>
}
