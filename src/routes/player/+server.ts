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
    const headers = history[0];
    assert(headers !== undefined);
    assert(headers[0] == "Rev");
    const revs = history.slice(1).map((row) => parseInt(row[0]));
    const fields = history.slice(1).map((row) => row.slice(1));
    const dates: Array<[string, string]> = [];
    let lastDay: string | undefined = undefined;
    for (const rev of revs) {
      const timestamp = timestamps[rev];
      assert(timestamp !== undefined);
      // get day and time
      const time = formatTime(timestamp["time"]);
      const day = formatDay(timestamp["time"]);
      if (lastDay === day) {
        dates.push(["", time]);
      } else {
        dates.push([day, time]);
        lastDay = day;
      }
    }
    return json({
      headers: headers.slice(1),
      entries: fields.map((row, i) => {
        return {
          date: dates[i],
          fields: row,
        };
      }),
      revs: revs,
    });
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
