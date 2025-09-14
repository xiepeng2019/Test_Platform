import { useCallback, useEffect, useState } from 'react';
import {
  createTestTask,
  updateTestTask,
  deleteTestTask,
  listTestTask,
  TestTask,
  TestTaskCreate,
  runTestTask,
} from '@/client';
import { Message, PaginationProps } from '@arco-design/web-react';
import useLocale from '@/utils/useLocale';
import locale from '@/locale';
import { useCrudModalReducer } from './useTaskModalReducer';
import { CrudActionType } from '../types';


const useTestTaskCrud = () => {
  const t = useLocale(locale);
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<TestTask[]>([]);
  const { state, dispatch } = useCrudModalReducer<TestTask>();
  const { state: logState, dispatch: logDispatch } = useCrudModalReducer<TestTask>();
  const [filters, setFilters] = useState<{ [key: string]: any }>({});
  const [pagination, setPagination] = useState<PaginationProps>({
    sizeCanChange: true,
    showTotal: true,
    pageSize: 10,
    current: 1,
    pageSizeChangeResetCurrent: true,
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const query = {
        page: pagination.current,
        pageSize: pagination.pageSize,
        ...filters,
      };
      const { data, error } = await listTestTask({ query });
      if (error) {
        Message.error('获取测试任务列表失败');
        return;
      }
      setDataSource(data.list);
      setPagination((p) => ({
        ...p,
        total: data.total,
      }));
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  function handleSave(record: TestTask): Promise<void>;
  function handleSave(record: TestTaskCreate): Promise<void>;
  async function handleSave(record: TestTask | TestTaskCreate) {
    if ('id' in record && typeof record.id === 'number') {
      await handleUpdate(record);
    } else {
      await handleCreate(record as TestTaskCreate);
    }
  }

  const handleUpdate = async (record: TestTask) => {
    const { error } = await updateTestTask({ body: record, path: { id: record.id } });
    if (error) {
      Message.error(t['table.operation.update.error'] + (error?.detail || ''));
      return;
    }
    await fetchData();
    dispatch({ type: CrudActionType.CLOSE });
    Message.success(t['table.operation.update.success']);
  };

  const handleCreate = async (record: TestTaskCreate) => {
    console.log('create', record);
    const { error } = await createTestTask({ body: record });
    if (error) {
      Message.error(t['table.operation.create.error'] + (error?.detail || ''));
      return;
    }
    await fetchData();
    dispatch({ type: CrudActionType.CLOSE });
    Message.success(t['table.operation.create.success']);
  };

  const handleDelete = async (record: TestTask) => {
    await deleteTestTask({ path: { id: record.id } });
    await fetchData();
    Message.success(t['table.operation.delete.success']);
  };

  const onSearch = (params: Record<string, any>) => {
    setPagination({ ...pagination, current: 1 });
    setFilters(params);
  }

  const handleTableChange = ({ current, pageSize }) => {
    setPagination({ ...pagination, current, pageSize: pageSize || pagination.pageSize });
  };

  const handleAction = async (record: TestTask, action: CrudActionType) => {
    // setCurrentTask(record);
    switch (action) {
      case CrudActionType.RUN:
        const { error } = await runTestTask({ path: { id: record.id } });
        if (error) {
          Message.error(error?.detail?.toString() || '运行失败');
          return;
        }
        Message.success('运行成功');
        fetchData()
        break;
      case CrudActionType.LOG:
        logDispatch({ type: action, payload: record });
        break;
      case CrudActionType.DETAIL:
        dispatch({ type: action, payload: record });
        break;
      case CrudActionType.EDIT:
        dispatch({ type: action, payload: record });
        break;
      case CrudActionType.DELETE:
        handleDelete(record);
        break;
    }
  };

  return {
    loading,
    dataSource,
    pagination,
    state,
    dispatch,
    logState,
    logDispatch,
    handleSave,
    handleDelete,
    onSearch,
    setPagination,
    handleTableChange,
    handleAction,
  };
};

export default useTestTaskCrud;
