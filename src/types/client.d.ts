export type DualViewProps = {
    title: string,
    subtitle: string,
    entries: Array<Array<string>>,
    key: string,
}

export type SheetCellProps = {
    content: string,
    row: number,
    col: number,
    color: string,
    elem?: HTMLTableCellElement,
}

export type RGBColor = {
    red: number,
    green: number,
    blue: number,
}
