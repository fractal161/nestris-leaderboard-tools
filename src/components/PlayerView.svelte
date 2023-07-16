<script lang="ts">
  import { onMount } from "svelte";
  export let sheetId: string;
  export let selectedPlayer: string | undefined = undefined;
  // any future state that should be saved upon context switch should be
  // exported as a prop here, so the root page can bind to it.
  let playerList: Array<string> = [];
  let activeProfiles: Array<string> = [];
  let selectedProfile: string | undefined = undefined;
  let scoreInfo: {
    headers: Array<string>;
    entries: Array<{
      date: [string, string];
      fields: Array<string>;
    }>;
    editors: Array<Array<string>>;
    revs: Array<number>;
  } = {
    headers: [],
    entries: [],
    revs: [],
    editors: [],
  };
  let rowStates: Array<string> = [];
  let fieldStates: Array<Array<string>> = [];
  let mounted = false;
  let editorString = "";
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
    scoreInfo = await scoreFetch.json();
    rowStates = scoreInfo.entries.map(() => "none");
    fieldStates = scoreInfo.entries.map((row) => row.fields.map(() => "none"));
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
  const handleRowClick = (row: number): void => {
    // toggle entire row, cycle between "none" and "edit"
    if (rowStates[row] === "none") {
      rowStates[row] = "edit";
      for (let i = 0; i < fieldStates[row].length; i++) {
        fieldStates[row][i] = "edit";
      }
    } else {
      rowStates[row] = "none";
      for (let i = 0; i < fieldStates[row].length; i++) {
        fieldStates[row][i] = "none";
      }
    }
  };
  const handleFieldClick = (row: number, col: number): void => {
    // don't do anything if date is marked
    if (rowStates[row] === "edit") return;
    // toggle cell, cycle between "none", "edit", and "patch"
    if (fieldStates[row]?.[col] === "none") {
      fieldStates[row][col] = "edit";
    } else if (fieldStates[row]?.[col] === "edit") {
      fieldStates[row][col] = "patch";
    } else {
      fieldStates[row][col] = "none";
    }
  };
  const addProfile = (e: KeyboardEvent): void => {
    const input = e.target;
    if (
      input instanceof HTMLInputElement &&
      e.key === "Enter" &&
      !activeProfiles.includes(input.value)
    ) {
      if (activeProfiles.length === 0) selectedProfile = input.value;
      activeProfiles = [...activeProfiles, input.value];
      input.value = "";
    }
  };
  const setEditorString = (i: number): void => {
    const editors = scoreInfo.editors[i];
    editorString = editors.join(", ");
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
    <br />
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
  </div>
  <div class="scores">
    <h3>
      {sheetId || "waiting for player list..."}{selectedPlayer === undefined
        ? ""
        : ": " + selectedPlayer}
    </h3>
    <p>Editors: {editorString}</p>
    <div class="scroll-container">
      <table>
        <thead>
          <tr>
            {#if scoreInfo.entries.length > 0}
              <th>Day</th>
              <th>Time</th>
            {/if}
            {#each scoreInfo.headers as header}
              <th>
                {header}
              </th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each scoreInfo.entries as row, i}
            <tr>
              <td
                class:new-day={row.date[0] != ""}
                class:edit={rowStates[i] === "edit"}
                on:click={() => handleRowClick(i)}
                on:mouseenter={() => setEditorString(i)}
                ><div>{row.date[0]}</div></td
              >
              <td
                class:new-day={row.date[0] != ""}
                class:edit={rowStates[i] === "edit"}
                on:click={() => handleRowClick(i)}
                on:mouseenter={() => setEditorString(i)}
                ><div>{row.date[1]}</div></td
              >
              {#each row.fields as cell, j}
                <td
                  class="field"
                  class:new-day={row.date[0] != ""}
                  class:diff={i > 0 &&
                    scoreInfo.entries[i - 1].fields[j] !== cell}
                  class:edit={fieldStates[i][j] === "edit"}
                  class:patch={fieldStates[i][j] === "patch"}
                  on:click={() => handleFieldClick(i, j)}
                  on:mouseenter={() => setEditorString(i)}
                >
                  <div>{cell}</div>
                </td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    <div class="bottom">
      <div class="add-profile-box">
        Add:
        <input
          type="text"
          id="new-profile"
          name="new-profile"
          on:keypress={addProfile}
        />
      </div>
      <div class="profile-box">
        Profile:
        <select class="profiles" bind:value={selectedProfile}>
          {#each activeProfiles as prof}
            <option value={prof}>
              {prof}
            </option>
          {/each}
        </select>
      </div>
      <button type="button">Confirm</button>
    </div>
  </div>
</div>

<style>
  h3 {
    margin: 4px;
  }
  h3 + p {
    margin: 4px;
    margin-top: 0px;
  }
  br {
    margin-top: 17px;
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
    padding-bottom: 28px;
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
    font-size: 12px;
  }
  td,
  th {
    box-sizing: border-box;
    border: 1px solid gray;
    white-space: nowrap;
    height: 12px; /* kinda bad but works for now */
  }
  td {
    padding: 0px;
    height: 18px; /* kinda bad but works for now */
  }
  td:nth-child(-n + 2) {
    border-right: 2px solid black;
  }
  th:nth-child(2) {
    border-right: 2px solid black;
  }
  th:first-child {
    border-left: none;
  }
  td:first-child {
    border: none;
  }
  td:nth-child(-n + 2):hover ~ td.field {
    background-color: rgba(0, 0, 0, 0.1);
  }
  td.field:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }
  td.new-day {
    border-top: 2px solid black;
  }
  tr:last-child {
    border-bottom: 2px solid black;
  }
  td div {
    padding: 3px;
    height: 12px;
  }
  td.edit div {
    padding: 3px;
    height: 12px;
    background: rgb(173, 216, 230, 0.5);
  }
  td.patch div {
    padding: 3px;
    height: 12px;
    background: rgba(221, 160, 221, 0.5);
  }
  .bottom {
    border-top: 3px solid grey;
    padding: 3px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-direction: row;
  }
  .add-profile-box {
    flex: 2;
  }
  .profile-box {
    padding-left: 3px;
    padding-right: 3px;
    min-width: 0px;
    flex: 2;
    display: flex;
    align-items: center;
    justify-content: left;
  }
  .profiles {
    min-width: 0px;
  }
  .profiles option {
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .diff {
    color: rgb(0, 128, 0);
    font-weight: bold;
  }
</style>
