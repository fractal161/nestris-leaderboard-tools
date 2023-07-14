import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";

export async function GET(req: RequestEvent): Promise<Response> {
  try {
    // TODO: better error handling
    const sheet =
      req.url.searchParams.get("sheet") ?? assert.fail("sheet is null");
    const players = JSON.parse(
      (
        await fs.promises.readFile(
          `findings/sheets/${sheet}/players/names.json`,
        )
      ).toString(),
    );
    return json(Object.keys(players));
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
