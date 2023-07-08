<!--
  Contains a table and supports the following features:
    - one cell is able to be marked as unselected
    - colors of each cell can be set (to show differing files)
  Virtual list part inspired by https://github.com/sveltejs/svelte-virtual-list/blob/master/VirtualList.svelte
-->

<script lang="ts">
  import { onMount, tick } from "svelte";
  import type { SheetCellProps, RGBColor } from "$types/client";
  export let cells: Array<Array<SheetCellProps>>;
  export let selected: [number, number] | undefined = undefined;
  let topPad = 0;
  let bottomPad = 0;
  let visibleRows: Array<Array<SheetCellProps>> = [[]];
  export let scrollTop: number;
  export let viewHeight: number;
  let mounted = false;
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
  };
  let selectorStyle: string;
  export const getRowHeight = (i: number): number => {
    if (i === Infinity) return Infinity;
    if (cells[0][0].elem === undefined) return Infinity;
    const thHeight = cells[0][0].elem.getBoundingClientRect().height;
    const tdHeight = thHeight + 4;
    return thHeight + tdHeight * (i-1);
  };
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
  };
  const updateSelector = (i: number, j: number): void => {
    if (selected !== undefined && selected[0] === i && selected[1] === j) {
      selected = undefined;
    }
    else {
      selected = [i, j];
      updateSelectorStyle();
    }
  };
  // only render the rows already seen
  const refresh = async (cells: Array<Array<SheetCellProps>>, scrollTop: number) => {
    await tick();
    if (cells.length < 2) {
      visibleRows = cells.slice(1);
      topPad = 0;
      bottomPad = 0;
      return;
    }
    // visible range is around scrollTop to scrollTop + viewHeight
    // main idea: make each row the same height, so computations can be fixed
    // start by rendering the first row so actual height can be measured
    if (cells[0][0].elem === undefined) return;
    const thHeight = cells[0][0].elem.getBoundingClientRect().height-1;
    const tdHeight = thHeight + 5;
    const startIndex = Math.max(Math.floor((scrollTop - thHeight) / tdHeight) - 9, 1);
    const endIndex = Math.min(Math.floor((scrollTop + viewHeight) / tdHeight) + 9, cells.length);
    // TODO: the +1 is a hack to make scrolling nice when a new row is added
    // to the bottom, maybe better to share a maxRowCount prop across both
    [ topPad, bottomPad, visibleRows ] = [
      tdHeight * (startIndex-1),
      tdHeight * (cells.length - endIndex + 1),
      cells.slice(startIndex, endIndex)
    ];
    await tick();
  };
  $: selected, updateSelectorStyle();
  $: if(mounted) refresh(cells, scrollTop);
  onMount(() => {
    mounted = true;
    console.log("Sheet mounted");
  });
</script>

<div class="wrapper">
  <div
    class={selected === undefined ? "hidden" : "selector"}
    style={selectorStyle}
  >
  </div>
  <div style={`border: none;
               padding-top: ${topPad}px;
               padding-bottom: ${bottomPad+10}px`
  }>
  <table>
    <thead>
      <tr>
        {#each cells[0] as cell}
          <th
            role=cell
            tabindex=-1
            bind:this={cell.elem}
            on:click={() => updateSelector(0, cell.col)}
            style={cell.color}
          >
            {cell.content}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each visibleRows as row}
        <tr>
          {#each row as cell}
            <td
              bind:this={cell.elem}
              on:click={() => updateSelector(cell.row, cell.col)}
              style={cell.color}
            >
              {cell.content}
            </td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
  </div>
</div>

<style>
  table {
    border-collapse: collapse;
    font-size: 10px;
  }
  td, th {
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
  .wrapper {
    position: relative;
    width: max-content;
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
    z-index: 1;
  }
</style>
