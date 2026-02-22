import { json } from '@sveltejs/kit';

export async function POST({ request, platform }) {
    if (!platform?.env?.DB) {
        return json({ error: 'Database binding not found' }, { status: 500 });
    }

    // 1. Authorization Check
    const authHeader = request.headers.get('Authorization');
    // Ensure we have an env variable for the secret, fallback for local dev if needed
    const expectedSecret = platform.env.INGEST_SECRET || 'dev-secret-key-123';

    if (!authHeader || authHeader !== `Bearer ${expectedSecret}`) {
        return json({ error: 'Unauthorized' }, { status: 401 });
    }

    try {
        const article = await request.json();

        // 2. Validate essential fields
        if (!article.id || !article.title || !article.url || !article.domain) {
            return json({ error: 'Missing core article fields (id, title, url, domain)' }, { status: 400 });
        }

        // 3. Insert into D1 (ON CONFLICT DO NOTHING equivalent in SQLite)
        const query = `
            INSERT INTO articles (
                id, title, url, domain, content, published_at,
                epistemic_opinion_score, epistemic_mixed_score, epistemic_facts_score,
                emotive_triggering_score, emotive_mixed_score, emotive_calm_score,
                density_fluff_score, density_standard_score, density_deep_score
            ) VALUES (
                ?1, ?2, ?3, ?4, ?5, ?6,
                ?7, ?8, ?9,
                ?10, ?11, ?12,
                ?13, ?14, ?15
            )
            ON CONFLICT(url) DO NOTHING
            RETURNING id;
        `;

        const stmt = platform.env.DB.prepare(query).bind(
            article.id,
            article.title,
            article.url,
            article.domain,
            article.content || null,
            article.published_at || null,
            article.epistemic_opinion_score ?? 0.333,
            article.epistemic_mixed_score ?? 0.333,
            article.epistemic_facts_score ?? 0.334,
            article.emotive_triggering_score ?? 0.333,
            article.emotive_mixed_score ?? 0.333,
            article.emotive_calm_score ?? 0.334,
            article.density_fluff_score ?? 0.333,
            article.density_standard_score ?? 0.333,
            article.density_deep_score ?? 0.334
        );

        const result = await stmt.first();

        // If result is null, the DO NOTHING clause was triggered (conflict)
        if (!result) {
            return json({ status: 'ignored', message: 'Article URL already exists' }, { status: 200 });
        }

        return json({ status: 'success', id: result.id }, { status: 201 });

    } catch (e: any) {
        console.error("Database error during ingestion:", e);
        return json({ error: "Failed to ingest article", details: e.message }, { status: 500 });
    }
}
