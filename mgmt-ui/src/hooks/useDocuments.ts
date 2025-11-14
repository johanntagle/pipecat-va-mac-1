import { useQuery } from '@tanstack/react-query'
import { supabase } from '../lib/supabase'

export function useDocuments() {
  return useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('documents')
        .select(`
          *,
          companies (
            id,
            name
          )
        `)
        .order('created_at', { ascending: false })

      if (error) throw error
      return data
    },
  })
}

