import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";
import { getSheetRev } from "$lib/sheet";

const leaderboards = JSON.parse(
  fs.readFileSync("data/leaderboards.json").toString(),
);

export async function GET(req: RequestEvent): Promise<Response> {
  try {
    // TODO: better error handling
    const name =
      req.url.searchParams.get("name") ?? assert.fail("name is null");
    const index =
      req.url.searchParams.get("index") ?? assert.fail("index is null");
    const unique = req.url.searchParams.get("unique") === "true";
    let indexNum = parseInt(index);
    const leaderboard = leaderboards[name];
    assert(leaderboard !== undefined, "leaderboard name not found");
    if (unique) {
      let rev = 0;
      let id: string | undefined = undefined;
      for (const sheet of leaderboard) {
        // loop through unique_revs to find rev number and id
        const uniqueRevs = JSON.parse(
          (
            await fs.promises.readFile(
              `data/revs/${sheet.gid}/unique_revs.json`,
            )
          ).toString(),
        );
        let start = 0;
        while (start < uniqueRevs.length && uniqueRevs[start] < sheet.start) {
          start++;
        }
        let end = uniqueRevs.length - 1;
        while (end >= 0 && uniqueRevs[end] > sheet.end) {
          end--;
        }
        if (indexNum < end - start + 1) {
          rev = uniqueRevs[start + indexNum];
          id = sheet.gid;
          break;
        }
        indexNum -= end - start + 1;
      }
      if (id === undefined) throw Error("id not found");
      return json(await getSheetRev(id, rev));
    }
    let rev = 0;
    let id: string | undefined = undefined;
    for (const sheet of leaderboard) {
      if (indexNum < sheet.end - sheet.start + 1) {
        rev = sheet.start + indexNum;
        id = sheet.gid;
        break;
      }
      indexNum -= sheet.end - sheet.start + 1;
    }
    if (id === undefined) throw Error("id not found");
    return json(await getSheetRev(id, rev));
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
