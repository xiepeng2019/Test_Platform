import { useCallback, useEffect, useState } from 'react';
import {
  Server,
  ServerCreate,
  ServerUpdate,
  createServer,
  deleteServer,
  listServer,
  updateServer,
} from '@/client';
import { Message, PaginationProps } from '@arco-design/web-react';
import { CrudActionType, useCrudModalReducer } from '@/hooks';
import useLocale from '@/utils/useLocale';
import locale from '@/locale';

const useServerCrud = () => {
  const t = useLocale(locale);
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<Server[]>([]);
  const { state, dispatch } = useCrudModalReducer<Server>();
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
      const params = {
        page: pagination.current,
        pageSize: pagination.pageSize,
        ...filters,
      };
      const { data, error } = await listServer({ query: params });
      if (error) {
        Message.error('获取测试环境列表失败');
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

  function handleSave(record: Server): Promise<void>;
  function handleSave(record: ServerCreate): Promise<void>;
  async function handleSave(record: Server | ServerCreate) {
    if ('id' in record && typeof record.id === 'number') {
      await handleUpdate(record);
    } else {
      await handleCreate(record as ServerCreate);
    }
  }

  const handleUpdate = async (record: Server) => {
    const { error } = await updateServer({ body: record as ServerUpdate, path: { id: record.id } });
    if (error) {
      Message.error(t['table.operation.update.error'] + (error?.detail || ''));
      return;
    }
    await fetchData();
    dispatch({ type: CrudActionType.CLOSE });
    Message.success(t['table.operation.update.success']);
  };

  const handleCreate = async (record: ServerCreate) => {
    const { error } = await createServer({ body: record });
    if (error) {
      Message.error(t['table.operation.create.error'] + (error?.detail || ''));
      return;
    }
    await fetchData();
    dispatch({ type: CrudActionType.CLOSE });
    Message.success(t['table.operation.create.success']);
  };

  const handleDelete = async (record: Server) => {
    await deleteServer({ path: { id: record.id } });
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

  const handleAction = (record: Server, action: CrudActionType) => {
    switch (action) {
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
    handleSave,
    handleDelete,
    onSearch,
    setPagination,
    handleTableChange,
    handleAction,
  };
};

export default useServerCrud;
