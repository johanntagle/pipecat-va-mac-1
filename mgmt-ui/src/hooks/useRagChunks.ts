import { useQuery } from '@tanstack/react-query'
import { supabase } from '../lib/supabase'

export function useRagChunks() {
  return useQuery({
    queryKey: ['rag-chunks'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('rag_chunks')
        .select(`
          *,
          documents (
            id,
            file_name,
            company_id,
            companies (
              id,
              name
            )
          )
        `)
        .order('created_at', { ascending: false })

      if (error) throw error
      return data
    },
  })
}

