<!--
  Contains a table and supports the following features:
    - one cell is able to be marked as unselected
    - colors of each cell can be set (to show differing files)
-->

<script lang="ts">
  import { onMount } from "svelte";
  import type { SheetCellProps, RGBColor } from "../types/client";
  export let cells: Array<Array<SheetCellProps>>;
  export let maxHeight: number;
  export let actualHeight: number;
  export let selected: [number, number] | undefined = undefined;
  let selector: {
    top: number;
    left: number;
    width: number;
    height: number;
  } = {
    top: 0,
    left: 0,
    width: 0,
    height: 0,
  };
  export const setCellColor = (i: number, j: number, color: RGBColor | undefined): void => {
    if (color === undefined) {
      cells[i][j].color = "";
    }
    else {
      cells[i][j].color = `background-color:rgb(${color.red},${color.green},${color.blue})`;
    }
  }
  let selectorStyle: string;
  export const getRowHeight = (i: number): number => {
    if (i === Infinity) return Infinity;
    const cell = cells[i]?.[0].elem;
    if (cell === undefined) {
      console.error(`Attempted to get row ${i} in getRowHeight`);
      return 0;
    }
    return cell.offsetTop;
  }
  const updateSelectorStyle = (): void => {
    if (selected === undefined) return;
    const [i, j] = selected;
    let cellElem = cells[i][j].elem;
    if (cellElem === undefined) {
      console.error(`Attempted to update location ${i}, ${j} in updateSelectorStyle`);
      return;
    }
    selector.top = cellElem.offsetTop-1;
    selector.left = cellElem.offsetLeft-1;
    selector.width = cellElem.offsetWidth-2;
    selector.height = cellElem.offsetHeight-2;
    selectorStyle = `left: ${selector.left}px;
      top: ${selector.top}px; width: ${selector.width}px;
      height: ${selector.height}px`;
  }
  const updateSelector = (i: number, j: number): void => {
    if (selected !== undefined && selected[0] === i && selected[1] === j) {
      selected = undefined;
    }
    else {
      selected = [i, j];
      updateSelectorStyle();
    }
  }
  $: selected, updateSelectorStyle();
  onMount(() => {
    console.log("Sheet mounted");
  });
</script>

<div
  class="wrapper"
  style={maxHeight === undefined ? "" : `height: ${maxHeight+10}px`}
>
  <div
    class={selected === undefined ? "hidden" : "selector"}
    style={selectorStyle}
  >
  </div>
  <table bind:clientHeight={actualHeight}>
    <thead>
      <tr>
        {#each cells[0] as cell, j}
          <th
            role=cell
            tabindex=-1
            bind:this={cell.elem}
            on:click={() => updateSelector(0, j)}
            style={cell.color}
          >
            {cell.content}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each cells as row, i}
        {#if i > 0}
          <tr>
            {#each row as cell, j}
              <td
                role=cell
                tabindex=-1
                bind:this={cell.elem}
                on:click={() => updateSelector(i, j)}
                style={cell.color}
              >
                {cell.content}
              </td>
            {/each}
          </tr>
        {/if}
      {/each}
    </tbody>
  </table>
</div>

<style>
  table {
    border-collapse: collapse;
    font-size: 10px;
  }
  td, th {
    border: 1px solid gray;
  }
  .wrapper {
    position: relative;
  }
  .hidden {
    position: absolute;
    display: none;
    pointer-events: none;
  }
  .selector {
    position: absolute;
    border: 2px solid blue;
    pointer-events: none;
  }
</style>
