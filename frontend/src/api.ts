import { apiFetch } from '@hubra/plugin-sdk'

export interface Code {
  id: number
  name: string
  description: string | null
  isActive: boolean
  updatedAt: string
}

// The code itself is never in a list or detail answer: revealCode asks for
// one, and the server writes who saw it into the audit log.
interface BackendCode {
  id: number
  name: string
  description: string | null
  is_active: boolean
  updated_at: string
}

const adapt = (b: BackendCode): Code => ({
  id: b.id,
  name: b.name,
  description: b.description,
  isActive: b.is_active,
  updatedAt: b.updated_at,
})

export interface CodeInput {
  name: string
  code: string
  description: string | null
  isActive?: boolean
}

const body = (input: CodeInput) =>
  JSON.stringify({
    name: input.name,
    // Left empty when editing: the code stays as it is.
    ...(input.code ? { code: input.code } : {}),
    description: input.description,
    ...(input.isActive === undefined ? {} : { is_active: input.isActive }),
  })

export async function listCodes(): Promise<Code[]> {
  return (await apiFetch<BackendCode[]>('/codes/')).map(adapt)
}

export async function createCode(input: CodeInput): Promise<Code> {
  return adapt(await apiFetch<BackendCode>('/codes/', { method: 'POST', body: body(input) }))
}

export async function updateCode(id: number, input: CodeInput): Promise<Code> {
  return adapt(await apiFetch<BackendCode>(`/codes/${id}`, { method: 'PATCH', body: body(input) }))
}

export async function deleteCode(id: number): Promise<void> {
  await apiFetch(`/codes/${id}`, { method: 'DELETE' })
}

export async function revealCode(id: number): Promise<string> {
  const res = await apiFetch<{ id: number; code: string }>(`/codes/${id}/reveal`, {
    method: 'POST',
  })
  return res.code
}
