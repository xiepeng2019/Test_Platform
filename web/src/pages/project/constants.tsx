import React from 'react';
import { Button, Space } from '@arco-design/web-react';
import UserColumnRender from '@/components/UserColumn';
import dayjs from 'dayjs';
import { UserSearch } from '@/client';
import { Project } from '@/client';

export function getColumns(t, callback: (record: Project, type: string) => void) {
  return [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
      fixed: 'left' as const,
    },
    {
      title: t['project.columns.name'],
      dataIndex: 'name',
      width: 120,
    },
    {
      title: t['project.columns.gitRepository'],
      dataIndex: 'git_repo',
      width: 400,
    },
    {
      title: t['project.columns.branch'],
      dataIndex: 'branch',
      width: 150,
    },
    {
      title: t['project.columns.owner'],
      dataIndex: 'owners',
      render: (record: UserSearch[]) => UserColumnRender(record),
    },
    {
      title: t['project.columns.qa'],
      dataIndex: 'qas',
      render: (record: UserSearch[]) => UserColumnRender(record),
    },
    {
      title: t['project.columns.dev'],
      dataIndex: 'devs',
      render: (record: UserSearch[]) => UserColumnRender(record),
    },
    {
      title: t['project.columns.createdTime'],
      dataIndex: 'created_at',
      width: 200,
      render: (record: string) => dayjs(record).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: t['project.columns.updatedTime'],
      dataIndex: 'updated_at',
      width: 200,
      render: (record: string) => dayjs(record).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: t['project.columns.operations'],
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
            {t['project.columns.operations.detail']}
          </Button>
          <Button
            status="warning"
            size="mini"
            onClick={() => callback(record, 'edit')}
          >
            {t['project.columns.operations.edit']}
          </Button>
          <Button
            status="danger"
            size="mini"
            onClick={() => callback(record, 'delete')}
          >
            {t['project.columns.operations.delete']}
          </Button>
        </Space>
      ),
    },
  ];
}
