export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init)
  if (!response.ok) throw new Error(`Request failed (${response.status}).`)
  return response.json() as Promise<T>
}

export function post<T>(path: string, data: object): Promise<T> {
  return api<T>(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
}
