import { useState, useEffect, useCallback } from 'react'
import { getApplications } from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'
import KanbanColumn from '../components/KanbanColumn'
import ApplicationModal from '../components/ApplicationModal'

const STATUSES = ['applied', 'interviewing', 'offer', 'rejected']

export default function Board() {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [filter, setFilter] = useState('')

  const handleWsMessage = useCallback((data) => {
    if (data.type === 'status_update') {
      setApplications((prev) =>
        prev.map((a) => a.id === data.app_id ? { ...a, status: data.status } : a)
      )
    }
  }, [])

  const { send } = useWebSocket(handleWsMessage)

  useEffect(() => {
    getApplications()
      .then((res) => setApplications(res.data))
      .finally(() => setLoading(false))
  }, [])

  const handleCreated = (app) => setApplications((prev) => [...prev, app])

  const filtered = filter
    ? applications.filter((a) =>
        a.company.toLowerCase().includes(filter.toLowerCase()) ||
        a.role.toLowerCase().includes(filter.toLowerCase())
      )
    : applications

  const byStatus = (status) => filtered.filter((a) => a.status === status)

  return (
    <div style={styles.page}>
      <div style={styles.toolbar}>
        <div style={styles.toolbarLeft}>
          <span style={styles.heading}>job board</span>
          <span style={styles.count}>{applications.length} applications</span>
        </div>
        <div style={styles.toolbarRight}>
          <input
            style={{ width: '200px' }}
            placeholder="filter by company or role..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <button className="primary" onClick={() => setShowModal(true)}>
            + new application
          </button>
        </div>
      </div>

      {loading ? (
        <p style={styles.loading}>loading...</p>
      ) : (
        <div style={styles.board}>
          {STATUSES.map((status) => (
            <KanbanColumn key={status} status={status} applications={byStatus(status)} />
          ))}
        </div>
      )}

      {showModal && (
        <ApplicationModal onClose={() => setShowModal(false)} onCreated={handleCreated} />
      )}
    </div>
  )
}

const styles = {
  page: { display: 'flex', flexDirection: 'column', height: 'calc(100vh - 44px)', overflow: 'hidden' },
  toolbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '14px 24px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-surface)',
  },
  toolbarLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  heading: { fontWeight: 700, fontSize: '13px' },
  count: { color: 'var(--text-muted)', fontSize: '11px', background: 'var(--bg-overlay)', border: '1px solid var(--border)', padding: '2px 8px', borderRadius: 'var(--radius)' },
  toolbarRight: { display: 'flex', alignItems: 'center', gap: '10px' },
  board: { display: 'flex', gap: '16px', padding: '20px 24px', flex: 1, overflowX: 'auto', overflowY: 'hidden', alignItems: 'stretch' },
  loading: { padding: '24px', color: 'var(--text-muted)' },
}
