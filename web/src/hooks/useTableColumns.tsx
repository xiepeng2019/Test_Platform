import React from 'react';
import { Button, Popconfirm, Space } from '@arco-design/web-react';
import { ColumnProps } from '@arco-design/web-react/lib/Table';
import { CrudActionType } from './types';

type LocaleMap = Record<string, string>;

export function useCrudTableColumns<T extends Record<string, any>>(
  baseColumns: ColumnProps<T>[],
  t: LocaleMap,
  callback: (record: T, action: CrudActionType) => void
): ColumnProps<T>[] {
  const operationColumn: ColumnProps<T> = {
    title: t['table.operation'],
    dataIndex: 'operations',
    key: 'operations',
    fixed: 'right' as const,
    width: 200,
    render: (_, record: T) => (
      <Space size="small">
        <Button
          status="success"
          size="mini"
          onClick={() => callback(record, CrudActionType.DETAIL)}
        >
          {t['table.operation.detail']}
        </Button>
        <Button
          status="warning"
          size="mini"
          onClick={() => callback(record, CrudActionType.EDIT)}
        >
          {t['table.operation.edit']}
        </Button>
        <Popconfirm
          focusLock
          title={t['table.operation.confirmDelete'] ?? '确认删除?'}
          content={t['table.operation.deleteTip'] ?? '删除后将无法恢复'}
          onOk={() => callback(record, CrudActionType.DELETE)}
        >
          <Button status="danger" size="mini">
            {t['table.operation.delete']}
          </Button>
        </Popconfirm>
      </Space>
    ),
  };

  return [...baseColumns, operationColumn];
}
