export type PaginatedResponse<T> = {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type ListResponse<T> = PaginatedResponse<T> | T[]

export const unwrapListResponse = <T>(response: ListResponse<T>) => {
  if (Array.isArray(response))
    return response

  return Array.isArray(response.results) ? response.results : []
}
