import { json } from '@sveltejs/kit';

export async function GET({ request, platform }) {
    if (!platform?.env?.DB) {
        return json({ error: 'Database binding not found' }, { status: 500 });
    }

    const url = new URL(request.url);

    // Parse query parameters matching the old Go backend
    let limit = parseInt(url.searchParams.get('limit') || '20', 10);
    if (isNaN(limit) || limit <= 0) limit = 20;
    if (limit > 100) limit = 100;

    let offset = parseInt(url.searchParams.get('offset') || '0', 10);
    if (isNaN(offset) || offset < 0) offset = 0;

    const minFacts = parseFloat(url.searchParams.get('min_facts') || '0.0');
    const minCalm = parseFloat(url.searchParams.get('min_calm') || '0.0');
    const minDeep = parseFloat(url.searchParams.get('min_deep') || '0.0');

    try {
        // Query to fetch articles
        const articlesQuery = `
            SELECT 
                id, title, url, domain, published_at,
                epistemic_opinion_score, epistemic_mixed_score, epistemic_facts_score,
                emotive_triggering_score, emotive_mixed_score, emotive_calm_score,
                density_fluff_score, density_standard_score, density_deep_score
            FROM articles
            WHERE epistemic_facts_score >= ?1
              AND emotive_calm_score >= ?2
              AND density_deep_score >= ?3
            ORDER BY density_deep_score DESC, emotive_calm_score DESC, published_at DESC
            LIMIT ?4 OFFSET ?5
        `;

        const { results: articles } = await platform.env.DB
            .prepare(articlesQuery)
            .bind(minFacts, minCalm, minDeep, limit, offset)
            .all();

        // Query to fetch total count
        const countQuery = `
            SELECT COUNT(*) as total
            FROM articles
            WHERE epistemic_facts_score >= ?1
              AND emotive_calm_score >= ?2
              AND density_deep_score >= ?3
        `;

        const totalResult = await platform.env.DB
            .prepare(countQuery)
            .bind(minFacts, minCalm, minDeep)
            .first();

        const total = totalResult ? (totalResult.total as number) : 0;

        return json({
            articles: articles,
            total,
            limit,
            offset
        });

    } catch (e: any) {
        console.error("Database error:", e);
        return json({ error: "Failed to fetch articles", details: e.message }, { status: 500 });
    }
}
