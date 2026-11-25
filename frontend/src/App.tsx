import { useEffect, useState } from 'react'

const apiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
type Connection = 'checking' | 'ready' | 'unavailable'

export default function App() {
  const [connection, setConnection] = useState<Connection>('checking')

  useEffect(() => {
    let active = true
    let controller: AbortController | undefined
    async function check() {
      controller = new AbortController()
      const timeout = window.setTimeout(() => controller?.abort(), 5000)
      try {
        const response = await fetch(`${apiUrl}/api/v1/health/ready`, { signal: controller.signal })
        const body: unknown = await response.json()
        const ready = response.ok && typeof body === 'object' && body !== null
          && 'status' in body && body.status === 'ready'
        if (active) setConnection(ready ? 'ready' : 'unavailable')
      } catch {
        if (active) setConnection('unavailable')
      } finally {
        window.clearTimeout(timeout)
      }
    }
    void check()
    const interval = window.setInterval(() => void check(), 10000)
    return () => { active = false; controller?.abort(); window.clearInterval(interval) }
  }, [])

  return (
    <main>
      <span className="label">PHASE 0 · FONDATIONS</span>
      <h1>CareerMatch AI<span className="accent">.</span></h1>
      <p className="subtitle">Multi-Agent Career Intelligence &amp; Skill Gap Analysis Platform</p>
      <section aria-labelledby="connection-title">
        <h2 id="connection-title">Connexion à la plateforme</h2>
        <p role="status" className={`status ${connection}`}>
          {connection === 'checking' && 'Vérification de la connexion…'}
          {connection === 'ready' && 'Backend connecté et prêt.'}
          {connection === 'unavailable' && 'Backend indisponible. Vérifiez son démarrage et l’URL de l’API.'}
        </p>
        <p className="note">Le statut est actualisé toutes les 10 secondes.</p>
      </section>
      <p className="note">Les fonctionnalités d’analyse de CV seront ajoutées lors des prochaines phases.</p>
    </main>
  )
}

