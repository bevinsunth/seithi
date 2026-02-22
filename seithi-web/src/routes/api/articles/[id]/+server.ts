import { json } from '@sveltejs/kit';

export async function GET({ params, platform }) {
    if (!platform?.env?.DB) {
        return json({ error: 'Database binding not found' }, { status: 500 });
    }

    const { id } = params;

    try {
        const query = `
            SELECT 
                id, title, url, domain, published_at,
                epistemic_opinion_score, epistemic_mixed_score, epistemic_facts_score,
                emotive_triggering_score, emotive_mixed_score, emotive_calm_score,
                density_fluff_score, density_standard_score, density_deep_score
            FROM articles
            WHERE id = ?1
        `;

        const article = await platform.env.DB
            .prepare(query)
            .bind(id)
            .first();

        if (!article) {
            return json({ error: 'Article not found' }, { status: 404 });
        }

        return json(article);

    } catch (e: any) {
        console.error("Database error:", e);
        return json({ error: "Failed to fetch article", details: e.message }, { status: 500 });
    }
}
