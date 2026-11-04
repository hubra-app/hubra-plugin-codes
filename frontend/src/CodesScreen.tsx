import { useState } from 'react'
import {
  ActionIcon,
  Button,
  Checkbox,
  CopyButton,
  Group,
  Paper,
  PinInput,
  Slider,
  Text,
  Textarea,
  TextInput,
  Tooltip,
} from '@mantine/core'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  IconCheck,
  IconCopy,
  IconEye,
  IconEyeOff,
  IconPencil,
  IconPlus,
  IconTrash,
} from '@tabler/icons-react'
import {
  ConfirmModal,
  DataTable,
  Field,
  formatDateTime,
  Modal,
  PageHead,
  useAuth,
  useT,
  useToast,
} from '@hubra/plugin-sdk'
import { createCode, deleteCode, listCodes, updateCode, type Code, type CodeInput } from './api'

const QK = ['codes'] as const

const EMPTY: CodeInput = { name: '', code: '', description: '', isActive: true }

type Status = 'all' | 'active' | 'inactive'

const mono = '"JetBrains Mono", monospace'

export function CodesScreen() {
  const { t } = useT()
  const { notify } = useToast()
  const { hasPermission } = useAuth()
  const qc = useQueryClient()
  const { data: codes = [], isLoading } = useQuery({ queryKey: QK, queryFn: listCodes })

  // null = closed, 'new' = add, a code = edit
  const [editing, setEditing] = useState<Code | 'new' | null>(null)
  const [form, setForm] = useState<CodeInput>(EMPTY)
  const [errors, setErrors] = useState<{ name?: string; code?: string }>({})
  const [length, setLength] = useState(4)
  const [saving, setSaving] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<Code | null>(null)
  const [visible, setVisible] = useState<Set<number>>(new Set())
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<Status>('all')

  const canCreate = hasPermission('codes.codes.create')
  const canUpdate = hasPermission('codes.codes.update')
  const canDelete = hasPermission('codes.codes.delete')

  const open = (target: Code | 'new') => {
    const c = target === 'new' ? null : target
    setForm(
      c
        ? { name: c.name, code: c.code, description: c.description ?? '', isActive: c.isActive }
        : EMPTY,
    )
    setLength(c?.code.length || 4)
    setErrors({})
    setEditing(target)
  }

  const save = async () => {
    const next = {
      name: form.name.trim() ? undefined : t('common.nameRequired', 'Name ist erforderlich'),
      code: form.code.trim() ? undefined : t('validation.codeRequired', 'Code ist erforderlich'),
    }
    setErrors(next)
    if (next.name || next.code || saving || !editing) return
    setSaving(true)
    const input = { ...form, description: form.description?.trim() || null }
    try {
      if (editing === 'new') await createCode({ ...input, isActive: undefined })
      else await updateCode(editing.id, input)
      qc.invalidateQueries({ queryKey: QK })
      setEditing(null)
      notify('success', t('codes.saved'))
    } catch (err: unknown) {
      notify('error', t('common.error'), err instanceof Error ? err.message : t('codes.saveError'))
    } finally {
      setSaving(false)
    }
  }

  const remove = async () => {
    if (!deleteTarget) return
    try {
      await deleteCode(deleteTarget.id)
      qc.invalidateQueries({ queryKey: QK })
      setDeleteTarget(null)
      notify('success', t('codes.deleted'))
    } catch (err: unknown) {
      notify('error', t('common.error'), err instanceof Error ? err.message : t('codes.deleteError'))
    }
  }

  const toggle = (id: number) =>
    setVisible((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })

  const statusChip = (c: Code) => (
    <span
      className={`chip${c.isActive ? ' on' : ''}`}
      style={{ fontSize: 'var(--mantine-font-size-xs)', flexShrink: 0 }}
    >
      {c.isActive ? t('codes.active') : t('codes.inactive')}
    </span>
  )

  const eye = (c: Code, size: number) => (
    <ActionIcon
      variant="subtle"
      onClick={() => toggle(c.id)}
      title={visible.has(c.id) ? t('codes.codeHidden') : t('codes.codeVisible')}
    >
      {visible.has(c.id) ? <IconEyeOff size={size} /> : <IconEye size={size} />}
    </ActionIcon>
  )

  const actions = (c: Code) => (
    <Group gap={4} wrap="nowrap">
      {canUpdate && (
        <ActionIcon variant="subtle" onClick={() => open(c)} aria-label={t('codes.edit')}>
          <IconPencil size={16} />
        </ActionIcon>
      )}
      {canDelete && (
        <ActionIcon
          variant="subtle"
          color="red"
          onClick={() => setDeleteTarget(c)}
          aria-label={t('codes.delete')}
        >
          <IconTrash size={16} />
        </ActionIcon>
      )}
    </Group>
  )

  const shown = (c: Code) => (visible.has(c.id) ? c.code : '•'.repeat(c.code.length))

  const renderCard = (c: Code) => (
    <Paper
      withBorder
      radius="lg"
      p="md"
      h="100%"
      style={{ display: 'flex', flexDirection: 'column', gap: 12 }}
    >
      <Group justify="space-between" wrap="nowrap" align="flex-start">
        <Text fw={700} style={{ minWidth: 0, overflowWrap: 'anywhere' }}>
          {c.name}
        </Text>
        {statusChip(c)}
      </Group>
      <Group gap={6} wrap="nowrap">
        <code
          style={{
            flex: 1,
            minWidth: 0,
            fontFamily: mono,
            fontSize: 'var(--mantine-font-size-xl)',
            fontWeight: 700,
            textAlign: 'center',
            background: 'var(--hb-surface-2)',
            padding: '10px 12px',
            borderRadius: 10,
            letterSpacing: visible.has(c.id) ? '0.12em' : '0.2em',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {shown(c)}
        </code>
        {eye(c, 18)}
        <CopyButton value={c.code} timeout={1500}>
          {({ copied, copy }) => (
            <Tooltip
              label={copied ? t('common.copied', 'Kopiert') : t('common.copy', 'Kopieren')}
              withArrow
            >
              <ActionIcon variant="subtle" color={copied ? 'green' : undefined} onClick={copy}>
                {copied ? <IconCheck size={18} /> : <IconCopy size={18} />}
              </ActionIcon>
            </Tooltip>
          )}
        </CopyButton>
      </Group>
      {c.description && (
        <Text size="sm" c="dimmed">
          {c.description}
        </Text>
      )}
      <Group
        justify="space-between"
        mt="auto"
        pt={8}
        style={{ borderTop: '1px solid var(--hb-border)' }}
      >
        <Text size="xs" c="dimmed" className="num">
          {formatDateTime(c.updatedAt)}
        </Text>
        {actions(c)}
      </Group>
    </Paper>
  )

  const q = search.toLowerCase()
  const filtered = codes.filter(
    (c) =>
      (!q || c.name.toLowerCase().includes(q) || c.code.toLowerCase().includes(q)) &&
      (status === 'all' || (status === 'active') === c.isActive),
  )

  const filter = (value: Status, label: string) => ({
    label,
    value,
    active: status === value,
    onClick: () => setStatus(value),
  })

  return (
    <div>
      <PageHead
        title={t('codes.title')}
        desc={t('codes.count', '{{count}} Codes', { count: filtered.length })}
        actions={
          canCreate ? (
            <Button variant="default" onClick={() => open('new')}>
              <IconPlus size={16} />
              {t('codes.add')}
            </Button>
          ) : undefined
        }
      />

      <DataTable
        breakpoint="wide"
        columns={[
          { key: 'name', header: t('codes.name'), render: (c: Code) => c.name },
          {
            key: 'code',
            header: t('codes.code'),
            render: (c: Code) => (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                <code
                  style={{
                    fontFamily: mono,
                    fontSize: 'var(--mantine-font-size-sm)',
                    background: 'var(--hb-surface-2)',
                    padding: '2px 8px',
                    borderRadius: 4,
                    letterSpacing: visible.has(c.id) ? '0.06em' : '0.15em',
                  }}
                >
                  {shown(c)}
                </code>
                {eye(c, 16)}
              </span>
            ),
          },
          {
            key: 'description',
            header: t('codes.description'),
            render: (c: Code) => (
              <span style={{ color: 'var(--hb-text-2)' }}>{c.description ?? '—'}</span>
            ),
          },
          { key: 'status', header: t('codes.status'), render: statusChip },
          {
            key: 'updatedAt',
            header: t('codes.lastUpdated'),
            render: (c: Code) => (
              <span
                className="num"
                style={{ color: 'var(--hb-text-2)', fontSize: 'var(--mantine-font-size-xs)' }}
              >
                {formatDateTime(c.updatedAt)}
              </span>
            ),
          },
          { key: 'actions', header: t('common.actions'), width: 80, render: actions },
        ]}
        data={filtered}
        loading={isLoading}
        emptyMessage={t('codes.noCodes')}
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder={t('codes.searchPlaceholder', 'Suchen …')}
        filters={[
          filter('all', t('common.all', 'Alle')),
          filter('active', t('codes.active')),
          filter('inactive', t('codes.inactive')),
        ]}
        getRowKey={(c: Code) => String(c.id)}
        renderCard={renderCard}
        viewKey="codes"
      />

      <Modal
        onSubmit={(e) => {
          e?.preventDefault()
          void save()
        }}
        open={editing !== null}
        onClose={() => setEditing(null)}
        title={editing === 'new' ? t('codes.add') : t('codes.edit')}
        subtitle={editing && editing !== 'new' ? editing.name : undefined}
        footer={
          <>
            <Button variant="default" onClick={() => setEditing(null)}>
              {t('common.cancel')}
            </Button>
            <Button variant="filled" type="submit" loading={saving}>
              {t('common.save')}
            </Button>
          </>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Field label={t('codes.name')}>
            <TextInput
              value={form.name}
              error={errors.name}
              onChange={(e) => setForm({ ...form, name: e.currentTarget.value })}
              placeholder={t('codes.namePlaceholder')}
            />
          </Field>
          <Field
            label={t('codes.code')}
            hint={t('codes.lengthHint', 'Mit dem Regler stellst du die Länge des Codes ein')}
          >
            <Slider
              value={length}
              onChange={setLength}
              min={2}
              max={16}
              label={(val) => `${val}`}
              mb="sm"
            />
            <PinInput
              value={form.code}
              onChange={(code) => setForm({ ...form, code })}
              length={length}
              type="alphanumeric"
              mask={false}
              error={!!errors.code}
              aria-label={t('codes.code', 'Code')}
              size="sm"
            />
            {errors.code && (
              <Text size="xs" c="red" mt={4}>
                {errors.code}
              </Text>
            )}
          </Field>
          <Field label={t('codes.description')}>
            <Textarea
              value={form.description ?? ''}
              onChange={(e) => setForm({ ...form, description: e.currentTarget.value })}
              placeholder={t('codes.descriptionPlaceholder')}
              rows={3}
              style={{ resize: 'vertical' }}
            />
          </Field>
          {editing !== 'new' && (
            <Checkbox
              label={t('codes.active')}
              checked={!!form.isActive}
              onChange={(e) => setForm({ ...form, isActive: e.currentTarget.checked })}
            />
          )}
        </div>
      </Modal>

      <ConfirmModal
        open={!!deleteTarget}
        title={t('codes.delete')}
        body={deleteTarget ? t('codes.deleteConfirm', { name: deleteTarget.name }) : undefined}
        onConfirm={remove}
        onClose={() => setDeleteTarget(null)}
      />
    </div>
  )
}
