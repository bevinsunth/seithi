export interface Article {
    id: string;
    title: string;
    url: string;
    domain: string;
    published_at: string;
    epistemic_opinion_score: number;
    epistemic_mixed_score: number;
    epistemic_facts_score: number;
    emotive_triggering_score: number;
    emotive_mixed_score: number;
    emotive_calm_score: number;
    density_fluff_score: number;
    density_standard_score: number;
    density_deep_score: number;
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

const API_BASE_URL = 'http://localhost:8080/api';

export async function getArticles(
    limit: number = 20,
    offset: number = 0,
    minFacts: number = 0,
    minCalm: number = 0,
    minDeep: number = 0
): Promise<ArticlesResponse> {
    const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
        min_facts: minFacts.toString(),
        min_calm: minCalm.toString(),
        min_deep: minDeep.toString()
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
