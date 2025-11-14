export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      companies: {
        Row: {
          id: number
          name: string
          openai_api_key: string | null
          system_prompt: string | null
          rag_system_instructions: string | null
          llm_model: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          name: string
          openai_api_key?: string | null
          system_prompt?: string | null
          rag_system_instructions?: string | null
          llm_model?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          name?: string
          openai_api_key?: string | null
          system_prompt?: string | null
          rag_system_instructions?: string | null
          llm_model?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      calls: {
        Row: {
          id: number
          company_id: number
          start_time: string
          end_time: string | null
          duration_seconds: number | null
          summary: string | null
          created_at: string
        }
        Insert: {
          id?: number
          company_id: number
          start_time?: string
          end_time?: string | null
          duration_seconds?: number | null
          summary?: string | null
          created_at?: string
        }
        Update: {
          id?: number
          company_id?: number
          start_time?: string
          end_time?: string | null
          duration_seconds?: number | null
          summary?: string | null
          created_at?: string
        }
      }
      call_details: {
        Row: {
          id: number
          call_id: number
          speaker: string
          message: string
          timestamp: string
          created_at: string
        }
        Insert: {
          id?: number
          call_id: number
          speaker: string
          message: string
          timestamp?: string
          created_at?: string
        }
        Update: {
          id?: number
          call_id?: number
          speaker?: string
          message?: string
          timestamp?: string
          created_at?: string
        }
      }
      appointments: {
        Row: {
          id: number
          company_id: number
          call_id: number | null
          caller_name: string
          caller_phone: string | null
          caller_email: string | null
          appointment_time: string
          status: string
          notes: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          company_id: number
          call_id?: number | null
          caller_name: string
          caller_phone?: string | null
          caller_email?: string | null
          appointment_time: string
          status?: string
          notes?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          company_id?: number
          call_id?: number | null
          caller_name?: string
          caller_phone?: string | null
          caller_email?: string | null
          appointment_time?: string
          status?: string
          notes?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      documents: {
        Row: {
          id: number
          company_id: number
          file_name: string
          file_path: string
          file_size: number | null
          mime_type: string | null
          created_at: string
        }
        Insert: {
          id?: number
          company_id: number
          file_name: string
          file_path: string
          file_size?: number | null
          mime_type?: string | null
          created_at?: string
        }
        Update: {
          id?: number
          company_id?: number
          file_name?: string
          file_path?: string
          file_size?: number | null
          mime_type?: string | null
          created_at?: string
        }
      }
      rag_chunks: {
        Row: {
          id: number
          document_id: number
          chunk_index: number
          chunk_text: string
          embedding: number[] | null
          metadata: Json | null
          created_at: string
        }
        Insert: {
          id?: number
          document_id: number
          chunk_index: number
          chunk_text: string
          embedding?: number[] | null
          metadata?: Json | null
          created_at?: string
        }
        Update: {
          id?: number
          document_id?: number
          chunk_index?: number
          chunk_text?: string
          embedding?: number[] | null
          metadata?: Json | null
          created_at?: string
        }
      }
    }
  }
}
