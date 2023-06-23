<!--
  Contains a table and supports the following features:
    - one cell is able to be marked as unselected
    - colors of each cell can be set (to show differing files)
  TODO: currently selection logic is super inefficient because it literally checks all
  cells instead of just the one or two that matter.
-->

<script lang="ts">
  export let headers: Array<string>;
  export let entries: Array<Array<string>>;
  export let selected: [number, number] | undefined = undefined;
  const makeCellSelected = async (i: number, j: number) => {
    if (selected !== undefined && selected[0] === i && selected[1] === j) {
      selected = undefined;
    }
    else {
      selected = [i, j];
    }
  }
  const isSelected = (i: number, j: number): boolean => {
    return selected !== undefined && i === selected[0] && j === selected[1];
  }
</script>

<table>
  <thead>
    <tr>
      {#each headers as header, j}
        <th
          class:selected={selected && isSelected(-1, j)}
          on:click={() => makeCellSelected(-1, j)}
        >{header}</th>
      {/each}
    </tr>
  </thead>
  {#each entries as row, i}
    <tr>
      {#each row as entry, j}
        <td
          class:selected={selected && isSelected(i, j)}
          on:click={() => makeCellSelected(i, j)}
        >{entry}</td>
      {/each}
    </tr>
  {/each}
</table>

<style>
  table {
    border-collapse: collapse;
  }
  td, th {
    border: 1px solid gray;
  }
  .selected {
    border: 2px solid blue;
  }
</style>
