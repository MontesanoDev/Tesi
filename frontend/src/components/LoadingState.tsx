export function LoadingState({ label = 'Caricamento' }: { label?: string }) {
  return (
    <div className="state-view" role="status">
      <span className="spinner" />
      <span>{label}</span>
    </div>
  )
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="state-view state-view--error" role="alert">
      {message}
    </div>
  )
}
