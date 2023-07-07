export type Sheet = {
    cells: Array<Array<string>>,
    context: SheetContext,
    rev: number,
}

export type SheetContext = {
    name: string,
    time?: number,
    editors?: Array<string>,
}

export type DualViewProps = {
    title: string,
    subtitle: string,
    cells: Array<Array<string>>,
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
