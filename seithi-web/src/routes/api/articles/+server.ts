import { json } from '@sveltejs/kit';

export async function GET({ request, platform }) {
    if (!platform?.env?.DB) {
        return json({ error: 'Database binding not found' }, { status: 500 });
    }

    const url = new URL(request.url);

    let limit = parseInt(url.searchParams.get('limit') || '20', 10);
    if (isNaN(limit) || limit <= 0) limit = 20;
    if (limit > 100) limit = 100;

    let offset = parseInt(url.searchParams.get('offset') || '0', 10);
    if (isNaN(offset) || offset < 0) offset = 0;

    const minObjectivity = parseFloat(url.searchParams.get('min_objectivity') || '0.0');
    const minCalm = parseFloat(url.searchParams.get('min_calm') || '0.0');
    const minDepth = parseFloat(url.searchParams.get('min_depth') || '0.0');

    try {
        const articlesQuery = `
            SELECT
                id, title, url, domain, image_url, published_at,
                objectivity_score, calm_score, depth_score
            FROM articles
            WHERE objectivity_score >= ?1
              AND calm_score        >= ?2
              AND depth_score       >= ?3
            ORDER BY depth_score DESC, calm_score DESC, published_at DESC
            LIMIT ?4 OFFSET ?5
        `;

        const { results: articles } = await platform.env.DB
            .prepare(articlesQuery)
            .bind(minObjectivity, minCalm, minDepth, limit, offset)
            .all();

        const countQuery = `
            SELECT COUNT(*) as total
            FROM articles
            WHERE objectivity_score >= ?1
              AND calm_score        >= ?2
              AND depth_score       >= ?3
        `;

        const totalResult = await platform.env.DB
            .prepare(countQuery)
            .bind(minObjectivity, minCalm, minDepth)
            .first();

        const total = totalResult ? (totalResult.total as number) : 0;

        return json({ articles, total, limit, offset });

    } catch (e: any) {
        console.error("Database error:", e);
        return json({ error: "Failed to fetch articles", details: e.message }, { status: 500 });
    }
}
