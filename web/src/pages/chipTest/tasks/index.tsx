import React from 'react';
import { Table, Card, Button, Typography, Form } from '@arco-design/web-react';
import PermissionWrapper from '@/components/PermissionWrapper';
import { IconPlus } from '@arco-design/web-react/icon';
import useLocale from '@/utils/useLocale';
import SearchForm from './components/SearchForm';
import locale from './locale';
import styles from './index.module.less';
import { getBaseColumns } from './constants/TableColumns';
import TaskLogPage from './components/taskLogs';
import { TestTask } from '@/client';
import { useSearchForm } from '@/hooks/useSearchForm';
import ModalForm from './components/ModalForm';
import useTestTaskCrud from './hooks/useCrud';
import { CrudActionType } from './types';

const { Title } = Typography;

function TestTaskTable() {
  const t = useLocale(locale);
  const [modalForm] = Form.useForm();
  const {
    loading,
    dataSource,
    pagination,
    state,
    dispatch,
    logState,
    logDispatch,
    handleSave,
    onSearch,
    handleTableChange,
    handleAction,
  } = useTestTaskCrud();

  const {
    form: searchForm,
    handleSearch,
    handleReset,
  } = useSearchForm((params) => onSearch(params));

  const baseColumns = getBaseColumns(t, handleAction);

  return (
    <Card>
      <SearchForm
        form={searchForm}
        onSearch={handleSearch}
        onReset={handleReset}
      />

      <PermissionWrapper
        requiredPermissions={[{ resource: 'menu.task', actions: ['write'] }]}
      >
        <div className={styles['button-group']}>
          <Button
            size='mini'
            type="primary"
            icon={<IconPlus />}
            onClick={() => dispatch({ type: CrudActionType.CREATE })}
          >
            {t['operations.create']}
          </Button>
        </div>
      </PermissionWrapper>

      <Table<TestTask>
        size="mini"
        rowKey="id"
        loading={loading}
        onChange={handleTableChange}
        pagination={pagination}
        columns={baseColumns}
        data={dataSource}
        scroll={{
          x: 1800,
          y: 550,
        }}
      />

      <ModalForm
        onSubmit={handleSave}
        form={modalForm}
        loading={loading}
        visible={state.visible}
        readOnly={state.readonly}
        record={state.record as TestTask | undefined}
        onCancel={() => dispatch({ type: CrudActionType.CLOSE })}
      />

      <TaskLogPage
        record={logState.record as TestTask | undefined}
        visible={logState.visible}
        onCancel={() => logDispatch({ type: CrudActionType.CLOSE })}
      />
    </Card>
  );
}

export default TestTaskTable;
