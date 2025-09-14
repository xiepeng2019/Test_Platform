import React from 'react';
import {
  Button,
  Descriptions,
  Popconfirm,
  Popover,
  Space,
  Tag,
} from '@arco-design/web-react';
import dayjs from 'dayjs';
import UserColumnRender from '@/components/UserColumn';
import { ColumnProps } from '@arco-design/web-react/es/Table';
import { TaskConfig, ServerInTask, TestTaskListItem } from '@/client';
import { getTaskStatusLabel } from '@/utils/Tags';
import { IconSettings } from '@arco-design/web-react/icon';
import { CrudActionType } from '../types';
import useLocale from '@/utils/useLocale';

const serverConfigTrigger = (config: ServerInTask) => {
  if (!config) {
    return null;
  }

  const data = Object.entries(config)
    .filter(([key]) => !['name'].includes(key))
    .map(([key, value]) => ({
      label: key,
      value,
    }));

  return (
    <Popover
      title={config.name}
      content={<Descriptions size="mini" column={1} data={data} />}
    >
      <Tag color="gray" icon={<IconSettings />}>
        {config.name}
      </Tag>
    </Popover>
  );
};

const taskConfigTrigger = (config: TaskConfig) => {
  if (!config) {
    return null;
  }

  const data = config.env_vars
    .map((item) => ({
      label: item.name,
      value: item.value,
    }));

  return (
    config && (
      <Popover
        title={config.name}
        content={<Descriptions size="mini" column={1} data={data} />}
      >
        <Tag color="gray" icon={<IconSettings />}>
          {config.name}
        </Tag>
      </Popover>
    )
  );
};

export function getBaseColumns(
  t: ReturnType<typeof useLocale>,
  callback: (record: TestTaskListItem, action: CrudActionType) => void
): ColumnProps<TestTaskListItem>[] {
  return [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
      fixed: 'left' as const,
    },
    {
      title: t['task.columns.name'],
      dataIndex: 'name',
      width: 220,
      fixed: 'left' as const,
    },
    {
      title: t['task.columns.owner'],
      dataIndex: 'owner',
      render: (record) => UserColumnRender([record]),
    },
    {
      title: t['task.columns.status'],
      dataIndex: 'status',
      render: (status) => getTaskStatusLabel(status),
    },
    {
      title: t['task.columns.server'],
      dataIndex: 'server',
      width: 120,
      render: (server) => {
        return serverConfigTrigger(server);
      },
    },
    {
      title: t['task.columns.config'],
      dataIndex: 'config',
      width: 120,
      render: (config) => {
        return taskConfigTrigger(config);
      },
    },
    {
      title: t['task.columns.failed_continue'],
      dataIndex: 'failed_continue',
      width: 120,
    },
    {
      title: t['task.columns.lark_notice'],
      dataIndex: 'lark_notice',
    },
    {
      title: t['task.columns.lark_subscribe'],
      dataIndex: 'lark_subscribe',
    },
    {
      title: t['columns.createdTime'],
      dataIndex: 'created_at',
      width: 220,
      render: (value: string) => {
        return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-';
      },
    },
    {
      title: t['columns.updatedTime'],
      dataIndex: 'updated_at',
      width: 220,
      render: (value: string) => {
        return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-';
      },
    },
    {
      title: t['columns.operations'],
      dataIndex: 'operations',
      fixed: 'right' as const,
      width: 300,
      render: (_, record: TestTaskListItem) => (
        <Space size="small">
          <Popconfirm
            focusLock
            title="确认运行任务?"
            content="目前暂不支持变更任务配置"
            onOk={() => callback(record, CrudActionType.RUN)}
          >
            <Button size="mini" status="default" type="primary">
              {t['columns.operations.run']}
            </Button>
          </Popconfirm>
          <Button
            size="mini"
            onClick={() => callback(record, CrudActionType.LOG)}
          >
            {t['columns.operations.log']}
          </Button>
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
    },
  ];
}
