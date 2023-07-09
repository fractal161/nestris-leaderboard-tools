import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";

export async function GET(req: RequestEvent): Promise<Response> {
  try {
    const player =
      req.url.searchParams.get("player") ?? assert.fail("player is null");
    const board =
      req.url.searchParams.get("board") ?? assert.fail("leaderboard is null");
    return json([
      [player, "score1"],
      [player, "score2"],
    ]);
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
