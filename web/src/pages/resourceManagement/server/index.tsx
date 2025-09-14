import React from 'react';
import { Card, Table, Button, Form } from '@arco-design/web-react';
import { Server } from '@/client';
import { IconPlus } from '@arco-design/web-react/icon';
import useLocale from '@/utils/useLocale';
import { CrudActionType } from '@/hooks';
import { useSearchForm } from '@/hooks/useSearchForm';
import { useCrudTableColumns } from '@/hooks/useTableColumns';
import { getBaseColumns } from './TableColumns';
import ServerModalForm from './ModalForm';
import locale from './locale';
import SearchForm from './SearchForm';
import useServerCrud from './useCrud';

const ServerTable = () => {
  const [modalForm] = Form.useForm();
  const t = useLocale(locale);
  const {
    loading,
    dataSource,
    pagination,
    state,
    dispatch,
    handleSave,
    handleAction,
    onSearch,
    handleTableChange,
  } = useServerCrud();
  const {
    form: searchForm,
    handleSearch,
    handleReset,
  } = useSearchForm((params) => {
    onSearch(params);
  });
  const baseColumns = getBaseColumns(t);
  const columnsWithOperation = useCrudTableColumns(
    baseColumns,
    t,
    handleAction
  );

  return (
    <Card>
      <SearchForm
        form={searchForm}
        onSearch={handleSearch}
        onReset={handleReset}
      />
      <div style={{ marginBottom: 10, padding: 10 }}>
        <Button
          size="mini"
          type="primary"
          icon={<IconPlus />}
          onClick={() => dispatch({ type: CrudActionType.CREATE })}
        >
          {t['table.operation.new']}
        </Button>
      </div>

      <ServerModalForm
        form={modalForm}
        loading={loading}
        visible={state.visible}
        readOnly={state.readonly}
        record={state.record as Server | undefined}
        onCancel={() => {
          dispatch({ type: CrudActionType.CLOSE });
          modalForm.resetFields();
        }}
        onSubmit={handleSave}
      />

      <Table
        size="mini"
        columns={columnsWithOperation}
        data={dataSource}
        pagination={pagination}
        onChange={handleTableChange}
        loading={loading}
        scroll={{
          x: 1400,
          y: 550,
        }}
      />
    </Card>
  );
};

export default ServerTable;
