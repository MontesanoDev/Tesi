export function markdownFilename(title: string) {
  const slug = title
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return `${slug || 'contenuto'}.md`
}

export function fragmentCountLabel(count: number) {
  return count === 1 ? '1 frammento' : `${count} frammenti`
}
