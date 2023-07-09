import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";

export async function GET(req: RequestEvent): Promise<Response> {
  try {
    // TODO: better error handling
    return json(["player1", "player2", "player3"]);
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}