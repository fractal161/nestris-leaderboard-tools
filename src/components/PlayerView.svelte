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
        <label class="player-option" for={player}>{player} </label>
      {/each}
    </div>
    <button type="button">Confirm</button>
  </div>
  <div class="scores">
    <h3>
      {sheetId}{selectedPlayer === undefined ? "" : ": " + selectedPlayer}
    </h3>
    <div class="scroll-container">
      <ul>
        {#each scoreList as score}
          <li value={score}>{score}</li>
        {/each}
      </ul>
    </div>
  </div>
</div>

<style>
  h3 {
    margin: 4px;
  }
  ul {
    list-style: none;
    text-align: left;
    padding: 0px;
    margin: 0px;
    border-collapse: collapse;
  }
  li {
    padding-left: 5px;
    border-top: 1px solid grey;
    border-bottom: 1px solid grey;
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
    border-top: 1px solid grey;
    overflow: scroll;
    height: 100%;
  }
  .scores {
    border: 1px solid grey;
    flex: 5;
    display: flex;
    flex-direction: column;
  }
  .player-option {
    display: block;
    border: 1px solid grey;
    margin: 0px -1px 0px -1px;
    padding-left: 5px;
  }
  .scroll-container input[type="radio"] {
    position: absolute;
    opacity: 0;
    cursor: pointer;
    height: 0;
    width: 0;
  }
  .player-option:hover {
    background-color: lightgrey;
  }
  .scroll-container input[type="radio"]:checked + label {
    background-color: lightblue;
  }
</style>
