import { useDocuments } from '../hooks/useDocuments'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'
import { format } from 'date-fns'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { FileText, Image, Video, Music, File, Building2, HardDrive, Calendar } from 'lucide-react'

export default function Documents() {
  const { data: documents, isLoading, error } = useDocuments()

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error.message} />
  if (!documents || documents.length === 0) {
    return <EmptyState title="No documents" message="No documents have been uploaded yet." />
  }

  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return 'N/A'
    const kb = bytes / 1024
    if (kb < 1024) return `${kb.toFixed(2)} KB`
    const mb = kb / 1024
    return `${mb.toFixed(2)} MB`
  }

  const getFileIcon = (mimeType: string | null) => {
    if (!mimeType) return { Icon: File, color: 'text-gray-600', bg: 'bg-gray-50' }
    if (mimeType.includes('pdf') || mimeType.includes('text'))
      return { Icon: FileText, color: 'text-blue-600', bg: 'bg-blue-50' }
    if (mimeType.includes('image'))
      return { Icon: Image, color: 'text-green-600', bg: 'bg-green-50' }
    if (mimeType.includes('video'))
      return { Icon: Video, color: 'text-purple-600', bg: 'bg-purple-50' }
    if (mimeType.includes('audio'))
      return { Icon: Music, color: 'text-pink-600', bg: 'bg-pink-50' }
    return { Icon: File, color: 'text-gray-600', bg: 'bg-gray-50' }
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight">Documents</h1>
        <p className="text-gray-500 mt-2">
          Manage uploaded documents for RAG system
        </p>
        <div className="mt-4">
          <Badge variant="secondary" className="text-base px-4 py-1.5">
            {documents.length} {documents.length === 1 ? 'Document' : 'Documents'}
          </Badge>
        </div>
      </div>

      {/* Documents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {documents.map((document) => {
          const { Icon, color, bg } = getFileIcon(document.mime_type)
          return (
            <Card key={document.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start gap-3">
                  <div className={`${bg} p-3 rounded-lg`}>
                    <Icon className={`h-6 w-6 ${color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-sm truncate" title={document.file_name}>
                      {document.file_name}
                    </CardTitle>
                    <CardDescription className="text-xs">ID: {document.id}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* Company */}
                <div className="flex items-center gap-2 text-sm">
                  <Building2 className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700 truncate">{document.companies?.name || 'N/A'}</span>
                </div>

                {/* File Size */}
                <div className="flex items-center gap-2 text-sm">
                  <HardDrive className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-700">{formatFileSize(document.file_size)}</span>
                </div>

                {/* MIME Type */}
                {document.mime_type && (
                  <div>
                    <Badge variant="secondary" className="text-xs font-mono">
                      {document.mime_type}
                    </Badge>
                  </div>
                )}

                {/* Created Date */}
                <div className="pt-3 border-t border-gray-200">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Calendar className="h-3 w-3" />
                    <span>{format(new Date(document.created_at), 'MMM d, yyyy')}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}

