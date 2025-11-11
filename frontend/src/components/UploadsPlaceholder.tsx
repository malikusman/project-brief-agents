import type { ChangeEvent } from 'react'
import type { DocumentReference } from '../types/brief'

interface UploadsPlaceholderProps {
  documents: DocumentReference[]
  onAdd: (doc: DocumentReference) => void
}

export function UploadsPlaceholder({ documents, onAdd }: UploadsPlaceholderProps) {
  const handleFakeUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    onAdd({ id: crypto.randomUUID(), name: file.name })
  }

  return (
    <div className="uploads-placeholder">
      <label className="upload-label">
        <span>Attach supporting documents (simulated)</span>
        <input type="file" onChange={handleFakeUpload} />
      </label>
      {documents.length > 0 && (
        <ul>
          {documents.map((doc) => (
            <li key={doc.id}>{doc.name}</li>
          ))}
        </ul>
      )}
    </div>
  )
}
