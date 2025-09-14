import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useSelector } from 'react-redux';
import { Table, PaginationProps } from '@arco-design/web-react';
import useLocale from '@/utils/useLocale';
import locale from '@/pages/chipTest/cases/locale';
import styles from '@/pages/chipTest/cases/style/index.module.less';
import { GlobalState } from '@/store';
import { listTestCase, TestCase } from '@/client';
import {
  getPriorityTag,
  TAG_NO,
  TAG_YES,
} from '@/pages/chipTest/cases/constants';

export interface CaseTableProps {
  selectedRowKeys?: (string | number)[];
  setSelectedRowKeys: (selectedRowKeys: (string | number)[]) => void;
  selectedTreeNode: (string | number)[];
  tableScroll?: {
    x?: number;
    y?: number;
  };
  readonly?: boolean;
}

function getColumns(t: {
  [x: string]:
    | boolean
    | React.ReactChild
    | React.ReactFragment
    | React.ReactPortal;
}) {
  return [
    {
      title: t['case.columns.index'],
      dataIndex: 'index',
      ellipsis: true,
      fixed: 'left' as const,
    },
    {
      title: t['case.columns.name'],
      dataIndex: 'name',
      ellipsis: true,
    },
    {
      title: t['case.columns.priority'],
      dataIndex: 'priority',
      width: 80,
      render: (value: string) => {
        return getPriorityTag(value);
      },
    },
    {
      title: t['case.columns.automation'],
      dataIndex: 'automation',
      width: 80,
      render: (value) => {
        return value ? TAG_YES : TAG_NO;
      },
      onFilter: (value, row) => {
        return row.automation === value;
      },
    },
    {
      title: t['case.columns.automated'],
      dataIndex: 'automated',
      width: 80,
      render: (value) => {
        return value ? TAG_YES : TAG_NO;
      },
    },
  ];
}

function CaseTable(props: CaseTableProps) {
  const t = useLocale(locale);
  const { selectedTreeNode } = props;

  const [data, setData] = useState<TestCase[]>([]);
  const [pagination, setPatination] = useState<PaginationProps>({
    sizeCanChange: true,
    showTotal: true,
    pageSize: 15,
    current: 1,
    pageSizeChangeResetCurrent: true,
  });
  const [loading, setLoading] = useState(true);
  const [formParams, setFormParams] = useState({});
  const columns = useMemo(() => getColumns(t), [t]);
  const caseUpdate = useSelector((state: GlobalState) => state.caseUpdate);
  const { current, pageSize } = pagination;

  const fetchData = useCallback(() => {
    setLoading(true);
    console.log('formParams', formParams);
    listTestCase({
      query: {
        page: current,
        pageSize,
        ...formParams,
      },
    }).then((res) => {
      setData(res.data.list);
      setPatination({
        ...pagination,
        current,
        pageSize,
        total: res.data.total,
      });
      setLoading(false);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current, pageSize, formParams]);

  useEffect(() => {
    fetchData();
  }, [fetchData, caseUpdate]);

  useEffect(() => {
    if (selectedTreeNode.length > 0) {
      const newFormParams = { ...formParams, node_id: selectedTreeNode[0] };
      setFormParams(newFormParams);
      setPatination({ ...pagination, current: 1 });
    } else if (selectedTreeNode.length === 0) {
      setFormParams({ ...formParams, node_id: [] });
      setPatination({ ...pagination, current: 1 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTreeNode]);

  function onChangeTable({ current, pageSize }) {
    setPatination({
      ...pagination,
      current,
      pageSize,
    });
  }

  return (
    <div className={styles['table-content']}>
      <Table
        size="mini"
        rowKey="index"
        rowSelection={{
          checkboxProps: () => ({
            disabled: props.readonly,
          }),
          selectedRowKeys: props.selectedRowKeys,
          checkCrossPage: true,
          type: 'checkbox',
          onSelect: (selected, record) => {
            const currentSelectedKeys = props.selectedRowKeys || [];
            if (selected) {
              props.setSelectedRowKeys([...currentSelectedKeys, record.index]);
            } else {
              props.setSelectedRowKeys(
                currentSelectedKeys.filter((key) => key !== record.index)
              );
            }
          },
          onSelectAll: (selected) => {
            const pageRowKeys = data.map((item) => item.index);
            const currentSelectedKeys = props.selectedRowKeys || [];
            if (selected) {
              const newSelectedKeys = [
                ...new Set([...currentSelectedKeys, ...pageRowKeys]),
              ];
              props.setSelectedRowKeys(newSelectedKeys);
            } else {
              const pageRowKeysSet = new Set(pageRowKeys);
              const newSelectedKeys = currentSelectedKeys.filter(
                (key) => !pageRowKeysSet.has(key.toString())
              );
              props.setSelectedRowKeys(newSelectedKeys);
            }
          },
        }}
        renderPagination={(paginationNode) => (
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginTop: 10,
            }}
          >
            {paginationNode}
          </div>
        )}
        loading={loading}
        onChange={onChangeTable}
        pagination={pagination}
        columns={columns}
        data={data}
        style={{ marginLeft: 10, marginBottom: 40 }}
        tableLayoutFixed={true}
        scroll={
          props.tableScroll || {
            x: 2000,
          }
        }
      />
    </div>
  );
}

export default CaseTable;
