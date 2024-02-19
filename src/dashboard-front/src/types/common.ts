// 分页interface
export interface IPagination {
  small?: boolean
  offset: number
  limit: number
  count: number
  abnormal?: boolean
}

export interface IDialog {
  isShow: boolean
  title: string
  loading?: boolean
}

export interface IMenu {
  name: string
  title: string
  icon?: string
  enabled?: boolean
  children?: IMenu[]
}

export interface IMethodList {
  id: string
  name: string
}
// drop下拉菜单interface
export interface IDropList {
  value: string
  label: string
  disabled?: boolean
}

export enum StaffType {
  RTX = 'rtx',
}
export interface Staff {
  english_name: string;
  chinese_name: string;
  username: string;
  display_name: string;
}
