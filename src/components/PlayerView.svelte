<script lang="ts">
  import { onMount } from "svelte";
  import type { ProfileChunk } from "$types/client";
  export let sheetId: string;
  export let selectedPlayer: string | undefined = undefined;
  // any future state that should be saved upon context switch should be
  // exported as a prop here, so the root page can bind to it.
  let playerList: Array<string> = [];
  let confirmedPlayers: Array<string> = [];
  let numConfirmed = 0;
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
    profiles: { [key: string]: { [key: string]: Array<ProfileChunk> } };
  } = {
    headers: [],
    entries: [],
    revs: [],
    editors: [],
    profiles: {},
  };
  let rowStates: Array<string> = [];
  let fieldStates: Array<Array<string>> = [];
  let mounted = false;
  let editorString = "";
  let addInputText = "";
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
    activeProfiles = Object.keys(scoreInfo.profiles);
    selectedProfile = activeProfiles.length > 0 ? activeProfiles[0] : undefined;
    addInputText = activeProfiles.length > 0 ? "" : selectedPlayer;
    loadProfile(selectedProfile);
  };
  const loadProfile = (profileName: string | undefined): void => {
    rowStates = scoreInfo.entries.map(() => "none");
    fieldStates = scoreInfo.entries.map((row) => row.fields.map(() => "none"));
    if (profileName === undefined) return;
    const profile = scoreInfo.profiles[profileName];
    for (const rev in profile) {
      const revNum = parseInt(rev);
      const rowIndex = scoreInfo.revs.indexOf(revNum);
      if (rowIndex === -1) throw Error("shouldn't happen");
      const chunks = profile[rev];
      for (const chunk of chunks) {
        const { type, values } = chunk;
        if (type === "UPDATE") {
          rowStates[rowIndex] = "edit";
          for (const header in values) {
            const colIndex = scoreInfo.headers.indexOf(header);
            fieldStates[rowIndex][colIndex] = "edit";
          }
        } else {
          for (const header in values) {
            const colIndex = scoreInfo.headers.indexOf(header);
            if (colIndex === -1) throw Error("shouldn't happen");
            if (type === "EDIT") {
              fieldStates[rowIndex][colIndex] = "edit";
            }
            if (type === "PATCH") {
              fieldStates[rowIndex][colIndex] = "patch";
            }
          }
        }
      }
    }
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
    selectedPlayer = undefined;
    const data = await playerListFetch.json();
    playerList = data.players;
    confirmedPlayers = data.confirmed;
    numConfirmed = confirmedPlayers.reduce(
      (sum, state) => sum + (state === "none" ? 0 : 1),
      0,
    );
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
    // toggle cell, cycle between "none", "edit", and "patch"
    if (fieldStates[row]?.[col] === "none") {
      fieldStates[row][col] = "edit";
    } else if (fieldStates[row]?.[col] === "edit") {
      fieldStates[row][col] = "patch";
    } else {
      fieldStates[row][col] = "none";
    }
  };
  const preventDoubleClick = (e: MouseEvent): void => {
    if (e.detail > 1) e.preventDefault();
  };
  const addProfile = (e: KeyboardEvent): void => {
    const input = e.target;
    if (
      input instanceof HTMLInputElement &&
      e.key === "Enter" &&
      !activeProfiles.includes(input.value)
    ) {
      activeProfiles = [...activeProfiles, input.value];
      selectedProfile = input.value;
      input.value = "";
      if (activeProfiles.length > 1) {
        // in this case, a profile already exists, and thus the board should
        // be wiped.
        scoreInfo.profiles[selectedProfile] = {};
        loadProfile(selectedProfile);
      }
    }
  };
  const setEditorString = (i: number): void => {
    const editors = scoreInfo.editors[i];
    editorString = editors.join(", ");
  };
  const writeProfile = async (): Promise<void> => {
    if (selectedPlayer === undefined) {
      alert("No player selected!");
      return;
    }
    if (selectedProfile === undefined || selectedProfile === null) {
      alert("No profile selected!");
      return;
    }
    // loop through row states and field states, construct profiles
    const allInfo: { [key: number]: Array<ProfileChunk> } = {};
    for (let i = 0; i < rowStates.length; i++) {
      const rev = scoreInfo.revs[i];
      if (rowStates[i] === "edit") {
        // add entire row
        const chunk: ProfileChunk = {
          type: "UPDATE",
          values: {} as { [key: string]: string },
        };
        for (let j = 0; j < fieldStates[i].length; j++) {
          if (fieldStates[i][j] !== "none") {
            chunk.values[scoreInfo.headers[j]] = scoreInfo.entries[i].fields[j];
          }
        }
        allInfo[rev] = [chunk];
      } else {
        // loop through all headers
        const chunks: Array<ProfileChunk> = [];
        for (let j = 0; j < fieldStates[i].length; j++) {
          if (fieldStates[i][j] === "edit") {
            const values: { [key: string]: string } = {};
            values[scoreInfo.headers[j]] = scoreInfo.entries[i].fields[j];
            chunks.push({
              type: "EDIT",
              values: values,
            });
          } else if (fieldStates[i][j] === "patch") {
            const values: { [key: string]: string } = {};
            values[scoreInfo.headers[j]] = scoreInfo.entries[i].fields[j];
            chunks.push({
              type: "PATCH",
              values: values,
            });
          }
        }
        if (chunks.length > 0) {
          allInfo[rev] = chunks;
        }
      }
    }
    if (Object.keys(allInfo).length === 0) {
      alert("Cannot confirm blank submission - use 'Ignore' instead.");
    }
    const data = {
      gid: sheetId,
      player: selectedPlayer,
      profile: selectedProfile,
      info: allInfo,
    };
    const writeProfileFetch = await fetch("/player", {
      method: "POST",
      headers: {
        "Content-type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (writeProfileFetch.status !== 200) {
      alert("error writing profiles");
    }
    // update saved state
    scoreInfo.profiles[selectedProfile] = allInfo;
    // mark corresponding row as confirmed
    const playerIndex = playerList.indexOf(selectedPlayer);
    confirmedPlayers[playerIndex] = "confirmed";
    numConfirmed = confirmedPlayers.reduce(
      (sum, state) => sum + (state === "none" ? 0 : 1),
      0,
    );
  };
  const ignorePlayer = async (): Promise<void> => {
    if (selectedPlayer === undefined) return;
    const data = {
      gid: sheetId,
      player: selectedPlayer,
      profile: null,
      info: null,
    }
    const ignorePlayerFetch = await fetch("/player", {
      method: "POST",
      headers: {
        "Content-type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (ignorePlayerFetch.status !== 200) {
      alert("error writing profiles");
    }
    const playerIndex = playerList.indexOf(selectedPlayer);
    confirmedPlayers[playerIndex] = "ignored";
    numConfirmed = confirmedPlayers.reduce(
      (sum, state) => sum + (state === "none" ? 0 : 1),
      0,
    );
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
    <p>Progress: {numConfirmed}/{playerList.length}</p>
    <div class="scroll-container">
      {#each playerList as player, i}
        <input
          type="radio"
          bind:group={selectedPlayer}
          name="players"
          id={player}
          value={player}
        />
        <label
          class="player-option"
          class:confirmed={confirmedPlayers[i] === "confirmed"}
          class:ignored={confirmedPlayers[i] === "ignored"}
          for={player}>{player}</label
        >
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
                on:mousedown={preventDoubleClick}
                on:mouseenter={() => setEditorString(i)}
                ><div>{row.date[0]}</div></td
              >
              <td
                class:new-day={row.date[0] != ""}
                class:edit={rowStates[i] === "edit"}
                on:click={() => handleRowClick(i)}
                on:mousedown={preventDoubleClick}
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
                  on:mousedown={preventDoubleClick}
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
          bind:value={addInputText}
          on:keypress={addProfile}
        />
      </div>
      <div class="profile-box">
        Profile:
        <select
          class="profiles"
          bind:value={selectedProfile}
          on:change={() => loadProfile(selectedProfile)}
        >
          {#each activeProfiles as prof}
            <option value={prof}>
              {prof}
            </option>
          {/each}
        </select>
      </div>
      <button type="button" on:click={ignorePlayer}>Ignore</button>
      <button type="button" on:click={writeProfile}>Confirm</button>
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
  .main {
    display: flex;
    flex-direction: row;
    height: 100%;
  }
  .player-menu {
    border: 1px solid grey;
    display: flex;
    flex-direction: column;
    flex: 2;
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
    flex: 9;
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
  .confirmed {
    background-color: rgb(151, 202, 114);
  }
  .ignored {
    background-color: rgb(239, 95, 107);
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
