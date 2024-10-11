export type ResponseSources = {
    text: string;
    doc_id: string;
    start: number;
    end: number;
    similarity: number;
  };
  
  export type QueryResponse = {
    text: string;
    sources: ResponseSources[];
  };
  
  const queryIndex = async (query: string): Promise<QueryResponse> => {
    const queryURL = `/api/query?text=${encodeURIComponent(query)}`;
    console.log("[",queryURL,"]")
  
    const response = await fetch(queryURL, { mode: 'cors' });
    if (!response.ok) {
      return { text: 'Error in query', sources: [] };
    }
  
    const queryResponse = (await response.json()) as QueryResponse;
  
    return queryResponse;
  };
  
  export default queryIndex;