import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";

export async function GET(req: RequestEvent): Promise<Response> {
  try {
    // TODO: better error handling
    const sheet =
      req.url.searchParams.get("sheet") ?? assert.fail("sheet is null");
    const playerMap = JSON.parse(
      (
        await fs.promises.readFile(
          `findings/sheets/${sheet}/players/names.json`,
        )
      ).toString(),
    );
    const players = Object.keys(playerMap);
    const confirmed: Array<boolean> = [];
    for (const player of players) {
      // check if file already exists
      const id = playerMap[player];
      try {
        await fs.promises.access(`findings/sheets/${sheet}/info/${id}.json`);
        // if here, then the file does exist
        confirmed.push(true);
      } catch (err) {
        confirmed.push(false);
      }
    }
    return json({
      players: players,
      confirmed: confirmed,
    });
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
