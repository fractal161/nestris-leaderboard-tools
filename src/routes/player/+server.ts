import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";
import { parseCsvFile } from "$lib/util";

export async function GET(req: RequestEvent): Promise<Response> {
  try {
    const player =
      req.url.searchParams.get("player") ?? assert.fail("player is null");
    const sheet =
      req.url.searchParams.get("sheet") ?? assert.fail("sheet is null");
    const players = JSON.parse(
      (await fs.promises.readFile(`findings/sheets/${sheet}/players/names.json`)).toString(),
    );
    const id = players[player];
    const history = await parseCsvFile(`findings/sheets/${sheet}/players/${id}.csv`);
    return json(history);
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
