import hash from "object-hash";
import { diffArrays } from "diff";

/**
  * STRATEGY
  *  hash each row of each 2d array, then find the diff of those
  *  out of the remaining ones, check if any hashes are the same
  *  from the remaining ones of those, find the lcs of each row
  */

/**
  * moved: array of pairs denoting the start/end indices of a row that moved
  * added: indices of array2 corresponding to rows not present in array1
  * removed: indices of array1 corresponding to rows not present in array2
  */
export const diffSheets = (
    array1: Array<Array<string>>,
    array2: Array<Array<string>>,
): {
    moved: Array<[number, number]>,
    added: Array<number>,
    removed: Array<number>
}=> {
    const hash1 = array1.map((row) => hash(row.slice(1)));
    const hash2 = array2.map((row) => hash(row.slice(1)));
    const rowDiff = diffArrays(hash1, hash2);
    // associates rows that aren't part of the diff with their
    // original positions in each array
    const map1: Map<string, number> = new Map();
    const map2: Map<string, number> = new Map();
    // walk through diff, see what rows are different
    let index1 = 0;
    let index2 = 0;
    for (const change of rowDiff) {
        if (change.count === undefined) throw Error("no count");
        // present in array2 but not array1
        if (change.added) {
            for (const row of change.value) {
                map2.set(row, index2);
                index2++;
            }
        }
        // present in array1 but not array2
        else if (change.removed) {
            for (const row of change.value) {
                map1.set(row, index1);
                index1++;
            }
        }
        // present in both
        else {
            index1 += change.count;
            index2 += change.count;
        }
    }
    console.assert(index1 === hash1.length);
    console.assert(index2 === hash2.length);
    const moved: Array<[number, number]> = [];
    const added: Array<number> = [];
    const removed: Array<number> = [];
    // if both maps have a common entry, that means the row was moved
    // otherwise, it was truly deleted
    for (const [key, index1] of map1) {
        const index2 = map2.get(key);
        if (index2 !== undefined) {
            moved.push([index1, index2]);
        }
        else {
            removed.push(index1);
        }
    }
    for (const [key, index] of map2) {
        if (!map1.has(key)) {
            added.push(index);
        }
    }
    return {
        moved,
        added,
        removed,
    };
};
