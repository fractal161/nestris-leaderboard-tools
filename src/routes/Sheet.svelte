<!--
  Contains a table and supports the following features:
    - one cell is able to be marked as unselected
    - colors of each cell can be set (to show differing files)
-->

<script lang="ts">
  export let headers: Array<string>;
  export let entries: Array<Array<string>>;
  let cells: Array<Array<HTMLTableCellElement>> = Array.from(
    Array(entries.length+1), () => []
  );
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
  let selectorStyle: string;
  $: selector, selectorStyle = `left: ${selector.left}px;
    top: ${selector.top}px;
    width: ${selector.width}px;
    height: ${selector.height}px`;
  const updateSelector = (i: number, j: number): void => {
    if (selected !== undefined && selected[0] === i && selected[1] === j) {
      selected = undefined;
    }
    else {
      selected = [i, j];
      let cell = cells[i][j];
      console.assert(cell !== undefined);
      selector.top = cell.offsetTop-1;
      selector.left = cell.offsetLeft-1;
      selector.width = cell.offsetWidth-2;
      selector.height = cell.offsetHeight-2;
    }
  }
</script>

<div class="wrapper">
  <div
    class={selected === undefined ? "hidden" : "selector"}
    style={selectorStyle}
  >
  </div>
  <table>
    <thead>
      <tr>
        {#each headers as header, j}
          <th
            bind:this={cells[0][j]}
            on:click={() => updateSelector(0, j)}
          >{header}</th>
        {/each}
      </tr>
    </thead>
    {#each entries as row, i}
      <tr>
        {#each row as entry, j}
          <td
            bind:this={cells[i+1][j]}
            on:click={() => updateSelector(i+1, j)}
          >{entry}</td>
        {/each}
      </tr>
    {/each}
  </table>
</div>

<style>
  table {
    border-collapse: collapse;
  }
  td, th {
    border: 1px solid gray;
    user-select: none;
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
