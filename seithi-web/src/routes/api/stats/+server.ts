import { json } from '@sveltejs/kit';

export async function GET({ platform }) {
    if (!platform?.env?.DB) {
        return json({ error: 'Database binding not found' }, { status: 500 });
    }

    try {
        const query = `
            SELECT 
                COUNT(*) as total_articles,
                AVG(epistemic_facts_score) as avg_facts_score,
                AVG(emotive_calm_score) as avg_calm_score,
                AVG(density_deep_score) as avg_deep_score
            FROM articles
        `;

        const stats = await platform.env.DB
            .prepare(query)
            .first();

        // Handle case where table might be empty
        if (!stats) {
            return json({
                total_articles: 0,
                avg_facts_score: 0,
                avg_calm_score: 0,
                avg_deep_score: 0
            });
        }

        return json({
            total_articles: stats.total_articles || 0,
            avg_facts_score: stats.avg_facts_score || 0,
            avg_calm_score: stats.avg_calm_score || 0,
            avg_deep_score: stats.avg_deep_score || 0
        });

    } catch (e: any) {
        console.error("Database error:", e);
        return json({ error: "Failed to fetch stats", details: e.message }, { status: 500 });
    }
}
