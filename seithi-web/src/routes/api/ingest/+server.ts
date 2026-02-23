import { json } from '@sveltejs/kit';

export async function POST({ request, platform }) {
    if (!platform?.env?.DB) {
        return json({ error: 'Database binding not found' }, { status: 500 });
    }

    // 1. Authorization Check
    const authHeader = request.headers.get('Authorization');
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

        // 3. Insert into D1
        const query = `
            INSERT INTO articles (
                id, title, url, domain, content, image_url, published_at,
                objectivity_score, calm_score, depth_score
            ) VALUES (
                ?1, ?2, ?3, ?4, ?5, ?6, ?7,
                ?8, ?9, ?10
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
            article.image_url || null,
            article.published_at || null,
            article.objectivity_score ?? 0.5,
            article.calm_score ?? 0.5,
            article.depth_score ?? 0.5
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
