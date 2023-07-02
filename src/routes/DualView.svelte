<script lang="ts">
  import { onMount, tick } from "svelte";
  import type { RGBColor, DualViewProps } from "../types/client";
  import { diffSheets } from "../lib/diff";
  import SheetView from "./SheetView.svelte";
  import Sheet from "./Sheet.svelte";
  export let scrollLeft = 0;
  export let scrollTop = 0;
  let setCellColor: Array<(i: number, j: number, color: RGBColor) => void> = [];
  let getRowHeight: Array<(i: number) => number> = [];
  export let leftProps: DualViewProps = {
    title: "",
    subtitle: "",
    entries: [[]],
    key: ""
  };

  export let rightProps: DualViewProps = {
    title: "",
    subtitle: "",
    entries: [[]],
    key: ""
  };

  let selected: [number, number] | undefined = undefined;

  const getSheetProps = (props: DualViewProps) => {
    return props.entries.map((row, i) => row.map((entry, j) => {
      return {
        content: entry,
        row: i,
        col: j,
        color: "rgb(255, 255, 255)",
      }
    }));
  }

  const setScroll = (e: Event) => {
    e.preventDefault();
    if (e.target instanceof Element) {
      scrollTop = e.target.scrollTop;
      scrollLeft = e.target.scrollLeft;
    }
  };
  const setSheetColors = async () => {
    await tick();
    const diff = diffSheets(leftProps.entries, rightProps.entries);
    // track index of earliest row for each half
    let min1 = Infinity;
    let min2 = Infinity;
    for (const [i1, i2] of diff.moved) {
      for (let j = 0; j < leftProps.entries[i1].length; j++) {
        setCellColor[0](i1, j, { red: 90, green: 176, blue: 246 });
        min1 = Math.min(min1, i1);
      }
      for (let j = 0; j < rightProps.entries[i2].length; j++) {
        setCellColor[1](i2, j, { red: 90, green: 176, blue: 246 });
        min2 = Math.min(min2, i2);
      }
    }
    for (const i of diff.added) {
      for (let j = 0; j < rightProps.entries[i].length; j++) {
        setCellColor[1](i, j, { red: 151, green: 202, blue: 114 });
        min2 = Math.min(min2, i);
      }
    }
    for (const i of diff.removed) {
      for (let j = 0; j < leftProps.entries[i].length; j++) {
        setCellColor[0](i, j, { red: 239, green: 95, blue: 107 });
        min1 = Math.min(min1, i);
      }
    }
    // scroll to show the earliest colored row
    scrollTop = Math.min(getRowHeight[0](min1), getRowHeight[1](min2)) - 40;
  };
  $: leftProps.entries, setSheetColors();
  $: rightProps.entries, setSheetColors();
  onMount(() => {
    console.log("DualView mounted");
  });
</script>

<div id=layout>
  <div id=left-title>
    <h2>{leftProps.title}</h2>
    <p>{leftProps.subtitle}</p>
  </div>

  <div id=right-title>
    <h2>{rightProps.title}</h2>
    <p>{rightProps.subtitle}</p>
  </div>

  {#key `${leftProps.key}${rightProps.key}`}
    <SheetView
      bind:scrollTop={scrollTop}
      bind:scrollLeft={scrollLeft}
      on:scroll={setScroll}
    >
      <Sheet
        entries={getSheetProps(leftProps)}
        bind:selected={selected}
        bind:setCellColor={setCellColor[0]}
        bind:getRowHeight={getRowHeight[0]}
      />
    </SheetView>
  {/key}

  {#key `${leftProps.key}${rightProps.key}`}
    <SheetView
      bind:scrollTop={scrollTop}
      bind:scrollLeft={scrollLeft}
      on:scroll={setScroll}
    >
      <Sheet
        entries={getSheetProps(rightProps)}
        bind:selected={selected}
        bind:setCellColor={setCellColor[1]}
        bind:getRowHeight={getRowHeight[1]}
      />
    </SheetView>
  {/key}
</div>

<style>
  #layout {
    border: 0px;
    display: grid;
    height: 100%;
    width: 100%;
    grid-template-rows: auto minmax(0, 1fr);
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    grid-template-areas:
      "left-title right-title"
      "left right";
    font-family: monospace;
  }
  div {
    border: 1px solid gray;
  }
  p {
    font-size: 10px;
    margin: 2px;
  }
  #left-title {
    grid-area: left-title;
    overflow: auto;
  }
  #right-title {
    grid-area: right-title;
    overflow: auto;
  }
  h2 {
    margin: 2px;
  }
</style>
