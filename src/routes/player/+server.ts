import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";
import { parseCsvFile } from "$lib/util";
import { formatTime, formatDay } from "$lib/format";

const timestamps = JSON.parse(
  fs.readFileSync("data/timestamps.json").toString(),
);

export async function GET(req: RequestEvent): Promise<Response> {
  try {
    const player =
      req.url.searchParams.get("player") ?? assert.fail("player is null");
    const sheet =
      req.url.searchParams.get("sheet") ?? assert.fail("sheet is null");
    const players = JSON.parse(
      (
        await fs.promises.readFile(
          `findings/sheets/${sheet}/players/names.json`,
        )
      ).toString(),
    );
    const id = players[player];
    const history = await parseCsvFile(
      `findings/sheets/${sheet}/players/${id}.csv`,
    );
    // replace each revision by relevant time
    const header = history[0];
    assert(header !== undefined);
    assert(header[0] == "Rev");
    const new_history = [];
    new_history.push(["Day", "Time"].concat(header.slice(1)));
    let lastDay: string | undefined = undefined;
    for (const row of history.slice(1)) {
      const rev = row[0];
      assert(rev !== undefined);
      const timestamp = timestamps[rev];
      assert(timestamp !== undefined);
      const new_row = row.slice(1);
      // get day and time
      const time = formatTime(timestamp["time"]);
      const day = formatDay(timestamp["time"]);
      new_row.unshift(time);
      if (lastDay === day) {
        new_row.unshift("");
      } else {
        new_row.unshift(day);
        lastDay = day;
      }
      new_history.push(new_row);
    }
    return json(new_history);
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
