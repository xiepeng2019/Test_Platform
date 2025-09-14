export interface CrudModalState<T> {
  visible: boolean;
  readonly: boolean;
  record?: Partial<T>;
}

export enum CrudActionType {
  CREATE = 'CREATE',
  EDIT = 'EDIT',
  DETAIL = 'DETAIL',
  DELETE = 'DELETE',
  CLOSE = 'CLOSE',
}

export type CrudModalAction<T> =
  | { type: CrudActionType.CREATE }
  | { type: CrudActionType.EDIT; payload: Partial<T> }
  | { type: CrudActionType.DETAIL; payload: Partial<T> }
  | { type: CrudActionType.DELETE; payload: Partial<T> }
  | { type: CrudActionType.CLOSE };
