import * as fs from "fs";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => {
  const histories = JSON.parse(
    (await fs.promises.readFile('data/sheet_history.json')).toString()
  );
  return {
    gids: Object.keys(histories),
  };
}
