import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";

export async function GET(req: RequestEvent): Promise<Response> {
  try {
    const player = req.url.searchParams.get("player") ?? assert.fail("player is null");
    return json([player, "no data yet!"]);
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
