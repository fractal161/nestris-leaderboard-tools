import * as fs from "fs";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => {
  const gids = (await fs.promises.readdir('data/revs', { withFileTypes: true }))
    .filter((file) => file.isDirectory())
    .map((dir) => dir.name);
  const allHistories = JSON.parse(
    (await fs.promises.readFile('data/sheet_history.json')).toString()
  );
  const allBoards = JSON.parse(
    (await fs.promises.readFile(`data/leaderboards.json`)).toString()
  );
  return {
    gids: gids,
    histories: allHistories,
    boards: allBoards,
  };
}
