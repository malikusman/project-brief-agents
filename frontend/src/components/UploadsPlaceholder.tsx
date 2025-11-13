import { useState, type ChangeEvent } from 'react'
import type { DocumentReference } from '../types/brief'

interface UploadsPlaceholderProps {
  documents: DocumentReference[]
  onUpload: (file: File) => Promise<void>
}

export function UploadsPlaceholder({ documents, onUpload }: UploadsPlaceholderProps) {
  const [isUploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      await onUpload(file)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  return (
    <div className="uploads-placeholder">
      <label className="upload-label">
        <span>Attach supporting documents</span>
        <input type="file" onChange={handleUpload} disabled={isUploading} />
      </label>
      {isUploading && <span className="loading">Uploading...</span>}
      {error && <span className="error">{error}</span>}
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
