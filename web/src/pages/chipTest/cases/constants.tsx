import React from 'react';
import { Button, Space, Tag } from '@arco-design/web-react';
import { TestCase } from '@/client';
import dayjs from 'dayjs';

export const TAG_YES = (
  <Tag checkable color="blue" defaultChecked>
    YES
  </Tag>
);

export const TAG_NO = (
  <Tag checkable color="gray" defaultChecked>
    NO
  </Tag>
);

export const getPriorityTag = (value: string) => {
  const color = value === 'P0' ? 'red' : value === 'P1' ? 'orange' : 'green';
  return <Tag color={color}>{value}</Tag>;
};

export function getColumns(
  t: {
    [x: string]:
      | boolean
      | React.ReactChild
      | React.ReactFragment
      | React.ReactPortal;
  },
  callback: {
    (record: TestCase, type: string): Promise<void>;
  }
) {
  return [
    {
      title: t['case.columns.index'],
      dataIndex: 'index',
      width: 220,
      ellipsis: true,
      fixed: 'left' as const,
    },
    {
      title: t['case.columns.name'],
      dataIndex: 'name',
      width: 200,
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
    {
      title: t['case.columns.createdTime'],
      dataIndex: 'created_at',
      render: (record) => dayjs(record).format('YYYY-MM-DD HH:mm:ss'),
      width: 180,
    },
    {
      title: t['case.columns.updatedTime'],
      dataIndex: 'updated_at',
      render: (record) => dayjs(record).format('YYYY-MM-DD HH:mm:ss'),
      width: 180,
    },
    {
      title: 'ID',
      dataIndex: 'id',
    },
    {
      title: '节点ID',
      dataIndex: 'node_id',
      width: 80,
    },
    {
      title: t['case.columns.operations'],
      dataIndex: 'operations',
      fixed: 'right' as const,
      width: 190,
      render: (_, record) => (
        <Space size="small">
          <Button
            status="success"
            size="mini"
            onClick={() => callback(record, 'detail')}
          >
            {t['case.columns.operations.detail']}
          </Button>
          <Button
            status="warning"
            size="mini"
            onClick={() => callback(record, 'edit')}
          >
            {t['case.columns.operations.edit']}
          </Button>
          <Button
            status="danger"
            size="mini"
            onClick={() => callback(record, 'delete')}
          >
            {t['case.columns.operations.delete']}
          </Button>
        </Space>
      ),
    },
  ];
}
