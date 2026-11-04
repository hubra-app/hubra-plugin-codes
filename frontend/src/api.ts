import { apiFetch } from '@hubra/plugin-sdk'

export interface Code {
  id: number
  name: string
  code: string
  description: string | null
  isActive: boolean
  updatedAt: string
}

interface BackendCode {
  id: number
  name: string
  code: string
  description: string | null
  is_active: boolean
  updated_at: string
}

const adapt = (b: BackendCode): Code => ({
  id: b.id,
  name: b.name,
  code: b.code,
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
    code: input.code,
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
