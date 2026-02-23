export interface Article {
    id: string;
    title: string;
    url: string;
    domain: string;
    image_url?: string;
    published_at: string;
    // Single score per axis (0.0 → 1.0)
    objectivity_score: number; // 0 = opinionated, 1 = factual
    calm_score: number;        // 0 = rage-bait, 1 = calm
    depth_score: number;       // 0 = fluff, 1 = deep dive
}

export interface ArticlesResponse {
    articles: Article[];
    total: number;
    limit: number;
    offset: number;
}

export interface FeedbackRequest {
    article_id: string;
    axis: string;
    user_score: number;
}

const API_BASE_URL = '/api';

export async function getArticles(
    limit: number = 20,
    offset: number = 0,
    minObjectivity: number = 0,
    minCalm: number = 0,
    minDepth: number = 0
): Promise<ArticlesResponse> {
    const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
        min_objectivity: minObjectivity.toString(),
        min_calm: minCalm.toString(),
        min_depth: minDepth.toString()
    });

    const response = await fetch(`${API_BASE_URL}/articles?${params}`);
    if (!response.ok) {
        throw new Error('Failed to fetch articles');
    }
    return response.json();
}

export async function submitFeedback(feedback: FeedbackRequest): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedback)
    });

    if (!response.ok) {
        throw new Error('Failed to submit feedback');
    }
}
