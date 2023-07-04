<script lang="ts">
  import { onMount, tick } from "svelte";
  import type { RGBColor, DualViewProps, SheetCellProps } from "../types/client";
  import { diffSheets } from "../lib/diff";
  import SheetView from "./SheetView.svelte";
  import Sheet from "./Sheet.svelte";
  let scrollLeft = 0;
  let scrollTop = 0;
  let setCellColor: Array<(i: number, j: number, color: RGBColor | undefined) => void> = [];
  let getRowHeight: Array<(i: number) => number> = [];
  let heights: Array<number> = [];
  let maxHeight: number | undefined;
  let viewHeight: number;
  let mounted = false;
  export let leftProps: DualViewProps = {
    title: "",
    subtitle: "",
    cells: [[]],
    key: ""
  };

  export let rightProps: DualViewProps = {
    title: "",
    subtitle: "",
    cells: [[]],
    key: ""
  };

  let leftCells: Array<Array<SheetCellProps>> = [[]];
  let rightCells: Array<Array<SheetCellProps>> = [[]];

  let selected: [number, number] | undefined = undefined;

  const getSheetCells = (props: DualViewProps) => {
    return props.cells.map((row, i) => row.map((content, j) => {
      return {
        content: content,
        row: i,
        col: j,
        color: "background-color:rgb(255, 255, 255)",
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
    const diff = diffSheets(leftProps.cells, rightProps.cells);
    // track index of earliest row for each half
    let min1 = Infinity;
    let min2 = Infinity;
    for (const [i1, i2] of diff.moved) {
      for (let j = 0; j < leftProps.cells[i1].length; j++) {
        setCellColor[0](i1, j, { red: 90, green: 176, blue: 246 });
        min1 = Math.min(min1, i1);
      }
      for (let j = 0; j < rightProps.cells[i2].length; j++) {
        setCellColor[1](i2, j, { red: 90, green: 176, blue: 246 });
        min2 = Math.min(min2, i2);
      }
    }
    for (const i of diff.added) {
      for (let j = 0; j < rightProps.cells[i].length; j++) {
        setCellColor[1](i, j, { red: 151, green: 202, blue: 114 });
        min2 = Math.min(min2, i);
      }
    }
    for (const i of diff.removed) {
      for (let j = 0; j < leftProps.cells[i].length; j++) {
        setCellColor[0](i, j, { red: 239, green: 95, blue: 107 });
        min1 = Math.min(min1, i);
      }
    }
    // scroll to show the earliest colored row
    const newScrollTop = Math.min(getRowHeight[0](min1), getRowHeight[1](min2)) - 40;
    scrollTop = newScrollTop === Infinity ? 0 : Math.max(newScrollTop, 0);
    if (maxHeight === undefined) return;
    scrollTop = Math.min(scrollTop, maxHeight-viewHeight);
  };
  const updateSheetState = async (left: DualViewProps, right: DualViewProps) => {
    leftCells = getSheetCells(left);
    rightCells = getSheetCells(right);
    maxHeight = undefined;
    // wait for each view to show new table
    await tick();
    maxHeight = Math.max(heights[0], heights[1])+10;
    await tick();
    // wait for each view to share the max height
    await setSheetColors();
  };
  $: heights, maxHeight = Math.max(heights[0], heights[1])+10;
  $: if (mounted) updateSheetState(leftProps, rightProps);
  onMount(() => {
    mounted = true;
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

  <SheetView
    bind:scrollTop={scrollTop}
    bind:scrollLeft={scrollLeft}
    bind:height={viewHeight}
    on:scroll={setScroll}
  >
    <Sheet
      cells={leftCells}
      scrollTop={scrollTop}
      viewHeight={viewHeight}
      bind:selected={selected}
      bind:maxHeight={maxHeight}
      bind:actualHeight={heights[0]}
      bind:setCellColor={setCellColor[0]}
      bind:getRowHeight={getRowHeight[0]}
    />
  </SheetView>

  <SheetView
    bind:scrollTop={scrollTop}
    bind:scrollLeft={scrollLeft}
    bind:height={viewHeight}
    on:scroll={setScroll}
  >
    <Sheet
      cells={rightCells}
      scrollTop={scrollTop}
      viewHeight={viewHeight}
      bind:selected={selected}
      bind:maxHeight={maxHeight}
      bind:actualHeight={heights[1]}
      bind:setCellColor={setCellColor[1]}
      bind:getRowHeight={getRowHeight[1]}
    />
  </SheetView>
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
