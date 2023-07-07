import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";

const leaderboards = JSON.parse(fs.readFileSync('data/leaderboards.json').toString());

export async function GET( req: RequestEvent ): Promise<Response> {
  try {
    // TODO: better error handling
    const name = req.url.searchParams.get("name") ?? assert.fail("no name provided");
    const unique = req.url.searchParams.get("unique") === "true";
    if (unique) {
      return json({
        count: await getUniqueCount(name)
      });
    }
    return json({
      count: await getTotalCount(name)
    });
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}

async function getTotalCount(name: string): Promise<number> {
  const leaderboard = leaderboards[name];
  assert(leaderboard !== undefined, "leaderboard name not found");
  let count = 0;
  for (const sheet of leaderboard) {
    // for safety, check if file exists
    assert(fs.existsSync(`data/revs/${sheet.gid}`), "sheet not present");
    count += sheet.end - sheet.start + 1;
  }
  return count;
}

async function getUniqueCount(name: string): Promise<number> {
  const leaderboard = leaderboards[name];
  assert(leaderboard !== undefined, "leaderboard name not found");
  let count = 0;
  for (const sheet of leaderboard) {
    // for safety, check if file exists
    assert(fs.existsSync(`data/revs/${sheet.gid}/unique_revs.json`), "sheet not present");
    // find smallest index that's at least sheet.start and greatest index
    // that's at most sheet.end
    const uniqueRevs = JSON.parse(
      (await fs.promises.readFile(`data/revs/${sheet.gid}/unique_revs.json`))
        .toString()
    );
    let start = 0;
    while (start < uniqueRevs.length && uniqueRevs[start] < sheet.start) {
      start++;
    }
    let end = uniqueRevs.length - 1;
    while (end >= 0 && uniqueRevs[end] > sheet.end) {
      end--;
    }
    count += end - start + 1;
  }
  return count;
}

