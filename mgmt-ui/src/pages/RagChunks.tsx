import { useRagChunks } from '../hooks/useRagChunks'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'
import { format } from 'date-fns'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Puzzle, FileText, Building2, CheckCircle2, Clock, Calendar } from 'lucide-react'

export default function RagChunks() {
  const { data: chunks, isLoading, error } = useRagChunks()

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error.message} />
  if (!chunks || chunks.length === 0) {
    return <EmptyState title="No RAG chunks" message="No RAG chunks have been created yet." />
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight">RAG Chunks</h1>
        <p className="text-gray-500 mt-2">
          Vector embeddings for document retrieval
        </p>
        <div className="mt-4">
          <Badge variant="secondary" className="text-base px-4 py-1.5">
            {chunks.length} {chunks.length === 1 ? 'Chunk' : 'Chunks'}
          </Badge>
        </div>
      </div>

      {/* Chunks Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {chunks.map((chunk) => (
          <Card key={chunk.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="bg-pink-50 p-2 rounded-lg">
                    <Puzzle className="h-5 w-5 text-pink-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-base">Chunk #{chunk.chunk_index}</CardTitle>
                    <CardDescription>ID: {chunk.id}</CardDescription>
                  </div>
                </div>
                {chunk.embedding ? (
                  <Badge variant="default" className="bg-green-600 hover:bg-green-700">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Embedded
                  </Badge>
                ) : (
                  <Badge variant="secondary">
                    <Clock className="h-3 w-3 mr-1" />
                    Pending
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Chunk Text */}
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Content</p>
                <p className="text-sm text-gray-700 line-clamp-3">
                  {chunk.chunk_text}
                </p>
              </div>

              {/* Document */}
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Document</p>
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <p className="text-sm text-gray-900 truncate">
                    {chunk.documents?.file_name || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Company */}
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Company</p>
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-gray-400" />
                  <p className="text-sm text-gray-900">
                    {chunk.documents?.companies?.name || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Created Date */}
              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Calendar className="h-3 w-3" />
                  <span>{format(new Date(chunk.created_at), 'MMM d, yyyy h:mm a')}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

