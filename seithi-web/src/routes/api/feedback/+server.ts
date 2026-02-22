import { json } from '@sveltejs/kit';

export async function POST({ request, platform }) {
    if (!platform?.env?.DB) {
        return json({ error: 'Database binding not found' }, { status: 500 });
    }

    try {
        const body = await request.json();
        const { article_id, axis, user_score } = body;

        // Basic validation
        if (!article_id || !axis) {
            return json({ error: 'Missing required fields' }, { status: 400 });
        }

        if (user_score < 0 || user_score > 2) {
            return json({ error: 'user_score must be 0, 1, or 2' }, { status: 400 });
        }

        // Insert feedback into D1
        const query = `
            INSERT INTO feedback_log (article_id, axis, user_score)
            VALUES (?1, ?2, ?3)
        `;

        await platform.env.DB
            .prepare(query)
            .bind(article_id, axis, user_score)
            .run();

        return json({ status: 'success' }, { status: 201 });

    } catch (e: any) {
        console.error("Database error:", e);
        return json({ error: "Failed to save feedback", details: e.message }, { status: 500 });
    }
}
