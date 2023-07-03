<!--
  Contains a table and supports the following features:
    - one cell is able to be marked as unselected
    - colors of each cell can be set (to show differing files)
-->

<script lang="ts">
  import { onMount } from "svelte";
  import type { SheetCellProps, RGBColor } from "../types/client";
  import VirtualList from '@sveltejs/svelte-virtual-list';
  export let entries: Array<Array<SheetCellProps>>;
  //export let rowEntries: Array<{
  //  index: number,
  //  row: Array<string>
  //}>;
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
      entries[i][j].color = "";
    }
    else {
      entries[i][j].color = `background-color:rgb(${color.red},${color.green},${color.blue})`;
    }
  }
  let selectorStyle: string;
  export const getRowHeight = (i: number): number => {
    if (i === Infinity) return Infinity;
    const cell = entries[i]?.[0].elem;
    if (cell === undefined) {
      console.error(`Attempted to get row ${i} in getRowHeight`);
      return 0;
    }
    return cell.offsetTop;
  }
  const updateSelectorStyle = (): void => {
    if (selected === undefined) return;
    const [i, j] = selected;
    let cellElem = entries[i][j].elem;
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
  //const updateRowEntries = () => {
  //  rowEntries = entries.map((row, i) => {
  //    return {
  //      index: i,
  //      row: row,
  //    };
  //  });
  //}
  $: selected, updateSelectorStyle();
  //$: entries, updateRowEntries();
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
        {#each entries[0] as entry, j}
          <th
            role=cell
            tabindex=-1
            bind:this={entry.elem}
            on:click={() => updateSelector(0, j)}
            style={entry.color}
          >
            {entry.content}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each entries as row, i}
        {#if i > 0}
          <tr>
            {#each row as entry, j}
              <td
                role=cell
                tabindex=-1
                bind:this={entry.elem}
                on:click={() => updateSelector(i, j)}
                style={entry.color}
              >
                {entry.content}
              </td>
            {/each}
          </tr>
        {/if}
      {/each}
    </tbody>
    <!--
    <VirtualList items={rowEntries} let:item>
      {console.log(rowEntries)}
      <tr>
        {#each item.value as entry, j}
          <td
            bind:this={cells[item.index+1][j]}
            on:click={() => updateSelector(item.index+1, j)}
            style={cellColors[item.index+1][j] == undefined ? "" :
              `background-color:${cellColors[entry.index+1][j]};`
            }
          >{entry}</td>
        {/each}
      </tr>
    </VirtualList>
    -->
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
