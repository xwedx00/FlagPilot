export async function ingestFile(url: string, filename: string, userId?: string) {
    const response = await fetch("/api/v1/rag/ingest", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            url,
            filename,
            user_id: userId || "anonymous"
        }),
    });

    if (!response.ok) {
        throw new Error("Failed to ingest file");
    }

    return response.json();
}
