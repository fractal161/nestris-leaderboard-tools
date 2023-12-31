import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";
import { parseCsvFile } from "$lib/util";
import { formatTime, formatDay } from "$lib/format";
import type { ProfileChunk } from "$types/client";

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
    const editors: Array<Array<string>> = [];
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
      // update editors
      editors.push(timestamp["editors"]);
    }
    // attempt to fetch existing profiles
    let profiles: { [key: string]: { [key: string]: Array<ProfileChunk> } };
    try {
      profiles = JSON.parse(
        (
          await fs.promises.readFile(`findings/sheets/${sheet}/info/${id}.json`)
        ).toString(),
      );
    } catch (e) {
      profiles = {};
    }
    return json({
      headers: headers.slice(1),
      entries: fields.map((row, i) => {
        return {
          date: dates[i],
          fields: row,
        };
      }),
      editors: editors,
      revs: revs,
      profiles: profiles,
    });
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}

export async function POST(req: RequestEvent): Promise<Response> {
  try {
    // parse arguments
    const { gid, player, profile, info } = await req.request.json();
    const players = JSON.parse(
      (
        await fs.promises.readFile(`findings/sheets/${gid}/players/names.json`)
      ).toString(),
    );
    const pid = players[player];
    try {
      // test if folder exists
      await fs.promises.access(`findings/sheets/${gid}/info`);
    } catch (err) {
      // create folder if it doesn't exist
      await fs.promises.mkdir(`findings/sheets/${gid}/info`);
    }
    // if profile or info is null, this means that the player should be ignored
    if (profile === null || info === null) {
      await fs.promises.writeFile(
        `findings/sheets/${gid}/info/${pid}.json`,
        "{}",
      );
      return new Response("good");
    }
    //
    try {
      // if file already exists, attempt to update it
      const existingProfiles = JSON.parse(
        (
          await fs.promises.readFile(`findings/sheets/${gid}/info/${pid}.json`)
        ).toString(),
      );
      existingProfiles[profile] = info;
      await fs.promises.writeFile(
        `findings/sheets/${gid}/info/${pid}.json`,
        JSON.stringify(existingProfiles, null, 2),
      );
    } catch (err) {
      // otherwise, create it
      const profiles: {
        [key: string]: { [key: number]: Array<ProfileChunk> };
      } = {};
      profiles[profile] = info;
      await fs.promises.writeFile(
        `findings/sheets/${gid}/info/${pid}.json`,
        JSON.stringify(profiles, null, 2),
      );
    }
    return new Response("good");
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
