<script lang="ts">
  import DualView from "$components/DualView.svelte";
  import PlayerView from "$components/PlayerView.svelte";
  import type { DualViewProps } from "$types/client";
  import type { PageServerData } from "./$types";
  import { formatFullDate } from "$lib/format";
  import { onMount } from "svelte";
  export let data: PageServerData;
  let MIN_INDEX: number;
  let MAX_INDEX: number;
  let currentIndex: number;
  let index_is_updating: boolean;
  let index_has_changed: boolean;
  let menuGid: string;
  let sheetIds: Array<string> = [];
  let boards: {
    [key: string]: Array<{
      gid: string;
      start: number;
      end: number;
    }>;
  } = {};
  let menuBoard = "";
  // TODO: change to default
  let mode = "sheet";
  let view = "player";
  let menuIndex: number;
  let showUnique = true;

  let dualViewProps: Array<DualViewProps> = [
    {
      title: "",
      subtitle: "",
      cells: [[]],
    },
    {
      title: "",
      subtitle: "",
      cells: [[]],
    },
  ];

  // for keeping playerview consistent
  let selectedPlayer: string | undefined = undefined;

  const fetchSheetByIndex = async (
    view: number,
    id: string,
    index: number | undefined,
  ): Promise<void> => {
    if (index == undefined) return;
    try {
      const sheetFetch = await fetch(
        "/sheet?" +
          new URLSearchParams({
            id: id,
            index: index.toString(),
            unique: showUnique.toString(),
          }),
        {
          method: "GET",
          headers: {
            "Content-type": "application/json",
          },
        },
      );
      if (sheetFetch.status != 200) {
        throw Error("error fetching sheet");
      }
      // TODO: duplicate code
      const { cells, context, rev } = await sheetFetch.json();
      dualViewProps[view] = {
        title: rev.toString() + ": " + context.name,
        subtitle: `${formatFullDate(context.time) ?? "unknown time"} by ${
          context.editors ?? "unknown editor"
        }`,
        cells: cells,
      };
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLeaderboardByIndex = async (
    view: number,
    name: string,
    index: number | undefined,
  ): Promise<void> => {
    if (index == undefined) return;
    try {
      const boardFetch = await fetch(
        "/leaderboard?" +
          new URLSearchParams({
            name: name,
            index: index.toString(),
            unique: showUnique.toString(),
          }),
        {
          method: "GET",
          headers: {
            "Content-type": "application/json",
          },
        },
      );
      if (boardFetch.status != 200) {
        throw Error("error fetching board");
      }
      // TODO: duplicate code
      const { cells, context, rev } = await boardFetch.json();
      dualViewProps[view] = {
        title: rev.toString() + ": " + context.name,
        subtitle: `${formatFullDate(context.time) ?? "unknown time"} by ${
          context.editors ?? "unknown editor"
        }`,
        cells: cells,
      };
    } catch (err) {
      console.error(err);
    }
  };

  const updateProps = async (): Promise<void> => {
    if (currentIndex === undefined) return;
    // use index to compute the rev+id that's needed to be fetched
    if (index_is_updating) {
      index_has_changed = true;
      return;
    }
    index_is_updating = true;
    if (mode === "sheet") {
      await Promise.all([
        fetchSheetByIndex(0, menuGid, currentIndex),
        fetchSheetByIndex(1, menuGid, currentIndex + 1),
      ]);
    } else if (mode === "leaderboard") {
      await Promise.all([
        fetchLeaderboardByIndex(0, menuBoard, currentIndex),
        fetchLeaderboardByIndex(1, menuBoard, currentIndex + 1),
      ]);
    } else {
      throw Error("invalid mode");
    }
    index_is_updating = false;
    if (index_has_changed) {
      index_has_changed = false;
      await updateProps();
    }
  };
  const updateInterval = async (
    menuGid: string,
    menuBoard: string,
    mode: string,
    showUnique: boolean,
  ): Promise<void> => {
    if (menuGid === undefined) return;
    if (mode === "sheet") {
      const sheetCountFetch = await fetch(
        "/sheet/info?" +
          new URLSearchParams({
            id: menuGid,
            unique: showUnique.toString(),
          }),
        {
          method: "GET",
          headers: {
            "Content-type": "application/json",
          },
        },
      );
      if (sheetCountFetch.status != 200) {
        throw Error("error fetching sheet");
      }
      // TODO: duplicate code
      const count = (await sheetCountFetch.json()).count;
      MIN_INDEX = 0;
      MAX_INDEX = count - 2;
      currentIndex = MIN_INDEX;
      menuIndex = MIN_INDEX;
    } else if (mode === "leaderboard") {
      // fetch information for sheet view
      const sheetCountFetch = await fetch(
        "/leaderboard/info?" +
          new URLSearchParams({
            name: menuBoard,
            unique: showUnique.toString(),
          }),
        {
          method: "GET",
          headers: {
            "Content-type": "application/json",
          },
        },
      );
      if (sheetCountFetch.status != 200) {
        throw Error("error fetching sheet");
      }
      // TODO: duplicate code
      const count = (await sheetCountFetch.json()).count;
      MIN_INDEX = 0;
      MAX_INDEX = count - 2;
      currentIndex = MIN_INDEX;
      menuIndex = MIN_INDEX;
    }
    await updateProps();
  };
  const updateIndexFromMenu = (e: KeyboardEvent) => {
    if (e.key === "Enter") {
      currentIndex = menuIndex;
    }
  };
  onMount(async () => {
    currentIndex = MIN_INDEX;
    menuIndex = MIN_INDEX;
    sheetIds = data.gids;
    boards = data.boards;
    menuGid = sheetIds[0];
    menuBoard = Object.keys(boards)[0];
    await updateProps();
  });
  $: currentIndex, updateProps();
  $: currentIndex, (menuIndex = currentIndex);
  $: updateInterval(menuGid, menuBoard, mode, showUnique);
</script>

<div id="layout">
  <div id="view">
    {#if mode === "sheet" && view === "player"}
      <PlayerView sheetId={menuGid} bind:selectedPlayer />
    {:else}
      <DualView leftProps={dualViewProps[0]} rightProps={dualViewProps[1]} />
    {/if}
  </div>

  {#if !(mode === "sheet" && view === "player")}
    <div id="scrollbar">
      <p class="scrollbar-text">Index:</p>
      <input
        type="number"
        min={MIN_INDEX}
        max={MAX_INDEX}
        bind:value={menuIndex}
        on:keypress={updateIndexFromMenu}
      />
      <button
        class="scroll-button"
        on:click={() => {
          currentIndex = Math.max(MIN_INDEX, currentIndex - 1);
        }}>-</button
      >
      <input
        type="range"
        min={MIN_INDEX}
        max={MAX_INDEX}
        bind:value={currentIndex}
      />
      <button
        class="scroll-button"
        on:click={() => {
          currentIndex = Math.min(MAX_INDEX, currentIndex + 1);
        }}>+</button
      >
    </div>
  {/if}

  <div id="sidebar">
    <p class="sidebar-text">Mode:</p>
    <select bind:value={mode}>
      <option value="leaderboard">leaderboard</option>
      <option value="sheet">sheet</option>
    </select>

    {#if mode === "sheet"}
      <p>Sheet ID:</p>
      <select bind:value={menuGid}>
        {#each sheetIds as id}
          <option value={id}>
            {id}
          </option>
        {/each}
      </select>

      <p>View:</p>
      <select bind:value={view}>
        <option value="sheet">sheet</option>
        <option value="player">player</option>
      </select>
    {:else if mode === "leaderboard"}
      <p>Leaderboard:</p>
      <select bind:value={menuBoard}>
        {#each Object.keys(boards) as id}
          <option value={id}>
            {id}
          </option>
        {/each}
      </select>
    {/if}
    <p>Hide identical revisions:</p>
    <input type="checkbox" bind:checked={showUnique} />
  </div>
</div>

<style>
  #layout {
    border: 0px;
    height: 100vh;
    width: 100vw;
    display: grid;
    grid-template-rows: minmax(0, 1fr) auto;
    grid-template-columns: minmax(0, 1fr) 15%;
    grid-template-areas:
      "view side"
      "slider side";
    font-family: "Ubuntu Mono", monospace;
    font-size: 12px;
  }
  div {
    border: 1px solid gray;
  }
  input[type="range"] {
    border: none;
    width: 100%;
  }
  input[type="number"] {
    width: 75px;
  }
  #scrollbar {
    grid-area: slider;
    margin: auto;
    padding: 5px 0px 5px 0px;
    width: 100%;
    display: flex;
    flex-direction: row;
  }
  #sidebar {
    grid-area: side;
    padding: 6px;
  }
  .scrollbar-text {
    margin: auto;
  }
  #view {
    grid-area: view;
  }
  :global(body) {
    margin: 0;
    padding: 0;
  }
  .scroll-button {
    margin: 3px;
  }
</style>
