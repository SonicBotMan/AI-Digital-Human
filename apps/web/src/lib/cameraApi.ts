const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export interface CameraAnalysisResult {
  face_detection: {
    faces_found: number;
    identified: Array<{
      user_id: string;
      name: string;
      confidence: number;
    }>;
  };
  visual_analysis: Record<string, unknown>;
  timestamp: string;
}

interface AnalyzeFrameResponse {
  success: boolean;
  message: string;
  data: CameraAnalysisResult;
}

let pendingRequest: Promise<AnalyzeFrameResponse | null> | null = null;

export async function analyzeFrame(
  base64Image: string,
  options: {
    userId?: string;
    conversationId?: string;
    metadata?: Record<string, unknown>;
  } = {}
): Promise<CameraAnalysisResult | null> {
  if (pendingRequest) {
    return null;
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const requestPromise = fetch(`${API_BASE_URL}/camera/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image: base64Image,
        user_id: options.userId ?? null,
        conversation_id: options.conversationId ?? null,
        metadata: options.metadata ?? {
          capture_timestamp: new Date().toISOString(),
        },
      }),
      signal: controller.signal,
    });

    pendingRequest = requestPromise
      .then(async (response) => {
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.detail ?? `HTTP ${response.status}`);
        }
        
        const data: AnalyzeFrameResponse = await response.json();
        return data;
      })
      .finally(() => {
        pendingRequest = null;
      });

    const result = await pendingRequest;
    
    if (result?.success && result.data) {
      return result.data;
    }
    
    return null;
  } catch (error) {
    clearTimeout(timeoutId);
    pendingRequest = null;
    return null;
  }
}

export function cancelPendingRequests(): void {
  pendingRequest = null;
}