import { useReducer } from 'react';
import { CrudActionType, CrudModalAction, CrudModalState } from '../types';


export function crudReducer<T>(
  state: CrudModalState<T>,
  action: CrudModalAction<T>
): CrudModalState<T> {
  console.log(state, action);
  switch (action.type) {
    case CrudActionType.CREATE:
      return { visible: true, readonly: false };
    case CrudActionType.EDIT:
      return { visible: true, readonly: false, record: action.payload };
    case CrudActionType.DETAIL:
      return { visible: true, readonly: true, record: action.payload };
    case CrudActionType.DELETE:
      return state; // 不是 modal 处理范围
    case CrudActionType.CLOSE:
      return { visible: false, readonly: false, record: undefined };
    case CrudActionType.LOG:
      return { visible: true, readonly: true, record: action.payload };
    default:
      return state;
  }
}

export function useCrudModalReducer<T>() {
  const initialState: CrudModalState<T> = {
    visible: false,
    readonly: false,
    record: undefined,
  };

  const [state, dispatch] = useReducer<React.Reducer<CrudModalState<T>, CrudModalAction<T>>>(
    crudReducer,
    initialState
  );

  return { state, dispatch };
}
