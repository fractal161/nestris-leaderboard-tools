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
    const confirmed: Array<string> = [];
    for (const player of players) {
      // check if file already exists
      const id = playerMap[player];
      try {
        await fs.promises.access(`findings/sheets/${sheet}/info/${id}.json`);
        // now, open the file and check if it's empty
        const profiles = JSON.parse(
          (
            await fs.promises.readFile(
              `findings/sheets/${sheet}/info/${id}.json`,
            )
          ).toString(),
        );
        if (Object.keys(profiles).length === 0) {
          confirmed.push("ignored");
        } else {
          confirmed.push("confirmed");
        }
      } catch (err) {
        confirmed.push("none");
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
