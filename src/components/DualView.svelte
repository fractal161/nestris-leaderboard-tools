<script lang="ts">
  import { onMount, tick } from "svelte";
  import type { RGBColor, DualViewProps, SheetCellProps } from "$types/client";
  import { diffSheets } from "$lib/diff";
  import SheetView from "$components/SheetView.svelte";
  import Sheet from "$components/Sheet.svelte";
  let scrollLeft = 0;
  let scrollTop = 0;
  let setCellColor: Array<
    (i: number, j: number, color: RGBColor | undefined) => void
  > = [];
  let getRowHeight: Array<(i: number) => number> = [];
  let viewHeight: number;
  let mounted = false;
  export let leftProps: DualViewProps = {
    title: "",
    subtitle: "",
    cells: [[]],
  };

  export let rightProps: DualViewProps = {
    title: "",
    subtitle: "",
    cells: [[]],
  };

  let leftCells: Array<Array<SheetCellProps>> = [[]];
  let rightCells: Array<Array<SheetCellProps>> = [[]];

  let selected: [number, number] | undefined = undefined;

  const getSheetCells = (props: DualViewProps) => {
    return props.cells.map((row, i) =>
      row.map((content, j) => {
        return {
          content: content,
          row: i,
          col: j,
          color: "background-color:rgb(255, 255, 255)",
        };
      }),
    );
  };

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
    // very light blue: 174, 216, 251
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
    for (const mod of diff.modified) {
      // to be lazy, start by setting everything to light blue,
      // then set the changes
      const newIndex = mod.added.rowIndex;
      for (let j = 0; j < leftProps.cells[newIndex].length; j++) {
        setCellColor[1](newIndex, j, { red: 174, green: 216, blue: 251 });
      }
      for (const j of mod.added.indices) {
        setCellColor[1](newIndex, j, { red: 151, green: 202, blue: 114 });
      }
      const oldIndex = mod.removed.rowIndex;
      for (let j = 0; j < leftProps.cells[oldIndex].length; j++) {
        setCellColor[0](oldIndex, j, { red: 174, green: 216, blue: 251 });
      }
      for (const j of mod.removed.indices) {
        setCellColor[0](oldIndex, j, { red: 239, green: 95, blue: 107 });
      }
      // update min row for scroll
      min1 = Math.min(min1, oldIndex);
      min2 = Math.min(min2, newIndex);
    }
    // scroll to show the earliest colored row
    const newScrollTop =
      Math.min(getRowHeight[0](min1), getRowHeight[1](min2)) - 40;
    scrollTop = newScrollTop === Infinity ? 0 : Math.max(newScrollTop, 0);
  };
  const updateSheetState = async (
    left: DualViewProps,
    right: DualViewProps,
  ) => {
    leftCells = getSheetCells(left);
    rightCells = getSheetCells(right);
    // wait for each view to show new table
    await tick();
    // wait for each view to share the max height
    await setSheetColors();
  };
  $: if (mounted) updateSheetState(leftProps, rightProps);
  onMount(() => {
    mounted = true;
    console.log("DualView mounted");
  });
</script>

<div id="layout">
  <div id="left-title">
    <h2>{leftProps.title}</h2>
    <p>{leftProps.subtitle}</p>
  </div>

  <div id="right-title">
    <h2>{rightProps.title}</h2>
    <p>{rightProps.subtitle}</p>
  </div>

  <SheetView
    bind:scrollTop
    bind:scrollLeft
    bind:height={viewHeight}
    on:scroll={setScroll}
  >
    <Sheet
      cells={leftCells}
      {scrollTop}
      {viewHeight}
      bind:selected
      bind:setCellColor={setCellColor[0]}
      bind:getRowHeight={getRowHeight[0]}
    />
  </SheetView>

  <SheetView
    bind:scrollTop
    bind:scrollLeft
    bind:height={viewHeight}
    on:scroll={setScroll}
  >
    <Sheet
      cells={rightCells}
      {scrollTop}
      {viewHeight}
      bind:selected
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
    font-family: "Ubuntu Mono", monospace;
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
