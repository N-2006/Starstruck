
const API_BASE = "http://localhost:8000";

export interface UserInput {
    spotify_username?: string;
    letterboxd_username?: string;
    github_username?: string;
    book_titles?: string[];
    location?: string;
}

export interface MatchRequest {
    user_a: UserInput;
    user_b: UserInput;
    include_venue: boolean;
}

export interface CoachingResponse {
    venues: any[];
    coaching_a: any;
    coaching_b: any;
    cross_ref: any;
}

export const StarstruckAPI = {
    async runPipeline(request: MatchRequest): Promise<CoachingResponse> {
        const resp = await fetch(`${API_BASE}/run`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(request),
        });
        if (!resp.ok) throw new Error("Failed to run pipeline");
        return resp.json();
    },

    async getProfile(request: UserInput): Promise<any> {
        const resp = await fetch(`${API_BASE}/profile`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(request),
        });
        if (!resp.ok) throw new Error("Failed to get profile");
        return resp.json();
    },

    streamPipeline() {
        // Implementation using EventSource if needed
        console.log("Streaming not implemented yet");
    }
};
