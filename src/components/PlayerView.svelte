<script lang="ts">
  import { onMount } from "svelte";
  export let sheetId: string;
  export let selectedPlayer: string | undefined = undefined;
  // any future state that should be saved upon context switch should be
  // exported as a prop here, so the root page can bind to it.
  let playerList: Array<string> = [];
  let scoreList: Array<Array<string>> = [[]];
  let mounted = false;
  const fetchPlayerScores = async (
    selectedPlayer: string | undefined,
  ): Promise<void> => {
    if (!mounted) return;
    if (selectedPlayer === undefined) return;
    const scoreFetch = await fetch(
      "/player?" +
        new URLSearchParams({
          player: selectedPlayer,
          sheet: sheetId,
        }),
      {
        method: "GET",
        headers: {
          "Content-type": "application/json",
        },
      },
    );
    if (scoreFetch.status !== 200) {
      throw Error("error fetching player scores");
    }
    scoreList = await scoreFetch.json();
  };
  const fetchPlayerList = async (sheetId: string): Promise<void> => {
    if (!mounted) return;
    if (sheetId === undefined) return;
    // fetch list of players
    const playerListFetch = await fetch(
      "/player/all?" +
        new URLSearchParams({
          sheet: sheetId,
        }),
      {
        method: "GET",
        headers: {
          "Content-type": "application/json",
        },
      },
    );
    if (playerListFetch.status !== 200) {
      throw Error("error fetching player list");
    }
    playerList = await playerListFetch.json();
  };
  onMount(async () => {
    mounted = true;
    console.log("PlayerView mounted");
    if (sheetId !== undefined) await fetchPlayerList(sheetId);
    if (selectedPlayer !== undefined) await fetchPlayerScores(selectedPlayer);
  });
  $: fetchPlayerList(sheetId);
  $: fetchPlayerScores(selectedPlayer);
</script>

<div class="main">
  <div class="player-menu">
    <h3>Players</h3>
    <div class="scroll-container">
      {#each playerList as player}
        <input
          type="radio"
          bind:group={selectedPlayer}
          name="players"
          id={player}
          value={player}
        />
        <label class="player-option" for={player}>{player}</label>
      {/each}
    </div>
    <button type="button">Confirm</button>
  </div>
  <div class="scores">
    <h3>
      {sheetId || "waiting for player list..."}{selectedPlayer === undefined
        ? ""
        : ": " + selectedPlayer}
    </h3>
    <div class="scroll-container">
      <table>
        <thead>
          <tr>
            {#each scoreList[0] as cell}
              <th role="cell" tabindex="-1">
                {cell}
              </th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each scoreList.slice(1) as row}
            <tr>
              {#each row as cell}
                <td>
                  {cell}
                </td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>

<style>
  h3 {
    margin: 4px;
  }
  .main {
    display: flex;
    flex-direction: row;
    height: 100%;
  }
  .player-menu {
    border: 1px solid grey;
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  .scroll-container {
    position: relative;
    border-top: 1px solid grey;
    overflow: scroll;
    height: 100%;
    width: 100%;
  }
  .scores {
    border: 1px solid grey;
    display: flex;
    flex-direction: column;
    flex: 5;
    min-width: 0px;
  }
  .player-option {
    display: block;
    border: 1px solid grey;
    border-left-width: 0px;
    border-right-width: 0px;
    margin: 0px;
    padding-left: 5px;
  }
  .scroll-container input[type="radio"] {
    display: none;
  }
  .player-option:hover {
    background-color: lightgrey;
  }
  .scroll-container input[type="radio"]:checked + label {
    background-color: lightblue;
  }
  table {
    border-collapse: collapse;
    font-size: 10px;
  }
  td,
  th {
    box-sizing: border-box;
    border: 1px solid gray;
    white-space: nowrap;
    height: 12px; /* kinda bad but works for now */
  }
  td {
    padding-top: 3px;
    padding-bottom: 3px;
    height: 18px; /* kinda bad but works for now */
  }
</style>
